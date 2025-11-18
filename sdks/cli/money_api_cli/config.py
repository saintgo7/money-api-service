"""Configuration management."""
import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Manage CLI configuration."""

    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / ".money-api"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}

        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _save_config(self, config: dict):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def get_api_key(self) -> Optional[str]:
        """Get API key from config."""
        config = self._load_config()
        return config.get('api_key')

    def set_api_key(self, api_key: str):
        """Set API key in config."""
        config = self._load_config()
        config['api_key'] = api_key
        self._save_config(config)

    def get_base_url(self) -> str:
        """Get base URL from config."""
        config = self._load_config()
        return config.get('base_url', 'https://api.money-api.com')

    def set_base_url(self, base_url: str):
        """Set base URL in config."""
        config = self._load_config()
        config['base_url'] = base_url
        self._save_config(config)

    def get(self, key: str, default=None):
        """Get configuration value."""
        config = self._load_config()
        return config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value."""
        config = self._load_config()
        config[key] = value
        self._save_config(config)
