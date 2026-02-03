"""
High complexity Python - deep nesting, many concerns, anti-patterns
"""
import os
import sys
import json
import logging
from typing import List, Dict, Optional, Any, Callable, Tuple
from datetime import datetime
from collections import defaultdict
import hashlib
import base64
import re


class ComplexDataProcessor:
    """
    Overly complex data processor with too many responsibilities.
    Anti-patterns: God class, deep nesting, magic numbers.
    """

    def __init__(self, config_path: Optional[str] = None, verbose: bool = False):
        self.config_path = config_path or "config.json"
        self.verbose = verbose
        self.logger = self._setup_logging()
        self.cache = {}
        self.metrics = defaultdict(int)
        self.validators = []
        self.transformers = []
        self.middleware = []
        self._initialize_components()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with multiple handlers."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
            logger.addHandler(handler)

        return logger

    def _initialize_components(self) -> None:
        """Initialize all components with complex logic."""
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            self.logger.warning(f"Config load failed: {e}, using defaults")
            config = self._get_default_config()

        self._parse_validators(config.get("validators", []))
        self._parse_transformers(config.get("transformers", []))
        self._setup_middleware(config.get("middleware", []))

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with many nested options."""
        return {
            "validators": [
                {"type": "required", "fields": ["id", "name"]},
                {"type": "type", "field": "id", "expected": "int"},
                {"type": "pattern", "field": "email", "pattern": r".+@.+\..+"},
            ],
            "transformers": [
                {"type": "trim", "fields": ["name", "description"]},
                {"type": "upper", "fields": ["name"]},
                {"type": "sanitize", "fields": ["description"]},
            ],
            "middleware": [
                {"type": "cache", "ttl": 300},
                {"type": "metrics", "enabled": True},
            ],
        }

    def _parse_validators(self, validator_configs: List[dict]) -> None:
        """Parse validator configurations with deep nesting."""
        for vc in validator_configs:
            vtype = vc.get("type")
            if vtype == "required":
                fields = vc.get("fields", [])
                for field in fields:
                    self.validators.append(lambda d, f=field: self._validate_required(d, f))
            elif vtype == "type":
                field = vc.get("field")
                expected = vc.get("expected")
                self.validators.append(
                    lambda d, f=field, e=expected: self._validate_type(d, f, e)
                )
            elif vtype == "pattern":
                field = vc.get("field")
                pattern = vc.get("pattern")
                self.validators.append(
                    lambda d, f=field, p=pattern: self._validate_pattern(d, f, p)
                )
            elif vtype == "range":
                field = vc.get("field")
                min_val = vc.get("min")
                max_val = vc.get("max")
                self.validators.append(
                    lambda d, f=field, mn=min_val, mx=max_val: self._validate_range(
                        d, f, mn, mx
                    )
                )
            elif vtype == "custom":
                fn_name = vc.get("function")
                try:
                    fn = getattr(self, fn_name)
                    self.validators.append(lambda d, func=fn: func(d))
                except AttributeError:
                    self.logger.warning(f"Custom validator {fn_name} not found")

    def _parse_transformers(self, transformer_configs: List[dict]) -> None:
        """Parse transformer configurations."""
        for tc in transformer_configs:
            ttype = tc.get("type")
            if ttype == "trim":
                fields = tc.get("fields", [])
                self.transformers.append(
                    lambda d, fs=fields: self._transform_trim(d, fs)
                )
            elif ttype == "upper":
                fields = tc.get("fields", [])
                self.transformers.append(
                    lambda d, fs=fields: self._transform_upper(d, fs)
                )
            elif ttype == "lower":
                fields = tc.get("fields", [])
                self.transformers.append(
                    lambda d, fs=fields: self._transform_lower(d, fs)
                )
            elif ttype == "sanitize":
                fields = tc.get("fields", [])
                self.transformers.append(
                    lambda d, fs=fields: self._transform_sanitize(d, fs)
                )
            elif ttype == "hash":
                fields = tc.get("fields", [])
                algorithm = tc.get("algorithm", "sha256")
                self.transformers.append(
                    lambda d, fs=fields, alg=algorithm: self._transform_hash(
                        d, fs, alg
                    )
                )
            elif ttype == "encode":
                fields = tc.get("fields", [])
                encoding = tc.get("encoding", "base64")
                self.transformers.append(
                    lambda d, fs=fields, enc=encoding: self._transform_encode(
                        d, fs, enc
                    )
                )

    def _setup_middleware(self, middleware_configs: List[dict]) -> None:
        """Setup middleware stack."""
        for mc in middleware_configs:
            mtype = mc.get("type")
            if mtype == "cache":
                ttl = mc.get("ttl", 300)
                self.middleware.append(
                    lambda d, t=ttl: self._middleware_cache(d, t)
                )
            elif mtype == "metrics":
                enabled = mc.get("enabled", True)
                if enabled:
                    self.middleware.append(lambda d: self._middleware_metrics(d))
            elif mtype == "log":
                level = mc.get("level", "info")
                self.middleware.append(lambda d, l=level: self._middleware_log(d, l))

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data through full pipeline with deep nesting."""
        self.logger.info(f"Processing {len(data)} items")

        for i, item in enumerate(data):
            self.metrics["items_processed"] += 1

            if not item:
                self.logger.warning(f"Skipping empty item at index {i}")
                continue

            cache_key = self._generate_cache_key(item)
            cached = self._get_cached_result(cache_key)

            if cached:
                self.metrics["cache_hits"] += 1
                data[i] = cached
                continue

            self.metrics["cache_misses"] += 1
            processed_item = item.copy()

            if not self._validate_item(processed_item):
                self.metrics["validation_failures"] += 1
                continue

            if self._transform_item(processed_item):
                self.metrics["transform_success"] += 1

            for middleware_fn in self.middleware:
                result = middleware_fn(processed_item)
                if result is not None:
                    processed_item = result

            self._cache_result(cache_key, processed_item)
            data[i] = processed_item

        self.metrics["total_time"] = datetime.now().timestamp()
        self._log_metrics()
        return data

    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """Validate item with all validators."""
        valid = True
        for validator in self.validators:
            try:
                result = validator(item)
                if not result:
                    valid = False
                    self.metrics["validation_errors"] += 1
            except Exception as e:
                self.logger.error(f"Validator error: {e}")
                valid = False

        return valid

    def _transform_item(self, item: Dict[str, Any]) -> bool:
        """Transform item with all transformers."""
        success = True
        for transformer in self.transformers:
            try:
                result = transformer(item)
                if result is not None:
                    item.update(result)
            except Exception as e:
                self.logger.error(f"Transformer error: {e}")
                success = False

        return success

    def _generate_cache_key(self, item: Dict[str, Any]) -> str:
        """Generate cache key with multiple hashing."""
        item_str = json.dumps(item, sort_keys=True)
        hash_obj = hashlib.sha256(item_str.encode())
        return base64.b64encode(hash_obj.digest()).decode()

    def _get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result with TTL check."""
        if key in self.cache:
            entry = self.cache[key]
            timestamp = entry.get("timestamp", 0)
            ttl = entry.get("ttl", 300)

            if datetime.now().timestamp() - timestamp < ttl:
                return entry.get("data")

        return None

    def _cache_result(self, key: str, data: Dict[str, Any]) -> None:
        """Cache result with timestamp."""
        self.cache[key] = {"data": data, "timestamp": datetime.now().timestamp(), "ttl": 300}

    def _validate_required(self, item: Dict[str, Any], field: str) -> bool:
        """Validate required field."""
        return field in item and item[field] is not None

    def _validate_type(
        self, item: Dict[str, Any], field: str, expected: str
    ) -> bool:
        """Validate field type."""
        if field not in item:
            return True
        actual = type(item[field]).__name__
        return actual == expected

    def _validate_pattern(
        self, item: Dict[str, Any], field: str, pattern: str
    ) -> bool:
        """Validate field pattern."""
        if field not in item or item[field] is None:
            return True
        return bool(re.match(pattern, str(item[field])))

    def _validate_range(
        self,
        item: Dict[str, Any],
        field: str,
        min_val: float,
        max_val: float,
    ) -> bool:
        """Validate field range."""
        if field not in item or item[field] is None:
            return True
        value = float(item[field])
        return min_val <= value <= max_val

    def _transform_trim(self, item: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Transform trim."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                result[field] = item[field].strip()
        return result

    def _transform_upper(self, item: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Transform uppercase."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                result[field] = item[field].upper()
        return result

    def _transform_lower(self, item: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Transform lowercase."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                result[field] = item[field].lower()
        return result

    def _transform_sanitize(
        self, item: Dict[str, Any], fields: List[str]
    ) -> Dict[str, Any]:
        """Transform sanitize."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                sanitized = re.sub(r"[<>\"'&]", "", item[field])
                result[field] = sanitized
        return result

    def _transform_hash(
        self, item: Dict[str, Any], fields: List[str], algorithm: str
    ) -> Dict[str, Any]:
        """Transform hash."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                if algorithm == "sha256":
                    hash_obj = hashlib.sha256(item[field].encode())
                elif algorithm == "md5":
                    hash_obj = hashlib.md5(item[field].encode())
                else:
                    hash_obj = hashlib.sha256(item[field].encode())
                result[f"{field}_hash"] = hash_obj.hexdigest()
        return result

    def _transform_encode(
        self, item: Dict[str, Any], fields: List[str], encoding: str
    ) -> Dict[str, Any]:
        """Transform encode."""
        result = {}
        for field in fields:
            if field in item and isinstance(item[field], str):
                if encoding == "base64":
                    encoded = base64.b64encode(item[field].encode()).decode()
                    result[f"{field}_encoded"] = encoded
        return result

    def _middleware_cache(
        self, item: Dict[str, Any], ttl: int
    ) -> Optional[Dict[str, Any]]:
        """Middleware cache."""
        return None

    def _middleware_metrics(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Middleware metrics."""
        self.metrics["middleware_calls"] += 1
        return None

    def _middleware_log(
        self, item: Dict[str, Any], level: str
    ) -> Optional[Dict[str, Any]]:
        """Middleware log."""
        if level == "debug":
            self.logger.debug(f"Processing item: {item}")
        elif level == "info":
            self.logger.info(f"Processing item")
        elif level == "warning":
            self.logger.warning(f"Item warning: {item}")
        return None

    def _log_metrics(self) -> None:
        """Log all metrics."""
        self.logger.info("=== Processing Metrics ===")
        for key, value in sorted(self.metrics.items()):
            self.logger.info(f"{key}: {value}")
