"""
Tests for dependency management system.
"""

import pytest
from datetime import datetime
from packaging.version import parse

from ..models import (
    DependencyScope,
    DependencySpec,
    PluginMetadata,
)
from .dependencies import DependencyManager


@pytest.fixture
def dependency_manager():
    return DependencyManager()


@pytest.fixture
def sample_plugin_metadata():
    return PluginMetadata(
        id="test-plugin",
        name="Test Plugin",
        version="1.0.0",
        description="Test plugin for dependency management",
        dependencies={
            "numpy": DependencySpec(
                type="REQUIRED",
                version=">=1.20.0",
                scope=DependencyScope.RUNTIME
            ),
            "pytest": DependencySpec(
                type="REQUIRED",
                version=">=6.0.0",
                scope=DependencyScope.TEST
            )
        }
    )


async def test_validate_dependencies_empty(dependency_manager):
    """Test validation with no dependencies."""
    plugin = PluginMetadata(
        id="empty-plugin",
        name="Empty Plugin",
        version="1.0.0",
        description="Plugin with no dependencies",
        dependencies={}
    )
    
    result = await dependency_manager.validate_dependencies(plugin)
    assert result.is_valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


async def test_validate_dependencies_cache(dependency_manager, sample_plugin_metadata):
    """Test dependency validation caching."""
    # First validation
    result1 = await dependency_manager.validate_dependencies(sample_plugin_metadata)
    
    # Cache should be used for second validation
    result2 = await dependency_manager.validate_dependencies(sample_plugin_metadata)
    
    assert result1 == result2
    
    # Modify cache TTL to expire cache
    dependency_manager._cache_ttl = datetime.timedelta(seconds=0)
    
    # Should revalidate
    result3 = await dependency_manager.validate_dependencies(sample_plugin_metadata)
    assert result3 == result1  # Results should still match


async def test_resolve_dependencies_no_conflicts(dependency_manager):
    """Test dependency resolution with no conflicts."""
    plugins = [
        PluginMetadata(
            id="plugin1",
            name="Plugin 1",
            version="1.0.0",
            description="First test plugin",
            dependencies={
                "numpy": DependencySpec(
                    type="REQUIRED",
                    version=">=1.20.0",
                    scope=DependencyScope.RUNTIME
                )
            }
        ),
        PluginMetadata(
            id="plugin2",
            name="Plugin 2",
            version="1.0.0",
            description="Second test plugin",
            dependencies={
                "numpy": DependencySpec(
                    type="REQUIRED",
                    version=">=1.20.0",
                    scope=DependencyScope.RUNTIME
                )
            }
        )
    ]
    
    result = await dependency_manager.resolve_dependencies(plugins)
    assert result.is_valid
    assert len(result.errors) == 0


async def test_resolve_dependencies_with_conflicts(dependency_manager):
    """Test dependency resolution with conflicts."""
    plugins = [
        PluginMetadata(
            id="plugin1",
            name="Plugin 1",
            version="1.0.0",
            description="First test plugin",
            dependencies={
                "numpy": DependencySpec(
                    type="REQUIRED",
                    version=">=1.20.0",
                    scope=DependencyScope.RUNTIME
                )
            }
        ),
        PluginMetadata(
            id="plugin2",
            name="Plugin 2",
            version="1.0.0",
            description="Second test plugin",
            dependencies={
                "numpy": DependencySpec(
                    type="REQUIRED",
                    version="<1.20.0",
                    scope=DependencyScope.RUNTIME
                )
            }
        )
    ]
    
    result = await dependency_manager.resolve_dependencies(plugins)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("Incompatible version" in error for error in result.errors)


@pytest.mark.asyncio
async def test_get_installed_version(dependency_manager, monkeypatch):
    """Test getting installed package version."""
    async def mock_get_version(*args):
        return parse("1.21.0")
    
    monkeypatch.setattr(dependency_manager, "_get_installed_version", mock_get_version)
    
    version = await dependency_manager._get_installed_version("numpy")
    assert str(version) == "1.21.0"