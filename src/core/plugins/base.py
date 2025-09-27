"""
Core plugin interface and base implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from ..models import (
    CompatibilityResult,
    DependencySpec,
    DiagnosticResult,
    PluginStatus,
    ValidationResult,
)


class ITableFormatPlugin(ABC):
    """Interface that all table format plugins must implement."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the plugin."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[DependencySpec]:
        """Get the plugin's dependencies."""
        pass

    @abstractmethod
    async def validate_dependencies(self) -> ValidationResult:
        """Validate that all dependencies are satisfied."""
        pass

    @abstractmethod
    async def check_version_compatibility(
        self, other_plugins: List["ITableFormatPlugin"]
    ) -> CompatibilityResult:
        """Check version compatibility with other plugins."""
        pass

    @abstractmethod
    def get_status(self) -> PluginStatus:
        """Get the current plugin status."""
        pass

    @abstractmethod
    async def run_diagnostics(self) -> DiagnosticResult:
        """Run plugin diagnostics."""
        pass


class BaseTableFormatPlugin(ITableFormatPlugin):
    """Base implementation of ITableFormatPlugin with common functionality."""

    def __init__(self, plugin_id: str, name: str, version: str):
        self._id = plugin_id
        self._name = name
        self._version = version
        self._status = PluginStatus.REGISTERED

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def get_status(self) -> PluginStatus:
        return self._status

    async def validate_dependencies(self) -> ValidationResult:
        """Base dependency validation."""
        dependencies = self.get_dependencies()
        # Implement basic validation logic here
        return ValidationResult(is_valid=True)

    async def check_version_compatibility(
        self, other_plugins: List[ITableFormatPlugin]
    ) -> CompatibilityResult:
        """Base version compatibility check."""
        # Implement basic compatibility check logic here
        return CompatibilityResult(is_compatible=True)

    async def run_diagnostics(self) -> DiagnosticResult:
        """Base diagnostics implementation."""
        return DiagnosticResult(
            status=self.get_status(),
            details={"plugin_id": self.id, "version": self.version},
        )