"""LLM Manager Module"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .config import LLMConfig, LLMProvider, create_llm_config
from .client import LLMClient
from .prompts import PromptManager


class LLMManager:
    """LLM Manager for handling multiple LLM configurations and clients"""
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        self.config_path = Path(config_path)
        self.configs: Dict[str, LLMConfig] = {}
        self.clients: Dict[str, LLMClient] = {}
        self.prompt_manager = PromptManager()
        self.provider_info = {}
        
        self._load_configurations()
        logger.info("LLM Manager initialized")
    
    def _load_configurations(self):
        """Load LLM configurations from YAML file"""
        if not self.config_path.exists():
            logger.warning(f"Configuration file not found: {self.config_path}")
            self._create_default_configs()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Load provider information
            self.provider_info = config_data.get("providers", {})
            
            # Load default configuration
            default_config = config_data.get("default", {})
            self.configs["default"] = self._create_config_with_env(default_config)
            
            # Load agent-specific configurations
            agents_config = config_data.get("agents", {})
            for agent_name, agent_config in agents_config.items():
                # Merge with default config
                merged_config = {**default_config, **agent_config}
                self.configs[agent_name] = self._create_config_with_env(merged_config)
            
            logger.info(f"Loaded {len(self.configs)} LLM configurations")
            
            # Log detected API keys
            self._log_detected_api_keys()
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            self._create_default_configs()
    
    def _create_config_with_env(self, config_dict: Dict[str, Any]) -> LLMConfig:
        """TODO: Add docstring."""
        provider = config_dict.get("provider", "qwen")
        
        # API
        api_key = self._detect_api_key(provider)
        if api_key:
            config_dict["api_key"] = api_key
        
        # base_url
        base_url = self._detect_base_url(provider)
        if base_url:
            config_dict["base_url"] = base_url
        
        return LLMConfig(**config_dict)
    
    def _detect_api_key(self, provider: str) -> Optional[str]:
        """Detect API key for a specific provider from environment variables"""
        # Define environment variable names for each provider
        env_keys = []
        
        # Map provider to environment variable names
        if provider == "openai":
            env_keys = ["OPENAI_API_KEY", "LLM_API_KEY"]
        elif provider == "azure_openai":
            env_keys = ["AZURE_OPENAI_API_KEY", "LLM_API_KEY"]
        elif provider == "anthropic":
            env_keys = ["ANTHROPIC_API_KEY", "LLM_API_KEY"]
        elif provider == "zhipu":
            env_keys = ["ZHIPU_API_KEY", "LLM_API_KEY"]
        elif provider == "qwen":
            env_keys = ["DASHSCOPE_API_KEY", "QWEN_API_KEY", "LLM_API_KEY"]
        elif provider == "deepseek":
            env_keys = ["DEEPSEEK_API_KEY", "LLM_API_KEY"]
        elif provider == "ollama":
            return None  # Ollama doesn't require an API key
        else:
            env_keys = ["LLM_API_KEY"]
        
        # Try to find API key from environment
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        return None
    
    def _detect_base_url(self, provider: str) -> Optional[str]:
        """Detect base URL for a specific provider"""
        # Check for custom base URL in environment
        base_url = os.getenv("LLM_BASE_URL")
        if base_url:
            return base_url
        
        # Use default URLs for each provider
        default_urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "ollama": "http://localhost:11434/v1"
        }
        
        return default_urls.get(provider)
    
    def _log_detected_api_keys(self):
        """Log which API keys were detected in environment"""
        detected_keys = []
        
        env_vars = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("ZHIPU_API_KEY", "Zhipu AI"),
            ("DASHSCOPE_API_KEY", "Qwen/DashScope"),
            ("QWEN_API_KEY", "Qwen"),
            ("DEEPSEEK_API_KEY", "DeepSeek"),
            ("LLM_API_KEY", "Generic LLM")
        ]
        
        for env_key, provider_name in env_vars:
            if os.getenv(env_key):
                detected_keys.append(f"{provider_name}({env_key})")
        
        if detected_keys:
            logger.info(f"Detected API keys: {', '.join(detected_keys)}")
        else:
            logger.warning("No API keys detected in environment")
    
    def _create_default_configs(self):
        """Create default configurations when no config file exists"""
        # Detect best available provider
        best_provider = self._detect_best_provider()

        # Get default parameters from environment
        default_temperature = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7"))
        default_max_tokens = int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "4000"))

        # Get API key
        api_key = self._detect_api_key(best_provider)
        if not api_key and best_provider != "ollama":
            logger.warning(f"No API key found for {best_provider}")

        # Get base_url
        base_url = self._detect_base_url(best_provider)

        # Create default configuration
        self.configs["default"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=default_temperature,
            max_tokens=default_max_tokens
        )

        # Create agent-specific configurations
        self.configs["query_optimizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=0.3,
            max_tokens=2000
        )

        self.configs["search_analyzer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=0.5,
            max_tokens=4000
        )

        self.configs["content_synthesizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=default_temperature,
            max_tokens=6000
        )

        logger.info(f"Default provider: {best_provider}, Model: {self._get_default_model(best_provider)}, API Key: {'configured' if api_key else 'not configured'}")
    
    def _detect_best_provider(self) -> str:
        """Detect the best available LLM provider based on environment variables"""
        # Check for explicit provider preference
        default_provider = os.getenv("DEFAULT_LLM_PROVIDER")
        if default_provider:
            # Verify API key is available for non-Ollama providers
            provider_env_keys = {
                "qwen": ["DASHSCOPE_API_KEY", "QWEN_API_KEY"],
                "deepseek": ["DEEPSEEK_API_KEY"],
                "zhipu": ["ZHIPU_API_KEY"],
                "openai": ["OPENAI_API_KEY"],
                "anthropic": ["ANTHROPIC_API_KEY"],
                "ollama": []  # Ollama doesn't need API key
            }

            env_keys = provider_env_keys.get(default_provider, [])

            # If ollama or if API key is available, use the specified provider
            if not env_keys or any(os.getenv(key) for key in env_keys):
                logger.info(f"Using specified provider: {default_provider}")
                return default_provider
            else:
                logger.warning(f"Specified provider {default_provider} but no API key found")

        # Auto-detect based on available API keys (priority order)
        # OpenAI is prioritized as the default provider
        providers_priority = [
            ("openai", ["OPENAI_API_KEY"]),
            ("anthropic", ["ANTHROPIC_API_KEY"]),
            ("deepseek", ["DEEPSEEK_API_KEY"]),
            ("qwen", ["DASHSCOPE_API_KEY", "QWEN_API_KEY"]),
            ("zhipu", ["ZHIPU_API_KEY"]),
            ("ollama", [])  # Ollama doesn't need API key
        ]

        # Check for generic LLM_API_KEY
        if os.getenv("LLM_API_KEY"):
            return "openai"  # Use OpenAI as default for generic key

        # Find first available provider with API key
        for provider, env_keys in providers_priority:
            if not env_keys:  # Ollama case
                continue

            for env_key in env_keys:
                if os.getenv(env_key):
                    logger.info(f"Auto-detected provider: {provider}")
                    return provider

        # Fall back to Ollama if no API keys found
        logger.warning("No API keys found, falling back to Ollama")
        return "ollama"
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model name for a provider"""
        # Check for explicit model preference
        env_model = os.getenv("DEFAULT_LLM_MODEL")
        if env_model:
            logger.info(f"Using specified model: {env_model}")
            return env_model

        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-sonnet-20250229",
            "zhipu": "glm-4",
            "qwen": "qwen-turbo",
            "deepseek": "deepseek-chat",
            "ollama": "llama3"
        }

        # Default to OpenAI's gpt-4o-mini if provider not found
        return default_models.get(provider, "gpt-4o-mini")
    
    def get_client(self, config_name: str = "default") -> LLMClient:
        """Get or create an LLM client for the specified configuration"""
        if config_name not in self.clients:
            if config_name not in self.configs:
                logger.warning(f"Configuration not found: {config_name}, using default")
                config_name = "default"
            
            config = self.configs[config_name]
            self.clients[config_name] = LLMClient(config)
        
        return self.clients[config_name]
    
    def get_config(self, config_name: str = "default") -> LLMConfig:
        """Get LLM configuration by name"""
        if config_name not in self.configs:
            logger.warning(f"Configuration not found: {config_name}, using default")
            config_name = "default"
        
        return self.configs[config_name]
    
    def get_all_configs(self) -> Dict[str, LLMConfig]:
        """TODO: Add docstring."""
        return self.configs.copy()
    
    def add_config(self, name: str, config: LLMConfig):
        """Add a new LLM configuration"""
        self.configs[name] = config
        # Clear cached client if exists
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"Added configuration: {name}")
    
    def update_config(self, name: str, **kwargs):
        """Update an existing LLM configuration"""
        if name not in self.configs:
            raise KeyError(f"Configuration not found: {name}")
        
        # Get current configuration
        current_config = self.configs[name]
        config_dict = current_config.model_dump()
        
        # Update with new values
        config_dict.update(kwargs)
        
        # Create new configuration
        self.configs[name] = LLMConfig(**config_dict)
        
        # Clear cached client
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"Updated configuration: {name}")
    
    def remove_config(self, name: str):
        """Remove an LLM configuration"""
        if name == "default":
            raise ValueError("Cannot remove default configuration")
        
        if name in self.configs:
            del self.configs[name]
        
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"Removed configuration: {name}")
    
    def get_prompt_manager(self) -> PromptManager:
        """TODO: Add docstring."""
        return self.prompt_manager
    
    def reload_prompts(self):
        """Reload all prompts from disk"""
        self.prompt_manager.reload_prompts()
        logger.info("Prompts reloaded successfully")
    
    def test_connection(self, config_name: str = "default") -> bool:
        """Test connection for a specific LLM configuration"""
        try:
            client = self.get_client(config_name)
            # Run async test in sync context
            import asyncio
            
            async def test():
                return await client.test_connection()
            
            result = asyncio.run(test())
            logger.info(f"Connection test for {config_name}: {'success' if result else 'failed'}")
            return result
            
        except Exception as e:
            logger.error(f"Connection test failed for {config_name}: {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available LLM providers"""
        available = {}
        
        for provider in LLMProvider:
            provider_name = provider.value
            api_key = self._detect_api_key(provider_name)
            base_url = self._detect_base_url(provider_name)
            
            available[provider_name] = {
                "has_api_key": api_key is not None,
                "base_url": base_url,
                "default_model": self._get_default_model(provider_name),
                "status": "available" if api_key or provider_name == "ollama" else "missing API key"
            }
        
        return available
    
    def get_manager_info(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "config_path": str(self.config_path),
            "total_configs": len(self.configs),
            "active_clients": len(self.clients),
            "available_configs": list(self.configs.keys()),
            "available_providers": self.get_available_providers(),
            "prompt_manager_info": {
                "prompts_count": len(self.prompt_manager.list_prompts()),
                "prompts_dir": str(self.prompt_manager.prompts_dir)
            }
        }


# Global LLM manager instance
llm_manager = LLMManager()