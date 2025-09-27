"""
Dependency management system for plugins.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from .config import DependencyConfig

from packaging.requirements import Requirement
from packaging.version import Version, parse

from ..models import (
    DependencyScope,
    DependencySpec,
    ErrorResponse,
    PluginMetadata,
    ValidationResult,
)


class DependencyManager:
    """
    Manages dependencies for table format plugins.
    Handles version resolution, validation, and caching.
    """

    def __init__(self, config: Optional["DependencyConfig"] = None):
        self._config = config or DependencyConfig.default()
        self._dependency_cache: Dict[str, Dict[str, Version]] = {}
        self._validation_cache: Dict[Tuple[str, str], Tuple[ValidationResult, datetime]] = {}

    async def validate_dependencies(
        self, plugin_metadata: PluginMetadata
    ) -> ValidationResult:
        """
        Validate all dependencies for a plugin.
        
        Args:
            plugin_metadata: Plugin metadata containing dependencies
            
        Returns:
            ValidationResult indicating whether all dependencies are satisfied
        """
        cache_key = (plugin_metadata.id, plugin_metadata.version)
        
        # Check cache
        if cache_key in self._validation_cache:
            result, timestamp = self._validation_cache[cache_key]
            if datetime.utcnow() - timestamp < self._config.cache_ttl:
                return result

        errors = []
        warnings = []

        for dep_name, dep_spec in plugin_metadata.dependencies.items():
            # Skip test dependencies in runtime validation
            if dep_spec.scope == DependencyScope.TEST:
                continue

            try:
                # Get installed version
                installed_version = await self._get_installed_version(dep_name)
                if not installed_version:
                    if dep_spec.type == "REQUIRED":
                        errors.append(
                            ErrorResponse(
                                code="DEP001",
                                severity="ERROR",
                                component=plugin_metadata.id,
                                message=f"Required dependency {dep_name} is not installed",
                                context={
                                    "operation": "dependency_validation",
                                    "dependency": dep_name,
                                    "required_version": dep_spec.version,
                                    "found_version": None
                                },
                                resolution=[
                                    f"Install {dep_name} version {dep_spec.version}",
                                    "Check package repository accessibility"
                                ]
                            )
                        )
                    else:
                        warnings.append(f"Optional dependency {dep_name} is not installed")
                    continue

                # Validate version requirement
                req = Requirement(f"{dep_name}{dep_spec.version}")
                if installed_version not in req.specifier:
                    if dep_spec.type == "REQUIRED":
                        errors.append(
                            ErrorResponse(
                                code="DEP002",
                                severity="ERROR",
                                component=plugin_metadata.id,
                                message=f"Incompatible version for {dep_name}",
                                context={
                                    "operation": "dependency_validation",
                                    "dependency": dep_name,
                                    "required_version": dep_spec.version,
                                    "found_version": str(installed_version)
                                },
                                resolution=[
                                    f"Upgrade {dep_name} to version {dep_spec.version}",
                                    f"Or downgrade plugin to version compatible with {dep_name} {installed_version}"
                                ]
                            )
                        )
                    else:
                        warnings.append(
                            f"Optional dependency {dep_name} version {installed_version} "
                            f"does not match requirement {dep_spec.version}"
                        )

            except Exception as e:
                errors.append(
                    ErrorResponse(
                        code="DEP003",
                        severity="ERROR",
                        component=plugin_metadata.id,
                        message=f"Error validating dependency {dep_name}",
                        context={
                            "operation": "dependency_validation",
                            "dependency": dep_name,
                            "error": str(e)
                        },
                        resolution=[
                            "Check package name and version format",
                            "Verify package manager is functioning"
                        ]
                    )
                )

        # Create validation result
        result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=[str(e) for e in errors],
            warnings=warnings
        )

        # Cache the result
        self._validation_cache[cache_key] = (result, datetime.utcnow())

        return result

    async def resolve_dependencies(
        self, plugins: List[PluginMetadata]
    ) -> ValidationResult:
        """
        Resolve dependencies across multiple plugins.
        
        Args:
            plugins: List of plugin metadata to check
            
        Returns:
            ValidationResult indicating whether dependencies can be satisfied
        """
        # Build dependency graph
        dependencies: Dict[str, Set[Tuple[str, str]]] = {}
        for plugin in plugins:
            for dep_name, dep_spec in plugin.dependencies.items():
                if dep_name not in dependencies:
                    dependencies[dep_name] = set()
                dependencies[dep_name].add((plugin.id, dep_spec.version))

        # Check for conflicts
        errors = []
        warnings = []

        for dep_name, requirements in dependencies.items():
            if len(requirements) > 1:
                # Check if versions are compatible
                try:
                    merged_requirement = self._merge_version_requirements(requirements)
                    if not merged_requirement:
                        plugins_str = ", ".join(f"{pid} ({ver})" for pid, ver in requirements)
                        errors.append(
                            ErrorResponse(
                                code="DEP004",
                                severity="ERROR",
                                component="dependency_resolver",
                                message=f"Incompatible version requirements for {dep_name}",
                                context={
                                    "operation": "dependency_resolution",
                                    "dependency": dep_name,
                                    "requirements": list(requirements)
                                },
                                resolution=[
                                    f"Resolve version conflict for {dep_name} between plugins: {plugins_str}",
                                    "Consider updating plugins to use compatible versions"
                                ]
                            )
                        )
                except Exception as e:
                    errors.append(
                        ErrorResponse(
                            code="DEP005",
                            severity="ERROR",
                            component="dependency_resolver",
                            message=f"Error resolving versions for {dep_name}",
                            context={
                                "operation": "dependency_resolution",
                                "dependency": dep_name,
                                "error": str(e)
                            },
                            resolution=[
                                "Check version requirement format",
                                "Verify all version specifications are valid"
                            ]
                        )
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=[str(e) for e in errors],
            warnings=warnings
        )

    async def _get_installed_version(self, package_name: str) -> Optional[Version]:
        """Get the installed version of a package."""
        # Implementation would use importlib.metadata or similar
        # This is a placeholder that should be implemented
        return parse("0.0.0")

    def _merge_version_requirements(
        self, requirements: Set[Tuple[str, str]]
    ) -> Optional[str]:
        """
        Attempt to merge version requirements.
        Returns None if requirements are incompatible.
        """
        # This is a simplified implementation
        # A real implementation would use packaging.specifiers
        return next(iter(requirements))[1] if requirements else None