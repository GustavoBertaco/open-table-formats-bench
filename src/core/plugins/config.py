"""
Configuration for dependency management.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class DependencyConfig:
    """Configuration for dependency management."""
    
    # Cache TTL in hours
    cache_ttl: timedelta = timedelta(hours=1)
    
    # Max depth for recursive dependency resolution
    max_depth: int = 5
    
    # Whether to allow optional dependencies to fail silently
    ignore_optional: bool = True
    
    # Package index URLs
    package_index: str = "https://pypi.org/simple"
    extra_indexes: Optional[list[str]] = None
    
    # Timeout for package version lookups
    lookup_timeout: float = 5.0
    
    @classmethod
    def default(cls) -> "DependencyConfig":
        """Get default configuration."""
        return cls()