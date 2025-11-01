import os
from .llm_client import LLMClient
from .logger import Logger

class LLMClientFactory:
    """
    Factory for creating configured LLM client instances.
    
    This factory class simplifies the creation of LLMClient instances by managing
    model-specific configurations and environment variables automatically.
    
    Key Responsibilities:
    - Centralize LLM configuration management
    - Map model names to appropriate API endpoints and settings
    - Handle environment variable resolution for API keys and URLs
    - Provide consistent client instantiation across the application
    
    Supported Models:
    - Qwen family (local/self-hosted models)
    - Claude models (Anthropic API)
    - OpenAI models (OpenAI API)
    - Custom model configurations
    
    Benefits:
    - Simplified model switching for comparative evaluations
    - Environment-specific configuration management
    - Consistent error handling and validation
    - Extensible design for new model providers
    """
    
    # Model name mappings to environment variable keys
    MODEL_CONFIGS = {
        'qwen': {
            'env_key': 'DEFAULT_MODEL',
            'default_value': 'qwen2.5vl:3b'
        },
        'claude': {
            'env_key': 'CLAUDE_MODEL',
            'default_value': 'anthropic/claude-sonnet-4'
        },
        'gemini': {
            'env_key': 'GEMINI_MODEL',
            'default_value': 'google/gemini-2.5-pro'
        },
        'llama': {
            'env_key': 'LLAMA_MODEL',
            'default_value': 'meta-llama/llama-4-maverick:free'
        },
        'openai': {
            'env_key': 'OPENAI_MODEL',
            'default_value': 'openai/gpt-5'
        }
    }
    
    @classmethod
    def create_client(cls, model_type: str, **kwargs) -> LLMClient:
        """
        Create an LLMClient instance based on the model type.
        
        Args:
            model_type (str): The type of model ('qwen2.5vl', 'claude-sonnet', 'gemini-pro', 'llama', 'gpt4')
            **kwargs: Additional parameters to override defaults
            
        Returns:
            LLMClient: Configured LLMClient instance
            
        Raises:
            ValueError: If model_type is not supported
        """
        Logger.debug(f"Creating LLM client for model type: {model_type}")
        
        if model_type not in cls.MODEL_CONFIGS:
            Logger.error(f"Unsupported model type: {model_type}. Supported types: {list(cls.MODEL_CONFIGS.keys())}")
            raise ValueError(f"Unsupported model type: {model_type}. "
                           f"Supported types: {list(cls.MODEL_CONFIGS.keys())}")
        
        config = cls.MODEL_CONFIGS[model_type]
        Logger.debug(f"Using config for {model_type}: {config}")
        
        # Default parameters
        default_params = {
            'base_url': os.getenv("BASE_URL", "https://openrouter.ai/api/v1"),
            'api_key': os.getenv("OPENAI_API_KEY"),
            'model_name': os.getenv(config['env_key'], config['default_value']),
            'temperature': float(os.getenv("MODEL_TEMPERATURE", "1.0")),
            'stream': os.getenv("MODEL_STREAM", "False").lower() == "true"
        }
        
        # Override with any provided kwargs
        default_params.update(kwargs)
        
        Logger.debug(f"LLM client parameters for {model_type}: {dict(default_params, api_key='***')}")  # Hide API key in logs
        
        try:
            client = LLMClient(**default_params)
            Logger.info(f"Successfully created LLM client for {model_type}")
            return client
        except Exception as e:
            Logger.error(f"Failed to create LLM client for {model_type}: {str(e)}")
            raise
    
    @classmethod
    def create_clients(cls, model_types: list) -> dict:
        """
        Create multiple LLMClient instances.
        
        Args:
            model_types (list): List of model types to create
            
        Returns:
            dict: Dictionary mapping model_type to LLMClient instance
        """
        Logger.info(f"Creating LLM clients for models: {model_types}")
        clients = {}
        
        for model_type in model_types:
            try:
                clients[model_type] = cls.create_client(model_type)
                Logger.debug(f"Successfully added client for {model_type}")
            except Exception as e:
                Logger.error(f"Failed to create client for {model_type}: {str(e)}")
                # Continue with other models even if one fails
                continue
        
        Logger.info(f"Successfully created {len(clients)} LLM clients out of {len(model_types)} requested")
        return clients
    
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available model types."""
        available_models = list(cls.MODEL_CONFIGS.keys())
        Logger.debug(f"Available models: {available_models}")
        return available_models
