"""MCP tools for managing user recipes."""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastmcp import FastMCP

from t2d_kit.models.user_recipe import (
    CreateRecipeParams,
    CreateRecipeResponse,
    DeleteRecipeParams,
    DeleteRecipeResponse,
    DiagramRequest,
    EditRecipeParams,
    EditRecipeResponse,
    MCPValidationError,
    MCPValidationResult,
    PRDContent,
    UserInstructions,
    UserRecipe,
    ValidateRecipeParams,
)

DEFAULT_RECIPE_DIR = Path("./recipes")


def _validate_recipe_content(content: dict, start_time: float) -> MCPValidationResult:
    """Internal helper to validate recipe content."""
    errors = []
    warnings = []

    # Validate with Pydantic
    try:
        recipe = UserRecipe.model_validate(content)

        # Additional validation checks
        if recipe.instructions.diagrams:
            if len(recipe.instructions.diagrams) > 20:
                warnings.append("Recipe has more than 20 diagrams, consider splitting")

        # Check PRD size if embedded
        if recipe.prd.content:
            size_bytes = len(recipe.prd.content.encode('utf-8'))
            if size_bytes > 1048576:  # 1MB
                errors.append(MCPValidationError(
                    field="prd.content",
                    message=f"PRD content exceeds 1MB limit: {size_bytes} bytes",
                    error_type="size_limit",
                    suggestion="Use file_path instead of embedding large PRDs"
                ))
            elif size_bytes > 524288:  # 512KB warning
                warnings.append(f"PRD content is large ({size_bytes} bytes), consider using file_path")

        duration_ms = (time.time() - start_time) * 1000

        return MCPValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            duration_ms=duration_ms
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return MCPValidationResult(
            valid=False,
            errors=[MCPValidationError(
                field="recipe",
                message=str(e),
                error_type="validation",
                suggestion="Check recipe structure and required fields"
            )],
            warnings=warnings,
            duration_ms=duration_ms
        )


