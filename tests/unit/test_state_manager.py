"""
T011: Test StateManager for managing application state and caching.
This test will fail initially until the StateManager is implemented.
"""
from t2d_kit.core.state_manager import StateManager
from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.models.user_recipe import UserRecipe


class TestStateManager:
    """Test cases for StateManager functionality."""

    def test_state_manager_initialization(self):
        """Test that StateManager can be initialized."""
        state_manager = StateManager()
        assert state_manager is not None
        assert hasattr(state_manager, 'cache')
        assert hasattr(state_manager, 'get_user_recipe')
        assert hasattr(state_manager, 'set_user_recipe')

    def test_state_manager_singleton_pattern(self):
        """Test that StateManager follows singleton pattern."""
        manager1 = StateManager()
        manager2 = StateManager()
        assert manager1 is manager2

    def test_cache_user_recipe(self):
        """Test caching and retrieving user recipes."""
        recipe_data = {
            "name": "Cached Recipe",
            "description": "For caching test",
            "components": ["cache_comp"],
            "connections": []
        }
        recipe = UserRecipe(**recipe_data)
        recipe_id = "cache_test_123"

        state_manager = StateManager()
        state_manager.set_user_recipe(recipe_id, recipe)

        retrieved_recipe = state_manager.get_user_recipe(recipe_id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.name == "Cached Recipe"
        assert retrieved_recipe.description == "For caching test"

    def test_cache_miss_user_recipe(self):
        """Test cache miss for non-existent user recipe."""
        state_manager = StateManager()
        result = state_manager.get_user_recipe("nonexistent_id")
        assert result is None

    def test_cache_processed_recipe(self):
        """Test caching and retrieving processed recipes."""
        user_recipe_data = {
            "name": "For Processing",
            "description": "To be processed",
            "components": ["proc_comp"],
            "connections": []
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [{"id": "proc_comp", "label": "Process Component", "shape": "rectangle"}],
            "edges": [],
            "layout": "grid"
        }

        processed_recipe = ProcessedRecipe(
            user_recipe=user_recipe,
            processed_data=processed_data
        )

        state_manager = StateManager()
        state_manager.set_processed_recipe("proc_123", processed_recipe)

        retrieved = state_manager.get_processed_recipe("proc_123")
        assert retrieved is not None
        assert retrieved.user_recipe.name == "For Processing"
        assert retrieved.processed_data["layout"] == "grid"

    def test_cache_invalidation(self):
        """Test cache invalidation functionality."""
        recipe_data = {
            "name": "To Invalidate",
            "description": "Will be invalidated",
            "components": ["invalid_comp"],
            "connections": []
        }
        recipe = UserRecipe(**recipe_data)

        state_manager = StateManager()
        state_manager.set_user_recipe("invalid_123", recipe)

        # Verify it's cached
        assert state_manager.get_user_recipe("invalid_123") is not None

        # Invalidate and verify it's gone
        state_manager.invalidate_user_recipe("invalid_123")
        assert state_manager.get_user_recipe("invalid_123") is None

    def test_cache_size_limit(self):
        """Test that cache respects size limits."""
        state_manager = StateManager(max_cache_size=2)

        # Add recipes up to the limit
        for i in range(3):
            recipe_data = {
                "name": f"Recipe {i}",
                "description": f"Recipe number {i}",
                "components": [f"comp{i}"],
                "connections": []
            }
            recipe = UserRecipe(**recipe_data)
            state_manager.set_user_recipe(f"recipe_{i}", recipe)

        # First recipe should be evicted due to size limit
        assert state_manager.get_user_recipe("recipe_0") is None
        assert state_manager.get_user_recipe("recipe_1") is not None
        assert state_manager.get_user_recipe("recipe_2") is not None

    def test_cache_ttl_expiration(self):
        """Test cache TTL (time-to-live) expiration."""
        recipe_data = {
            "name": "TTL Recipe",
            "description": "Will expire",
            "components": ["ttl_comp"],
            "connections": []
        }
        recipe = UserRecipe(**recipe_data)

        state_manager = StateManager(default_ttl=0.1)  # 100ms TTL
        state_manager.set_user_recipe("ttl_123", recipe)

        # Should be available immediately
        assert state_manager.get_user_recipe("ttl_123") is not None

        # Should be expired after TTL
        import time
        time.sleep(0.15)
        assert state_manager.get_user_recipe("ttl_123") is None

    def test_clear_all_cache(self):
        """Test clearing entire cache."""
        state_manager = StateManager()

        # Add multiple items
        for i in range(3):
            recipe_data = {
                "name": f"Clear Recipe {i}",
                "description": f"To be cleared {i}",
                "components": [f"clear_comp{i}"],
                "connections": []
            }
            recipe = UserRecipe(**recipe_data)
            state_manager.set_user_recipe(f"clear_{i}", recipe)

        # Verify they're cached
        assert state_manager.get_user_recipe("clear_0") is not None
        assert state_manager.get_user_recipe("clear_1") is not None
        assert state_manager.get_user_recipe("clear_2") is not None

        # Clear cache
        state_manager.clear_cache()

        # Verify they're all gone
        assert state_manager.get_user_recipe("clear_0") is None
        assert state_manager.get_user_recipe("clear_1") is None
        assert state_manager.get_user_recipe("clear_2") is None

    def test_cache_statistics(self):
        """Test cache statistics and metrics."""
        state_manager = StateManager()

        # Add some items
        recipe_data = {
            "name": "Stats Recipe",
            "description": "For statistics",
            "components": ["stats_comp"],
            "connections": []
        }
        recipe = UserRecipe(**recipe_data)
        state_manager.set_user_recipe("stats_123", recipe)

        # Access item (hit)
        state_manager.get_user_recipe("stats_123")

        # Access non-existent item (miss)
        state_manager.get_user_recipe("nonexistent")

        stats = state_manager.get_cache_stats()
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert stats["total_items"] >= 1
