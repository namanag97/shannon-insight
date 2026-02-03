"""
Caching system for Shannon Insight.

Uses diskcache for SQLite-based persistent caching.
"""

import hashlib
import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from diskcache import Cache

from .logging_config import get_logger

logger = get_logger(__name__)


class AnalysisCache:
    """
    SQLite-based cache for analysis results.

    Features:
    - Automatic cache key generation from file metadata
    - TTL-based expiration
    - Thread-safe operations
    - Efficient disk storage
    """

    def __init__(
        self,
        cache_dir: str = ".shannon-cache",
        ttl_hours: int = 24,
        enabled: bool = True
    ):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache storage
            ttl_hours: Time-to-live in hours
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.ttl_seconds = ttl_hours * 3600

        if self.enabled:
            self.cache = Cache(cache_dir)
            logger.debug(f"Cache initialized at {cache_dir} with TTL={ttl_hours}h")
        else:
            self.cache = None
            logger.debug("Cache disabled")

    def _get_file_key(self, filepath: Path, config_hash: str) -> str:
        """
        Generate cache key from file metadata and configuration.

        The key is based on:
        - File path
        - File modification time
        - File size
        - Configuration hash

        Args:
            filepath: File path
            config_hash: Hash of configuration settings

        Returns:
            Cache key string
        """
        try:
            stat = filepath.stat()
            key_data = f"{filepath}:{stat.st_mtime}:{stat.st_size}:{config_hash}"
            return hashlib.sha256(key_data.encode()).hexdigest()
        except OSError:
            # If we can't stat the file, generate key from path only
            key_data = f"{filepath}:{config_hash}"
            return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled or self.cache is None:
            return None

        try:
            value = self.cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key[:16]}...")
            return value
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.enabled or self.cache is None:
            return

        try:
            self.cache.set(key, value, expire=self.ttl_seconds)
            logger.debug(f"Cache set: {key[:16]}...")
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def clear(self) -> None:
        """Clear all cache entries."""
        if not self.enabled or self.cache is None:
            return

        try:
            self.cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or self.cache is None:
            return {"enabled": False}

        try:
            return {
                "enabled": True,
                "size": len(self.cache),
                "directory": self.cache.directory,
                "volume": self.cache.volume()
            }
        except Exception as e:
            logger.warning(f"Cache stats failed: {e}")
            return {"enabled": True, "error": str(e)}

    def memoize(
        self,
        config_hash: Optional[str] = None
    ) -> Callable:
        """
        Decorator for caching function results.

        Usage:
            cache = AnalysisCache()

            @cache.memoize(config_hash="abc123")
            def analyze_file(filepath: Path) -> FileMetrics:
                # Expensive operation
                return metrics

        Args:
            config_hash: Hash of configuration (for cache invalidation)

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(filepath: Path, *args, **kwargs):
                if not self.enabled or self.cache is None:
                    return func(filepath, *args, **kwargs)

                # Generate cache key
                cfg_hash = config_hash or kwargs.get('config_hash', '')
                key = self._get_file_key(filepath, cfg_hash)

                # Try cache first
                cached_result = self.get(key)
                if cached_result is not None:
                    return cached_result

                # Compute and cache
                result = func(filepath, *args, **kwargs)
                self.set(key, result)
                return result

            return wrapper
        return decorator

    def close(self) -> None:
        """Close cache (cleanup)."""
        if self.cache is not None:
            self.cache.close()


def compute_config_hash(config: dict) -> str:
    """
    Compute hash of configuration for cache invalidation.

    Args:
        config: Configuration dictionary

    Returns:
        SHA256 hash of configuration
    """
    # Sort keys for consistent hashing
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode()).hexdigest()[:16]
