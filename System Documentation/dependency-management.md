# Dependency Management System

The project includes a robust dependency management system for handling plugin dependencies, ensuring compatibility and proper version resolution across different table format plugins.

## Key Features

- Asynchronous dependency validation
- Smart caching system for performance optimization
- Version requirement resolution with conflict detection
- Support for runtime and test dependencies
- Detailed error reporting with resolution suggestions
- Configurable package index sources

## Usage

### Basic Usage

```python
from core.plugins.dependencies import DependencyManager
from core.plugins.config import DependencyConfig

# Create a dependency manager with default configuration
manager = DependencyManager()

# Validate dependencies for a plugin
result = await manager.validate_dependencies(plugin_metadata)
if result.is_valid:
    print("All dependencies are satisfied!")
else:
    print("Validation errors:", result.errors)
    print("Warnings:", result.warnings)
```

### Custom Configuration

You can customize the dependency management behavior:

```python
from datetime import timedelta

config = DependencyConfig(
    cache_ttl=timedelta(minutes=30),  # Cache validation results for 30 minutes
    ignore_optional=False,            # Treat optional dependencies as required
    max_depth=3,                     # Maximum depth for recursive dependency resolution
    package_index="https://custom-pypi.org/simple",  # Custom package index
    lookup_timeout=10.0              # Longer timeout for package lookups
)

manager = DependencyManager(config)
```

### Multi-Plugin Dependency Resolution

When working with multiple plugins, you can resolve dependencies across all of them:

```python
plugins = [plugin1, plugin2, plugin3]
result = await manager.resolve_dependencies(plugins)

if not result.is_valid:
    print("Dependency conflicts found:")
    for error in result.errors:
        print(f"- {error}")
```

## Plugin Metadata Example

To use the dependency management system, your plugin metadata should include dependency specifications:

```python
from core.models import PluginMetadata, DependencySpec, DependencyScope

plugin = PluginMetadata(
    id="delta-plugin",
    name="Delta Lake Plugin",
    version="1.0.0",
    description="Delta Lake format support",
    dependencies={
        "delta-spark": DependencySpec(
            type="REQUIRED",
            version=">=2.0.0",
            scope=DependencyScope.RUNTIME
        ),
        "pytest": DependencySpec(
            type="REQUIRED",
            version=">=7.0.0",
            scope=DependencyScope.TEST
        )
    }
)
```

## Error Handling

The system provides detailed error information when dependencies cannot be satisfied:

```python
# Example error response
{
    "code": "DEP001",
    "severity": "ERROR",
    "component": "delta-plugin",
    "message": "Required dependency delta-spark is not installed",
    "context": {
        "operation": "dependency_validation",
        "dependency": "delta-spark",
        "required_version": ">=2.0.0",
        "found_version": None
    },
    "resolution": [
        "Install delta-spark version >=2.0.0",
        "Check package repository accessibility"
    ]
}
```

## Caching Behavior

The dependency management system includes a caching mechanism to improve performance:

- Validation results are cached based on plugin ID and version
- Cache TTL is configurable (default: 1 hour)
- Cache is automatically invalidated when dependencies change
- Separate caches for package versions and validation results

## Testing Support

The system includes comprehensive test coverage. You can run the tests using:

```bash
pytest src/core/plugins/test_dependencies.py
```