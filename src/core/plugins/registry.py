"""
Plugin registry implementation.
"""

import asyncio
from typing import Dict, List, Optional, Type

from ..models import PluginMetadata, PluginStatus, TableFormat, ValidationResult
from .base import ITableFormatPlugin


class PluginRegistry:
    """
    Central registry for managing table format plugins.
    Handles plugin discovery, registration, and lifecycle management.
    """

    def __init__(self):
        self._plugins: Dict[str, ITableFormatPlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._active_formats: List[str] = []

    @property
    def plugins(self) -> Dict[str, ITableFormatPlugin]:
        """Get all registered plugins."""
        return self._plugins.copy()

    @property
    def metadata(self) -> Dict[str, PluginMetadata]:
        """Get metadata for all plugins."""
        return self._metadata.copy()

    @property
    def active_formats(self) -> List[str]:
        """Get list of active format IDs."""
        return self._active_formats.copy()

    async def register_plugin(self, plugin: ITableFormatPlugin) -> ValidationResult:
        """
        Register a new plugin with validation.
        
        Args:
            plugin: The plugin instance to register
            
        Returns:
            ValidationResult indicating success/failure
        """
        # Verify plugin isn't already registered
        if plugin.id in self._plugins:
            return ValidationResult(
                is_valid=False,
                errors=[f"Plugin {plugin.id} is already registered"]
            )

        # Check version compatibility with existing plugins
        compat_result = await plugin.check_version_compatibility(list(self._plugins.values()))
        if not compat_result.is_compatible:
            return ValidationResult(
                is_valid=False,
                errors=[f"Version compatibility check failed: {compat_result.conflicts}"]
            )

        # Validate dependencies
        dep_result = await plugin.validate_dependencies()
        if not dep_result.is_valid:
            return ValidationResult(
                is_valid=False,
                errors=dep_result.errors
            )

        # Create metadata
        format_info = TableFormat(
            name=plugin.name,
            version=plugin.version,
            status=PluginStatus.REGISTERED
        )
        
        metadata = PluginMetadata(
            id=plugin.id,
            name=plugin.name,
            version=plugin.version,
            format=format_info,
            interfaces=self._get_implemented_interfaces(plugin),
            dependencies={}  # Will be populated during initialization
        )

        # Store plugin and metadata
        self._plugins[plugin.id] = plugin
        self._metadata[plugin.id] = metadata

        return ValidationResult(is_valid=True)

    async def initialize_plugin(self, plugin_id: str) -> ValidationResult:
        """
        Initialize a registered plugin.
        
        Args:
            plugin_id: ID of plugin to initialize
            
        Returns:
            ValidationResult indicating success/failure
        """
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return ValidationResult(
                is_valid=False,
                errors=[f"Plugin {plugin_id} not found"]
            )

        try:
            # Update status
            metadata = self._metadata[plugin_id]
            metadata.format.status = PluginStatus.INITIALIZING

            # Initialize plugin
            await plugin.initialize()

            # Update status on success
            metadata.format.status = PluginStatus.ACTIVE
            if plugin_id not in self._active_formats:
                self._active_formats.append(plugin_id)

            return ValidationResult(is_valid=True)

        except Exception as e:
            # Update status on failure
            metadata.format.status = PluginStatus.ERROR
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to initialize plugin {plugin_id}: {str(e)}"]
            )

    async def shutdown_plugin(self, plugin_id: str) -> ValidationResult:
        """
        Shutdown an active plugin.
        
        Args:
            plugin_id: ID of plugin to shutdown
            
        Returns:
            ValidationResult indicating success/failure
        """
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return ValidationResult(
                is_valid=False,
                errors=[f"Plugin {plugin_id} not found"]
            )

        try:
            await plugin.shutdown()
            
            # Update status
            metadata = self._metadata[plugin_id]
            metadata.format.status = PluginStatus.REGISTERED
            
            # Remove from active formats
            if plugin_id in self._active_formats:
                self._active_formats.remove(plugin_id)

            return ValidationResult(is_valid=True)

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to shutdown plugin {plugin_id}: {str(e)}"]
            )

    async def get_plugin(self, plugin_id: str) -> Optional[ITableFormatPlugin]:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    async def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID."""
        return self._metadata.get(plugin_id)

    def _get_implemented_interfaces(self, plugin: ITableFormatPlugin) -> List[str]:
        """Get list of interfaces implemented by plugin."""
        interfaces = []
        for base in plugin.__class__.__mro__:
            if base != object and hasattr(base, "__abstractmethods__"):
                interfaces.append(base.__name__)
        return interfaces