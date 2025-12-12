#!/usr/bin/env python3
"""
Config Loader - YAML-based Application Configuration Loader
Loads application configuration from YAML files with environment variable override support
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages application configuration from YAML files"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the config loader
        
        Args:
            config_path: Path to the config YAML file
        """
        # Load .env file first (secrets)
        load_dotenv()
        
        self.config_path = Path(config_path)
        self.config = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                logger.warning("Using default configuration")
                self.config = self._get_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            logger.info(f"Loaded configuration from {self.config_path}")
            logger.info(f"Version: {self.config.get('version', 'unknown')}")
            logger.info(f"Default LLM provider: {self.get('llm.default_provider', 'not set')}")
        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.warning("Falling back to default configuration")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get minimal default configuration as fallback"""
        return {
            "version": "1.0",
            "llm": {
                "default_provider": "claude",
                "claude": {
                    "region": "us-west-2",
                    "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                    "default_temperature": 0.7,
                    "default_max_tokens": 131072
                }
            },
            "app": {
                "default_language": "zh_TW",
                "supported_languages": ["zh_TW", "en", "ja"],
                "database": {
                    "path": "prompts.db"
                }
            },
            "prompts": {
                "config_path": "resources/prompts/prompts.yaml",
                "version": "2.0"
            }
        }
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        # Google Cloud Project ID
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            if 'llm' in self.config and 'gemini_vertex' in self.config['llm']:
                self.config['llm']['gemini_vertex']['project_id'] = os.getenv('GOOGLE_CLOUD_PROJECT')
                logger.info("Overriding gemini_vertex.project_id from GOOGLE_CLOUD_PROJECT env var")
        
        # Add more environment variable overrides as needed
        # Example: DATABASE_PATH, DEFAULT_LANGUAGE, etc.
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation path
        
        Args:
            key_path: Dot-separated path (e.g., 'llm.claude.region')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """
        Get LLM provider configuration
        
        Args:
            provider: Provider name (claude, gemini, gemini_vertex, openai)
        
        Returns:
            Provider configuration dict
        """
        return self.config.get('llm', {}).get(provider, {})
    
    def get_default_provider(self) -> str:
        """Get default LLM provider name"""
        return self.get('llm.default_provider', 'claude')
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Get secret from environment variables
        
        Args:
            key: Environment variable name
        
        Returns:
            Secret value or None
        """
        return os.getenv(key)
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.config.get('app', {})
    
    def get_prompt_config(self) -> Dict[str, Any]:
        """Get prompt configuration"""
        return self.config.get('prompts', {})
    
    def get_parameter_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Get parameter preset configuration
        
        Args:
            preset_name: Preset name (balanced, creative, precise, etc.)
        
        Returns:
            Preset parameters dict
        """
        presets = self.config.get('parameter_presets', {})
        return presets.get(preset_name, {})
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return self.get('app.supported_languages', ['zh_TW'])
    
    def get_default_language(self) -> str:
        """Get default language"""
        return self.get('app.default_language', 'zh_TW')
    
    def validate_config(self) -> bool:
        """
        Validate configuration structure
        
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['version', 'llm', 'app']
        
        for key in required_keys:
            if key not in self.config:
                logger.error(f"Missing required key: {key}")
                return False
        
        # Validate LLM config
        if 'default_provider' not in self.config.get('llm', {}):
            logger.error("Missing llm.default_provider")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def reload(self) -> None:
        """Reload configuration from file (hot reload)"""
        logger.info("Reloading configuration...")
        self._load()
    
    def get_version(self) -> str:
        """Get configuration version"""
        return self.config.get('version', 'unknown')
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get entire configuration dict"""
        return self.config.copy()


# Singleton instance for global access
_default_config_loader = None


def get_default_config_loader() -> ConfigLoader:
    """Get default singleton config loader instance"""
    global _default_config_loader
    if _default_config_loader is None:
        _default_config_loader = ConfigLoader()
    return _default_config_loader


if __name__ == "__main__":
    # Test the loader
    print("Testing ConfigLoader...")
    
    loader = ConfigLoader()
    
    print(f"\nVersion: {loader.get_version()}")
    print(f"Valid: {loader.validate_config()}")
    
    print(f"\n=== LLM Configuration ===")
    print(f"Default Provider: {loader.get_default_provider()}")
    
    claude_config = loader.get_llm_config('claude')
    print(f"\nClaude Config:")
    print(f"  Region: {claude_config.get('region')}")
    print(f"  Model: {claude_config.get('model')}")
    
    gemini_config = loader.get_llm_config('gemini')
    print(f"\nGemini Config:")
    print(f"  Model: {gemini_config.get('model')}")
    
    print(f"\n=== App Configuration ===")
    print(f"Default Language: {loader.get_default_language()}")
    print(f"Supported Languages: {loader.get_supported_languages()}")
    print(f"Database Path: {loader.get('app.database.path')}")
    
    print(f"\n=== Parameter Presets ===")
    balanced = loader.get_parameter_preset('balanced')
    print(f"Balanced: {balanced}")
    
    creative = loader.get_parameter_preset('creative')
    print(f"Creative: {creative}")
    
    print(f"\n=== Secrets (from .env) ===")
    aws_key = loader.get_secret('AWS_ACCESS_KEY_ID')
    if aws_key:
        print(f"AWS_ACCESS_KEY_ID: {aws_key[:10]}... (masked)")
    else:
        print("AWS_ACCESS_KEY_ID: Not set")
    
    gemini_key = loader.get_secret('GEMINI_API_KEY')
    if gemini_key:
        print(f"GEMINI_API_KEY: {gemini_key[:10]}... (masked)")
    else:
        print("GEMINI_API_KEY: Not set")
    
    print("\nTest completed!")