async def register_user_recipe_tools(server: FastMCP, recipe_dir: Path | None = None) -> None:
    """Register user recipe tools with the MCP server.

    Args:
        server: FastMCP server instance
        recipe_dir: Directory for recipe files (defaults to ./recipes)
    """
    if recipe_dir is None:
        recipe_dir = DEFAULT_RECIPE_DIR

    # Ensure directory exists
    recipe_dir.mkdir(parents=True, exist_ok=True)

    @server.tool()
    async def create_user_recipe(params: CreateRecipeParams) -> CreateRecipeResponse:
        """Create a new user recipe file.

        Creates a new recipe YAML file with the provided PRD content and diagram specifications.
        Validates the recipe before saving and returns validation results.

        Args:
            params: Recipe creation parameters including name, PRD, and diagrams

        Returns:
            CreateRecipeResponse with success status and validation results
        """
        start_time = time.time()

        # Create output directory if specified
        output_dir = Path(params.output_dir) if params.output_dir else recipe_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Construct recipe path
        recipe_path = output_dir / f"{params.name}.yaml"

        # Check if file already exists
        if recipe_path.exists():
            return CreateRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                validation_result=MCPValidationResult(
                    valid=False,
                    errors=[MCPValidationError(
                        field="name",
                        message=f"Recipe file already exists: {recipe_path}",
                        error_type="duplicate",
                        suggestion="Choose a different name or delete the existing recipe"
                    )],
                    warnings=[],
                    duration_ms=(time.time() - start_time) * 1000
                ),
                message=f"Recipe {params.name} already exists"
            )

        try:
            # Build PRD content
            prd = PRDContent(
                content=params.prd_content if params.prd_content else None,
                file_path=params.prd_file_path if params.prd_file_path else None,
                format="markdown"
            )

            # Build instructions
            instructions = UserInstructions(
                diagrams=params.diagrams,
                documentation=params.documentation_config
            )

            # Create recipe model
            recipe = UserRecipe(
                name=params.name,
                version="1.0.0",
                prd=prd,
                instructions=instructions
            )

            # Validate
            validation_errors = []
            validation_warnings = []

        except Exception as e:
            # Validation failed
            duration_ms = (time.time() - start_time) * 1000
            return CreateRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                validation_result=MCPValidationResult(
                    valid=False,
                    errors=[MCPValidationError(
                        field="recipe",
                        message=str(e),
                        error_type="validation",
                        suggestion="Check the recipe structure and field values"
                    )],
                    warnings=[],
                    duration_ms=duration_ms
                ),
                message=f"Recipe validation failed: {str(e)}"
            )

        # Save to file
        try:
            with open(recipe_path, "w") as f:
                yaml.dump(
                    recipe.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )

            duration_ms = (time.time() - start_time) * 1000

            return CreateRecipeResponse(
                success=True,
                recipe_name=params.name,
                file_path=str(recipe_path),
                validation_result=MCPValidationResult(
                    valid=True,
                    errors=validation_errors,
                    warnings=validation_warnings,
                    duration_ms=duration_ms
                ),
                message=f"Recipe {params.name} created successfully"
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CreateRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                validation_result=MCPValidationResult(
                    valid=False,
                    errors=[MCPValidationError(
                        field="file",
                        message=f"Failed to write recipe file: {str(e)}",
                        error_type="io_error",
                        suggestion="Check file permissions and disk space"
                    )],
                    warnings=[],
                    duration_ms=duration_ms
                ),
                message=f"Failed to save recipe: {str(e)}"
            )

    @server.tool()
    async def validate_user_recipe(params: ValidateRecipeParams) -> MCPValidationResult:
        """Validate a user recipe file or content.

        Performs comprehensive validation of recipe structure and content,
        checking all required fields and constraints.

        Args:
            params: Either a recipe name to load from disk or recipe content to validate

        Returns:
            MCPValidationResult with validation status and any errors/warnings
        """
        start_time = time.time()
        errors = []
        warnings = []

        # Load recipe content
        if params.name:
            recipe_path = recipe_dir / f"{params.name}.yaml"
            if not recipe_path.exists():
                duration_ms = (time.time() - start_time) * 1000
                return MCPValidationResult(
                    valid=False,
                    errors=[MCPValidationError(
                        field="name",
                        message=f"Recipe not found: {params.name}",
                        error_type="not_found",
                        suggestion="Check the recipe name and directory"
                    )],
                    warnings=[],
                    duration_ms=duration_ms
                )

            try:
                with open(recipe_path) as f:
                    content = yaml.safe_load(f)
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return MCPValidationResult(
                    valid=False,
                    errors=[MCPValidationError(
                        field="file",
                        message=f"Failed to read recipe: {str(e)}",
                        error_type="io_error",
                        suggestion="Check file format and permissions"
                    )],
                    warnings=[],
                    duration_ms=duration_ms
                )
        else:
            content = params.content.model_dump() if params.content else {}

        # Use helper function
        return _validate_recipe_content(content, start_time)

    @server.tool()
    async def edit_user_recipe(params: EditRecipeParams) -> EditRecipeResponse:
        """Edit an existing user recipe.

        Updates specified fields in an existing recipe file.
        Optionally validates the changes before saving.

        Args:
            params: Edit parameters including recipe name and fields to update

        Returns:
            EditRecipeResponse with success status and changes applied
        """
        recipe_path = recipe_dir / f"{params.name}.yaml"

        if not recipe_path.exists():
            return EditRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                changes_applied={},
                message=f"Recipe not found: {params.name}"
            )

        # Load existing recipe
        try:
            with open(recipe_path) as f:
                content = yaml.safe_load(f)
            recipe = UserRecipe.model_validate(content)
        except Exception as e:
            return EditRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                changes_applied={},
                message=f"Failed to load recipe: {str(e)}"
            )

        # Apply changes
        changes_applied = {}

        if params.prd_content is not None:
            recipe.prd.content = params.prd_content
            recipe.prd.file_path = None
            changes_applied["prd.content"] = "updated"

        if params.prd_file_path is not None:
            recipe.prd.file_path = params.prd_file_path
            recipe.prd.content = None
            changes_applied["prd.file_path"] = params.prd_file_path

        if params.diagrams is not None:
            recipe.instructions.diagrams = params.diagrams
            changes_applied["diagrams"] = f"{len(params.diagrams)} diagrams"

        if params.documentation_config is not None:
            recipe.instructions.documentation = params.documentation_config
            changes_applied["documentation"] = "updated"

        # Validate if requested
        validation_result = None
        if params.validate_before_save:
            # Use helper function for validation
            validation_result = _validate_recipe_content(
                recipe.model_dump(exclude_none=True),
                time.time()
            )
            if not validation_result.valid:
                return EditRecipeResponse(
                    success=False,
                    recipe_name=params.name,
                    file_path=str(recipe_path),
                    changes_applied=changes_applied,
                    validation_result=validation_result,
                    message="Validation failed, changes not saved"
                )

        # Save updated recipe
        try:
            with open(recipe_path, "w") as f:
                yaml.dump(
                    recipe.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )

            return EditRecipeResponse(
                success=True,
                recipe_name=params.name,
                file_path=str(recipe_path),
                changes_applied=changes_applied,
                validation_result=validation_result,
                message=f"Recipe {params.name} updated successfully"
            )

        except Exception as e:
            return EditRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                changes_applied={},
                message=f"Failed to save changes: {str(e)}"
            )

    @server.tool()
    async def delete_user_recipe(params: DeleteRecipeParams) -> DeleteRecipeResponse:
        """Delete a user recipe file.

        Permanently removes a recipe file from the filesystem.
        Requires confirmation flag to prevent accidental deletion.

        Args:
            params: Recipe name and confirmation flag

        Returns:
            DeleteRecipeResponse with success status
        """
        if not params.confirm:
            return DeleteRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path="",
                message="Deletion not confirmed (set confirm=true to delete)"
            )

        recipe_path = recipe_dir / f"{params.name}.yaml"

        if not recipe_path.exists():
            return DeleteRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                message=f"Recipe not found: {params.name}"
            )

        try:
            os.remove(recipe_path)
            return DeleteRecipeResponse(
                success=True,
                recipe_name=params.name,
                file_path=str(recipe_path),
                message=f"Recipe {params.name} deleted successfully"
            )
        except Exception as e:
            return DeleteRecipeResponse(
                success=False,
                recipe_name=params.name,
                file_path=str(recipe_path),
                message=f"Failed to delete recipe: {str(e)}"
            )
