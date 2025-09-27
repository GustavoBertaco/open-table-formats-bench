# Data Model: Initial Table Format Dependencies Setup

## Core Entities

### TableFormat
```yaml
name: string           # Name of the table format
version: string        # Version of the format implementation
dependencies: Dict     # Map of dependencies and their versions
enabled: boolean      # Whether the format is currently enabled
status: enum          # REGISTERED, INITIALIZING, ACTIVE, ERROR
```

### PluginMetadata
```yaml
id: string            # Unique identifier for the plugin
name: string          # Display name
version: string       # Plugin version
format: TableFormat   # Reference to table format
interfaces: string[]  # List of implemented interfaces
dependencies: Dict    # Plugin-specific dependencies
```

### DependencySpec
```yaml
name: string          # Name of the dependency
version: string       # Version requirement
type: enum           # REQUIRED, OPTIONAL
scope: enum          # RUNTIME, TEST
```

### PluginRegistry
```yaml
plugins: PluginMetadata[]    # List of registered plugins
activeFormats: string[]      # Currently active format IDs
globalDependencies: Dict     # Shared dependencies
```

## Relationships

1. TableFormat ⟶ PluginMetadata
   - One-to-one relationship
   - TableFormat is implemented by exactly one plugin
   - Plugin implements exactly one table format

2. PluginRegistry ⟶ PluginMetadata
   - One-to-many relationship
   - Registry maintains list of all plugins
   - Each plugin belongs to one registry

## Validation Rules

1. Version Compatibility
   - Version formats must be semantic versioning compliant
   - Version conflicts must be detected at registration
   - Dependency versions must be explicitly specified

2. Plugin Registration
   - Plugin IDs must be unique
   - Required interfaces must be implemented
   - Dependencies must be resolvable

3. Dependency Management
   - No circular dependencies allowed
   - Version conflicts must be prevented
   - Optional dependencies must be handled gracefully

## State Transitions

1. Plugin Lifecycle
   ```
   REGISTERED → INITIALIZING → ACTIVE
                     ↓
                   ERROR
   ```

2. Version Resolution
   ```
   CHECK_DEPENDENCIES → RESOLVE_VERSIONS → VALIDATE_COMPATIBILITY
                           ↓
                     REPORT_CONFLICTS
   ```

## Configuration Schema

```yaml
tableFormats:
  - name: string
    version: string
    enabled: boolean
    dependencies:
      name: version
    config:
      # Format-specific configuration

plugins:
  discovery:
    paths: string[]
    autoEnable: boolean
  
  validation:
    level: string  # "full" for integration tests
    timeout: number
    retries: number

dependencies:
  central:
    repository: string
    cacheDir: string
  resolution:
    strategy: string  # "strict" or "flexible"
    conflicts: string # "fail" or "warn"
```