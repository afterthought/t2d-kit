"""
Performance tests for T2D Kit processing capabilities.

Tests recipe validation, state management, large recipe handling, and parallel processing.
Includes benchmarks for critical performance requirements:
- Recipe validation must complete under 200ms
- State management operations should be efficient
- Large recipes (10+ diagrams) should process without significant degradation
- Parallel processing should show efficiency gains

Prerequisites:
- Install pytest-benchmark for detailed benchmarking: pip install pytest-benchmark
- Run with: pytest tests/performance/test_processing.py --benchmark-only
- For comparison: pytest tests/performance/test_processing.py --benchmark-compare
"""

import asyncio
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from typing import Any

import pytest

# Import project modules
from t2d_kit.models.user_recipe import (
    UserRecipe,
)

# Try to import pytest-benchmark, fall back to timing if not available
try:
    import pytest_benchmark
    HAS_BENCHMARK = True
except ImportError:
    HAS_BENCHMARK = False
    pytest_benchmark = None


class PerformanceTimer:
    """Simple timer for when pytest-benchmark is not available."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


class TestRecipeValidationPerformance:
    """Test recipe validation performance requirements."""

    def _create_simple_recipe(self, name: str = "Test Recipe") -> dict[str, Any]:
        """Create a simple valid recipe data structure."""
        return {
            "name": name,
            "version": "1.0.0",
            "prd": {
                "content": "# Simple PRD\n\nBasic requirements for testing.",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "system_architecture",
                        "description": "High-level system overview",
                        "framework_preference": "d2"
                    }
                ],
                "documentation": {
                    "style": "technical",
                    "detail_level": "detailed",
                    "include_code_examples": True
                }
            }
        }

    def _create_complex_recipe(self, num_diagrams: int = 10) -> dict[str, Any]:
        """Create a complex recipe with multiple diagrams."""
        diagrams = []
        for i in range(num_diagrams):
            diagrams.append({
                "type": f"diagram_type_{i}",
                "description": f"Complex diagram {i} with detailed requirements",
                "framework_preference": "d2" if i % 2 == 0 else "mermaid"
            })

        return {
            "name": f"Complex Recipe {num_diagrams} Diagrams",
            "version": "1.0.0",
            "prd": {
                "content": "# Complex PRD\n\n" + "\n".join([
                    f"## Section {i}\n\nDetailed requirements for section {i}."
                    for i in range(20)
                ]),
                "format": "markdown"
            },
            "instructions": {
                "diagrams": diagrams,
                "documentation": {
                    "style": "technical",
                    "detail_level": "detailed",
                    "sections": [f"section_{i}" for i in range(10)],
                    "include_code_examples": True,
                    "include_diagrams_inline": True
                },
                "presentation": {
                    "audience": "Technical team",
                    "max_slides": 50,
                    "style": "technical",
                    "include_speaker_notes": True,
                    "time_limit": 30
                },
                "focus_areas": [f"focus_area_{i}" for i in range(5)]
            },
            "preferences": {
                "default_framework": "d2",
                "diagram_style": "clean",
                "color_scheme": "modern",
                "theme": "professional"
            }
        }

    def test_simple_recipe_validation_performance(self, benchmark=None):
        """Test that simple recipe validation completes under 200ms."""
        recipe_data = self._create_simple_recipe()

        def validate_recipe():
            return UserRecipe(**recipe_data)

        if HAS_BENCHMARK and benchmark:
            # Use pytest-benchmark if available
            result = benchmark(validate_recipe)
            assert result.name == "Test Recipe"
            # pytest-benchmark will automatically track timing
        else:
            # Manual timing measurement
            with PerformanceTimer() as timer:
                result = validate_recipe()

            assert result.name == "Test Recipe"
            assert timer.elapsed < 0.2, f"Recipe validation took {timer.elapsed:.3f}s, must be under 0.2s"

    def test_complex_recipe_validation_performance(self, benchmark=None):
        """Test complex recipe validation with 10+ diagrams."""
        recipe_data = self._create_complex_recipe(12)

        def validate_complex_recipe():
            return UserRecipe(**recipe_data)

        if HAS_BENCHMARK and benchmark:
            result = benchmark(validate_complex_recipe)
            assert len(result.instructions.diagrams) == 12
        else:
            with PerformanceTimer() as timer:
                result = validate_complex_recipe()

            assert len(result.instructions.diagrams) == 12
            # Complex recipes should still validate reasonably quickly
            assert timer.elapsed < 1.0, f"Complex recipe validation took {timer.elapsed:.3f}s, should be under 1.0s"

    def test_recipe_validation_scaling(self):
        """Test how validation performance scales with recipe complexity."""
        diagram_counts = [1, 5, 10, 20, 50]
        times = []

        for count in diagram_counts:
            recipe_data = self._create_complex_recipe(count)

            with PerformanceTimer() as timer:
                UserRecipe(**recipe_data)

            times.append(timer.elapsed)
            print(f"Diagrams: {count:2d}, Time: {timer.elapsed:.3f}s")

        # Validation time should not grow exponentially
        # Allow for some growth but ensure it's reasonable
        for i in range(1, len(times)):
            growth_factor = times[i] / times[i-1]
            assert growth_factor < 5.0, f"Validation time grew by {growth_factor:.1f}x from {diagram_counts[i-1]} to {diagram_counts[i]} diagrams"

    def test_batch_recipe_validation_performance(self, benchmark=None):
        """Test validating multiple recipes in batch."""
        recipes_data = [self._create_simple_recipe(f"Recipe {i}") for i in range(10)]

        def validate_batch():
            return [UserRecipe(**data) for data in recipes_data]

        if HAS_BENCHMARK and benchmark:
            results = benchmark(validate_batch)
            assert len(results) == 10
        else:
            with PerformanceTimer() as timer:
                results = validate_batch()

            assert len(results) == 10
            avg_time = timer.elapsed / 10
            assert avg_time < 0.05, f"Average recipe validation took {avg_time:.3f}s, should be under 0.05s"


class MockStateManager:
    """Mock state manager for testing performance."""

    def __init__(self, max_cache_size: int = 1000, default_ttl: float = 3600):
        self.cache: dict[str, Any] = {}
        self.access_times: dict[str, float] = {}
        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Any:
        """Get item from cache."""
        with self._lock:
            current_time = time.time()

            if key in self.cache:
                # Check TTL
                if current_time - self.access_times[key] < self.default_ttl:
                    self.hits += 1
                    self.access_times[key] = current_time
                    return self.cache[key]
                else:
                    # Expired
                    del self.cache[key]
                    del self.access_times[key]

            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        with self._lock:
            current_time = time.time()

            # Implement LRU eviction if at capacity
            if len(self.cache) >= self.max_cache_size and key not in self.cache:
                # Remove oldest item
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = value
            self.access_times[key] = current_time

    def clear(self) -> None:
        """Clear all cache."""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_items": len(self.cache)
            }


class TestStateManagerPerformance:
    """Test state management performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = MockStateManager()
        self.sample_recipe = UserRecipe(**{
            "name": "Performance Test Recipe",
            "version": "1.0.0",
            "prd": {"content": "Test content", "format": "markdown"},
            "instructions": {
                "diagrams": [{"type": "test_diagram", "description": "Test"}]
            }
        })

    def test_cache_get_performance(self, benchmark=None):
        """Test cache retrieval performance."""
        # Pre-populate cache
        for i in range(100):
            self.state_manager.set(f"key_{i}", f"value_{i}")

        def get_cached_item():
            return self.state_manager.get("key_50")

        if HAS_BENCHMARK and benchmark:
            result = benchmark(get_cached_item)
            assert result == "value_50"
        else:
            with PerformanceTimer() as timer:
                for _ in range(1000):
                    result = get_cached_item()

            assert result == "value_50"
            avg_time = timer.elapsed / 1000
            assert avg_time < 0.0001, f"Average cache get took {avg_time:.6f}s, should be under 0.0001s"

    def test_cache_set_performance(self, benchmark=None):
        """Test cache storage performance."""
        def set_cache_item():
            self.state_manager.set("perf_test", self.sample_recipe)

        if HAS_BENCHMARK and benchmark:
            benchmark(set_cache_item)
        else:
            with PerformanceTimer() as timer:
                for i in range(1000):
                    self.state_manager.set(f"perf_test_{i}", self.sample_recipe)

            avg_time = timer.elapsed / 1000
            assert avg_time < 0.001, f"Average cache set took {avg_time:.6f}s, should be under 0.001s"

    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access."""
        num_threads = 10
        operations_per_thread = 100

        def worker_thread(thread_id: int):
            """Worker function for concurrent testing."""
            for i in range(operations_per_thread):
                key = f"thread_{thread_id}_item_{i}"
                value = f"data_{thread_id}_{i}"

                # Set and then get
                self.state_manager.set(key, value)
                retrieved = self.state_manager.get(key)
                assert retrieved == value

        with PerformanceTimer() as timer:
            threads = []
            for tid in range(num_threads):
                thread = threading.Thread(target=worker_thread, args=(tid,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        total_operations = num_threads * operations_per_thread * 2  # set + get
        ops_per_second = total_operations / timer.elapsed

        print(f"Concurrent performance: {ops_per_second:.0f} ops/sec")
        assert ops_per_second > 10000, f"Concurrent cache performance: {ops_per_second:.0f} ops/sec, should be > 10000"

    def test_cache_memory_efficiency(self):
        """Test cache memory usage and eviction."""
        cache_size = 100
        state_manager = MockStateManager(max_cache_size=cache_size)

        # Fill cache to capacity
        for i in range(cache_size):
            state_manager.set(f"key_{i}", f"value_{i}")

        stats = state_manager.get_stats()
        assert stats["total_items"] == cache_size

        # Add more items to trigger eviction
        for i in range(cache_size, cache_size + 20):
            state_manager.set(f"key_{i}", f"value_{i}")

        stats = state_manager.get_stats()
        assert stats["total_items"] <= cache_size, "Cache should respect size limits"

        # Verify LRU behavior - oldest items should be evicted
        assert state_manager.get("key_0") is None, "Oldest item should be evicted"
        assert state_manager.get(f"key_{cache_size + 19}") is not None, "Newest item should be present"


class TestLargeRecipeHandling:
    """Test handling of large recipes with 10+ diagrams."""

    def test_large_recipe_creation_performance(self, benchmark=None):
        """Test creating recipes with many diagrams."""
        def create_large_recipe():
            diagrams = []
            for i in range(15):
                diagrams.append({
                    "type": f"large_diagram_{i}",
                    "description": f"Large diagram {i} with extensive requirements and detailed specifications",
                    "framework_preference": "d2" if i % 3 == 0 else "mermaid" if i % 3 == 1 else "plantuml"
                })

            return UserRecipe(
                name="Large Recipe Test",
                version="1.0.0",
                prd={
                    "content": "# Large Recipe\n\n" + "\n".join([
                        f"## Requirement {i}\n\nDetailed requirement {i} with multiple paragraphs of content."
                        for i in range(50)
                    ]),
                    "format": "markdown"
                },
                instructions={
                    "diagrams": diagrams,
                    "documentation": {
                        "style": "technical",
                        "sections": [f"section_{i}" for i in range(20)],
                        "detail_level": "detailed"
                    }
                }
            )

        if HAS_BENCHMARK and benchmark:
            recipe = benchmark(create_large_recipe)
            assert len(recipe.instructions.diagrams) == 15
        else:
            with PerformanceTimer() as timer:
                recipe = create_large_recipe()

            assert len(recipe.instructions.diagrams) == 15
            assert timer.elapsed < 0.5, f"Large recipe creation took {timer.elapsed:.3f}s, should be under 0.5s"

    def test_large_recipe_serialization_performance(self):
        """Test serialization/deserialization of large recipes."""
        # Create a large recipe
        large_recipe_data = {
            "name": "Serialization Test",
            "version": "1.0.0",
            "prd": {
                "content": "# Large Content\n\n" + "Large content section. " * 1000,
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": f"serial_diagram_{i}",
                        "description": f"Serialization test diagram {i}",
                        "framework_preference": "d2"
                    }
                    for i in range(25)
                ]
            }
        }

        recipe = UserRecipe(**large_recipe_data)

        # Test serialization
        with PerformanceTimer() as timer:
            serialized = recipe.model_dump()

        serialization_time = timer.elapsed
        assert serialization_time < 0.1, f"Serialization took {serialization_time:.3f}s, should be under 0.1s"

        # Test deserialization
        with PerformanceTimer() as timer:
            deserialized = UserRecipe(**serialized)

        deserialization_time = timer.elapsed
        assert deserialization_time < 0.1, f"Deserialization took {deserialization_time:.3f}s, should be under 0.1s"

        assert deserialized.name == recipe.name
        assert len(deserialized.instructions.diagrams) == len(recipe.instructions.diagrams)

    def test_memory_usage_large_recipes(self):
        """Test memory efficiency with large recipes."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create multiple large recipes
        recipes = []
        for batch in range(5):
            batch_recipes = []
            for i in range(10):
                recipe_data = {
                    "name": f"Memory Test Recipe {batch}_{i}",
                    "version": "1.0.0",
                    "prd": {
                        "content": f"# Recipe {batch}_{i}\n\n" + "Content section. " * 500,
                        "format": "markdown"
                    },
                    "instructions": {
                        "diagrams": [
                            {
                                "type": f"memory_diagram_{j}",
                                "description": f"Memory test diagram {j}",
                                "framework_preference": "d2"
                            }
                            for j in range(20)
                        ]
                    }
                }
                batch_recipes.append(UserRecipe(**recipe_data))
            recipes.extend(batch_recipes)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"Memory usage increased by {memory_increase:.1f}MB for {len(recipes)} large recipes")

        # Memory increase should be reasonable (less than 500MB for this test)
        assert memory_increase < 500, f"Memory usage increased by {memory_increase:.1f}MB, should be under 500MB"


