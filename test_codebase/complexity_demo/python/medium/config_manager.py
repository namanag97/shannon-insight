"""
Medium complexity Python - reasonable structure
"""
import os
import json
from typing import List, Optional, Dict
from datetime import datetime


class ConfigManager:
    """Manage configuration files with caching."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.cache: Dict[str, dict] = {}
        self.ensure_config_dir()

    def ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def load_config(self, name: str) -> Optional[dict]:
        """Load configuration from file."""
        if name in self.cache:
            return self.cache[name]

        config_path = os.path.join(self.config_dir, f"{name}.json")

        if not os.path.exists(config_path):
            return None

        with open(config_path, "r") as f:
            config = json.load(f)
            self.cache[name] = config
            return config

    def save_config(self, name: str, data: dict) -> bool:
        """Save configuration to file."""
        config_path = os.path.join(self.config_dir, f"{name}.json")

        try:
            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)
            self.cache[name] = data
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_value(self, config_name: str, key: str, default=None):
        """Get a specific value from configuration."""
        config = self.load_config(config_name)
        if config is None:
            return default
        return config.get(key, default)


class DataProcessor:
    """Process and transform data."""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def process_items(self, items: List[dict]) -> List[dict]:
        """Process a list of items based on config."""
        result = []
        processor_type = self.config.get_value("settings", "processor", "default")

        for item in items:
            processed = self._transform_item(item, processor_type)
            if processed:
                result.append(processed)

        return result

    def _transform_item(self, item: dict, processor_type: str) -> Optional[dict]:
        """Transform a single item."""
        if processor_type == "uppercase":
            item["name"] = item.get("name", "").upper()
        elif processor_type == "lowercase":
            item["name"] = item.get("name", "").lower()
        elif processor_type == "timestamp":
            item["processed_at"] = datetime.now().isoformat()

        return item if item else None


def main():
    """Main function for testing."""
    config_mgr = ConfigManager()
    processor = DataProcessor(config_mgr)

    sample_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35},
    ]

    processed = processor.process_items(sample_data)
    print(f"Processed {len(processed)} items")
    return processed
