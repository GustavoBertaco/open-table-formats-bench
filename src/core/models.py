"""
Core data models for the plugin system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PluginStatus(str, Enum):
    """Status of a plugin in the system."""
    REGISTERED = "REGISTERED"
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"


class DependencyType(str, Enum):
    """Type of dependency requirement."""
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"


class DependencyScope(str, Enum):
    """Scope of the dependency."""
    RUNTIME = "RUNTIME"
    TEST = "TEST"


class DependencySpec(BaseModel):
    """Specification for a plugin dependency."""
    name: str = Field(..., description="Name of the dependency")
    version: str = Field(..., description="Version requirement")
    type: DependencyType = Field(DependencyType.REQUIRED, description="Type of dependency")
    scope: DependencyScope = Field(DependencyScope.RUNTIME, description="Scope of dependency")


class TableFormat(BaseModel):
    """Represents a table format implementation."""
    name: str = Field(..., description="Name of the table format")
    version: str = Field(..., description="Version of the format implementation")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Map of dependencies and versions")
    enabled: bool = Field(True, description="Whether the format is currently enabled")
    status: PluginStatus = Field(PluginStatus.REGISTERED, description="Current status of the format")


class PluginMetadata(BaseModel):
    """Metadata for a plugin in the system."""
    id: str = Field(..., description="Unique identifier for the plugin")
    name: str = Field(..., description="Display name")
    version: str = Field(..., description="Plugin version")
    format: TableFormat = Field(..., description="Reference to table format")
    interfaces: List[str] = Field(default_factory=list, description="List of implemented interfaces")
    dependencies: Dict[str, DependencySpec] = Field(
        default_factory=dict,
        description="Plugin-specific dependencies"
    )


class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")


class CompatibilityResult(BaseModel):
    """Result of a compatibility check."""
    is_compatible: bool = Field(..., description="Whether versions are compatible")
    conflicts: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of compatibility conflicts"
    )


class DiagnosticResult(BaseModel):
    """Result of plugin diagnostics."""
    status: PluginStatus = Field(..., description="Current plugin status")
    details: Dict = Field(default_factory=dict, description="Additional diagnostic details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of diagnosis")


class ErrorResponse(BaseModel):
    """Structured error response."""
    code: str = Field(..., description="Unique error identifier")
    severity: str = Field(..., description="ERROR, WARN, or INFO")
    component: str = Field(..., description="Affected plugin or system component")
    message: str = Field(..., description="Human-readable description")
    context: Dict = Field(..., description="Error context details")
    resolution: List[str] = Field(default_factory=list, description="Resolution steps")
    timestamp: datetime = Field(default_factory=datetime.utcnow)