class TestParallelProcessingEfficiency:
    """Test parallel processing performance and efficiency."""

    def _cpu_intensive_validation(self, recipe_data: dict[str, Any]) -> UserRecipe:
        """Simulate CPU-intensive validation work."""
        # Add some CPU work to simulate complex validation
        total = 0
        for i in range(10000):
            total += i * i

        return UserRecipe(**recipe_data)

    def _create_test_recipes(self, count: int) -> list[dict[str, Any]]:
        """Create test recipe data."""
        recipes = []
        for i in range(count):
            recipes.append({
                "name": f"Parallel Test Recipe {i}",
                "version": "1.0.0",
                "prd": {
                    "content": f"# Recipe {i}\n\nContent for recipe {i}.",
                    "format": "markdown"
                },
                "instructions": {
                    "diagrams": [
                        {
                            "type": f"parallel_diagram_{j}",
                            "description": f"Parallel diagram {j}",
                            "framework_preference": "d2"
                        }
                        for j in range(5)
                    ]
                }
            })
        return recipes

    def test_sequential_vs_parallel_validation(self):
        """Compare sequential vs parallel recipe validation performance."""
        recipe_count = 20
        recipes_data = self._create_test_recipes(recipe_count)

        # Sequential processing
        with PerformanceTimer() as sequential_timer:
            sequential_results = [
                self._cpu_intensive_validation(data) for data in recipes_data
            ]

        # Parallel processing with ThreadPoolExecutor
        with PerformanceTimer() as parallel_timer:
            with ThreadPoolExecutor(max_workers=4) as executor:
                parallel_results = list(executor.map(self._cpu_intensive_validation, recipes_data))

        # Parallel processing with ProcessPoolExecutor
        with PerformanceTimer() as process_timer:
            with ProcessPoolExecutor(max_workers=4) as executor:
                process_results = list(executor.map(self._cpu_intensive_validation, recipes_data))

        assert len(sequential_results) == recipe_count
        assert len(parallel_results) == recipe_count
        assert len(process_results) == recipe_count

        print(f"Sequential: {sequential_timer.elapsed:.3f}s")
        print(f"Parallel (threads): {parallel_timer.elapsed:.3f}s")
        print(f"Parallel (processes): {process_timer.elapsed:.3f}s")

        # Parallel should be faster than sequential for CPU-intensive work
        thread_speedup = sequential_timer.elapsed / parallel_timer.elapsed
        process_speedup = sequential_timer.elapsed / process_timer.elapsed

        print(f"Thread speedup: {thread_speedup:.2f}x")
        print(f"Process speedup: {process_speedup:.2f}x")

        # Should show some improvement, but not requiring specific values
        # due to system-dependent performance characteristics
        assert process_speedup > 1.0, f"Process parallelization should show speedup, got {process_speedup:.2f}x"

    def test_async_recipe_processing(self):
        """Test asynchronous recipe processing performance."""
        async def async_validate_recipe(recipe_data: dict[str, Any]) -> UserRecipe:
            """Async validation with simulated I/O delay."""
            await asyncio.sleep(0.01)  # Simulate I/O
            return UserRecipe(**recipe_data)

        async def sequential_async():
            """Process recipes sequentially with async/await."""
            recipes_data = self._create_test_recipes(10)
            results = []
            for data in recipes_data:
                result = await async_validate_recipe(data)
                results.append(result)
            return results

        async def concurrent_async():
            """Process recipes concurrently with asyncio.gather."""
            recipes_data = self._create_test_recipes(10)
            tasks = [async_validate_recipe(data) for data in recipes_data]
            return await asyncio.gather(*tasks)

        # Sequential async
        with PerformanceTimer() as sequential_timer:
            sequential_results = asyncio.run(sequential_async())

        # Concurrent async
        with PerformanceTimer() as concurrent_timer:
            concurrent_results = asyncio.run(concurrent_async())

        assert len(sequential_results) == 10
        assert len(concurrent_results) == 10

        print(f"Sequential async: {sequential_timer.elapsed:.3f}s")
        print(f"Concurrent async: {concurrent_timer.elapsed:.3f}s")

        # Concurrent should be significantly faster for I/O-bound work
        speedup = sequential_timer.elapsed / concurrent_timer.elapsed
        print(f"Async speedup: {speedup:.2f}x")

        assert speedup > 5.0, f"Async concurrency should show significant speedup, got {speedup:.2f}x"

    def test_resource_usage_under_load(self):
        """Test system resource usage under parallel processing load."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Monitor CPU and memory during parallel processing
        recipes_data = self._create_test_recipes(50)

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent_before = process.cpu_percent()

        with PerformanceTimer() as timer, ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self._cpu_intensive_validation, recipes_data))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent_after = process.cpu_percent()

        memory_increase = final_memory - initial_memory

        print(f"Parallel processing of {len(recipes_data)} recipes:")
        print(f"  Time: {timer.elapsed:.3f}s")
        print(f"  Memory increase: {memory_increase:.1f}MB")
        print(f"  CPU usage: {cpu_percent_after:.1f}%")

        assert len(results) == 50
        # Memory usage should remain reasonable
        assert memory_increase < 200, f"Memory increase {memory_increase:.1f}MB should be under 200MB"


class TestPerformanceBenchmarks:
    """Integration tests for overall performance benchmarks."""

    @pytest.mark.skipif(not HAS_BENCHMARK, reason="pytest-benchmark not available")
    def test_end_to_end_recipe_processing_benchmark(self, benchmark):
        """Benchmark complete recipe processing workflow."""
        def full_recipe_workflow():
            # Create recipe
            recipe_data = {
                "name": "E2E Benchmark Recipe",
                "version": "1.0.0",
                "prd": {
                    "content": "# End-to-End Test\n\nComplete workflow benchmark.",
                    "format": "markdown"
                },
                "instructions": {
                    "diagrams": [
                        {
                            "type": "e2e_system_architecture",
                            "description": "System architecture diagram",
                            "framework_preference": "d2"
                        },
                        {
                            "type": "e2e_data_flow",
                            "description": "Data flow diagram",
                            "framework_preference": "mermaid"
                        }
                    ],
                    "documentation": {
                        "style": "technical",
                        "detail_level": "detailed"
                    }
                }
            }

            # Validate recipe
            recipe = UserRecipe(**recipe_data)

            # Simulate processing (create processed recipe structure)
            processed_data = {
                "name": recipe.name,
                "version": recipe.version,
                "source_recipe": "/path/to/source.yaml",
                "generated_at": datetime.now(),
                "content_files": [
                    {
                        "path": "docs/index.md",
                        "type": "markdown",
                        "content": "# Documentation\n\nGenerated content.",
                        "diagram_refs": ["e2e_system_architecture", "e2e_data_flow"]
                    }
                ],
                "diagram_specs": [
                    {
                        "id": "e2e_system_architecture",
                        "framework": "d2",
                        "spec_content": "direction: right\napi -> db",
                        "output_formats": ["svg", "png"],
                        "style_config": {}
                    },
                    {
                        "id": "e2e_data_flow",
                        "framework": "mermaid",
                        "spec_content": "graph TD\nA --> B",
                        "output_formats": ["svg"],
                        "style_config": {}
                    }
                ],
                "diagram_refs": [
                    {
                        "id": "e2e_system_architecture",
                        "title": "System Architecture",
                        "type": "system_architecture",
                        "expected_path": "docs/assets/system_architecture.svg"
                    },
                    {
                        "id": "e2e_data_flow",
                        "title": "Data Flow",
                        "type": "data_flow",
                        "expected_path": "docs/assets/data_flow.svg"
                    }
                ],
                "outputs": {
                    "assets_dir": "docs/assets"
                }
            }

            return recipe, processed_data

        result = benchmark(full_recipe_workflow)
        recipe, processed_data = result

        assert recipe.name == "E2E Benchmark Recipe"
        assert len(processed_data["diagram_specs"]) == 2

    def test_performance_regression_detection(self):
        """Test for performance regressions by establishing baselines."""
        # Simple baseline test - recipe validation should be fast
        simple_recipe_data = {
            "name": "Baseline Recipe",
            "version": "1.0.0",
            "prd": {"content": "# Simple test", "format": "markdown"},
            "instructions": {
                "diagrams": [{"type": "baseline_test", "description": "Baseline"}]
            }
        }

        # Measure baseline performance
        times = []
        for _ in range(10):
            with PerformanceTimer() as timer:
                UserRecipe(**simple_recipe_data)
            times.append(timer.elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        print(f"Baseline performance - Average: {avg_time:.4f}s, Max: {max_time:.4f}s")

        # Performance thresholds
        assert avg_time < 0.01, f"Average validation time {avg_time:.4f}s exceeds 0.01s threshold"
        assert max_time < 0.05, f"Max validation time {max_time:.4f}s exceeds 0.05s threshold"

        # Store results for future regression testing
        # In a real implementation, this could write to a file or database
        baseline_results = {
            "timestamp": datetime.now().isoformat(),
            "avg_validation_time": avg_time,
            "max_validation_time": max_time,
            "test_iterations": 10
        }

        print("Baseline established:", baseline_results)


# Utility functions for performance testing
def measure_memory_usage():
    """Get current memory usage in MB."""
    try:
        import os

        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return None


def stress_test_validation(iterations: int = 1000):
    """Stress test recipe validation with many iterations."""
    recipe_data = {
        "name": "Stress Test Recipe",
        "version": "1.0.0",
        "prd": {"content": "# Stress test", "format": "markdown"},
        "instructions": {
            "diagrams": [{"type": "stress_test", "description": "Stress testing"}]
        }
    }

    with PerformanceTimer() as timer:
        for i in range(iterations):
            UserRecipe(**recipe_data)

    avg_time = timer.elapsed / iterations
    ops_per_second = iterations / timer.elapsed

    return {
        "iterations": iterations,
        "total_time": timer.elapsed,
        "avg_time_per_operation": avg_time,
        "operations_per_second": ops_per_second
    }


if __name__ == "__main__":
    # Quick performance check when run directly
    print("T2D Kit Performance Test Suite")
    print("=" * 40)

    # Run a quick stress test
    print("Running stress test...")
    results = stress_test_validation(100)
    print(f"Validated {results['iterations']} recipes in {results['total_time']:.3f}s")
    print(f"Average: {results['avg_time_per_operation']:.6f}s per recipe")
    print(f"Throughput: {results['operations_per_second']:.0f} recipes/sec")

    if HAS_BENCHMARK:
        print("\npytest-benchmark is available - run with:")
        print("pytest tests/performance/test_processing.py --benchmark-only")
    else:
        print("\nFor detailed benchmarking, install pytest-benchmark:")
        print("pip install pytest-benchmark")
