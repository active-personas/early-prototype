from openai import OpenAI
from .logger import Logger

class LLMClient:
    """
    Large Language Model Client for AI-powered evaluations.
    
    This class provides a unified interface for interacting with various LLM providers
    (OpenAI, Anthropic, local models) during persona-based UX evaluations.
    
    Key Responsibilities:
    - Manage LLM API connections and authentication
    - Handle multi-modal message formatting (text, images)
    - Execute model inference with configurable parameters
    - Provide consistent interface across different LLM providers
    
    Features:
    - Support for OpenAI-compatible APIs
    - Configurable temperature and streaming options
    - Multi-modal input processing for image-based evaluations
    - Error handling and response validation
    
    Usage in Evaluation:
    - Powers persona responses during UX assessments
    - Processes evaluation prompts and generates insights
    - Handles complex reasoning tasks for usability analysis
    """
    def __init__(self, base_url: str, api_key: str, model_name: str, temperature=1.0, stream=False):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.stream = stream
        
        Logger.debug(f"Initializing LLMClient with model: {model_name}")
        Logger.debug(f"Base URL: {base_url}")
        Logger.debug(f"Temperature: {temperature}, Stream: {stream}")
        
        try:
            self.client = OpenAI(
                base_url = self.base_url,
                api_key = self.api_key,
            )
            Logger.info(f"LLMClient successfully initialized for model: {model_name}")
        except Exception as e:
            Logger.error(f"Failed to initialize LLMClient for model {model_name}: {str(e)}")
            raise

    def get_model_name(self):
        return self.model_name

    def invoke(self, messages):
        """
        Invoke the LLM with the provided messages.
        
        Args:
            messages: List of message dictionaries containing conversation history
            
        Returns:
            str: Response content from the LLM
        """
        Logger.debug(f"Invoking LLM {self.model_name} with {len(messages)} messages")
        
        try:
            extra_headers = {
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            }

            completion = self.client.chat.completions.create(
                extra_headers = extra_headers,
                model = self.model_name,
                stream = self.stream,
                temperature = self.temperature,
                messages = messages
            )

            content = completion.choices[0].message.content
            
            Logger.debug(f"LLM {self.model_name} response received successfully")
            Logger.debug(f"Response length: {len(content)} characters")
            
            return content
            
        except Exception as e:
            Logger.error(f"LLM {self.model_name} invocation failed: {str(e)}")
            Logger.error(f"Request details - Temperature: {self.temperature}, Stream: {self.stream}")
            raise
