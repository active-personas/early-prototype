import base64
from .llm_client import LLMClient
from .logger import Logger

class ActivePersona:
    """
    AI Persona for User Experience Evaluation.
    
    This class represents an AI-powered persona that simulates user behavior and 
    provides feedback during UX evaluations. It combines LLM capabilities with 
    domain-specific persona characteristics to generate realistic user insights.
    
    Key Responsibilities:
    - Embody specific user characteristics and behaviors
    - Interact with evaluation materials (text, images, audio)
    - Generate persona-driven responses to evaluation questions
    - Maintain conversation context across evaluation sessions
    
    Capabilities:
    - Multi-modal input processing (text, images, audio)
    - Template-based persona definition for consistency
    - Integration with various LLM providers via LLMClient
    - Audio transcription for voice-based evaluations
    
    Usage in Evaluation:
    - Provides human-like perspectives on interface designs
    - Simulates diverse user demographics and abilities
    - Generates qualitative feedback for usability analysis
    """
    def __init__(
            self, 
            name: str, 
            llm_client: LLMClient, 
            system_prompt: str = None
        ):
        self.name = name
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.message_history = []    
        self.reset_history()
        Logger.debug(f"ActivePersona '{name}' initialized with model '{llm_client.get_model_name()}'")
    
    def get_complete_name(self):
        return f"{self.name}_{self.llm_client.get_model_name()}"
    def get_system_prompt(self):
        return self.system_prompt

    def reset_history(self):
        """
        Reset the message history for the persona.
        """
        self.message_history = []
                
        # Add persona description to the message history
        self.message_history.append({
            "role": "system", 
            "content": self.system_prompt
        })
        Logger.debug(f"Message history reset for persona '{self.name}'")

    def interact(self, messages):
        """
        Interact with the persona using messages.
        
        Args:
            messages: A single message or array of messages.
                     Each message can be:
                     - Simple text string
                     - Dict with 'type': 'text' and 'text': content
                     - Dict with 'type': 'image' and 'path': image_file_path
                     - Dict with 'type': 'audio' and 'path': audio_file_path
        
        Returns:
            Response from the LLM
        """
        # Normalize to list if single message
        if not isinstance(messages, list):
            messages = [messages]
        
        processed_messages = []
        
        for message in messages:
            if isinstance(message, str):
                # Simple text message
                processed_messages.append({"type": "text", "text": message})
                Logger.debug(f"Processing text message for persona '{self.name}'")

            elif isinstance(message, dict):
                if message.get("type") == "text":
                    processed_messages.append(message)
                    Logger.debug(f"Processing text message for persona '{self.name}'")

                elif message.get("type") == "image":
                    # Convert image to base64
                    image_path = message["path"]
                    try:
                        with open(image_path, 'rb') as img_file:
                            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

                        processed_messages.append({
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                        })
                        Logger.debug(f"Processing image message for persona '{self.name}': {image_path}")
                    except FileNotFoundError:
                        Logger.error(f"Image file not found for persona '{self.name}': {image_path}")
                        raise
                    except Exception as e:
                        Logger.error(f"Error processing image for persona '{self.name}': {e}")
                        raise

                elif message.get("type") == "audio":
                    # Transcribe audio to text
                    audio_path = message["path"]
                    try:
                        transcription = self.whisper_transcriber.transcribe(audio_path)
                        processed_messages.append({"type": "text", "text": transcription})
                        Logger.debug(f"Processing audio message for persona '{self.name}': {audio_path}")
                    except Exception as e:
                        Logger.error(f"Error processing audio for persona '{self.name}': {e}")
                        raise
        
        # Create user message and add to history
        user_msg = {"role": "user", "content": processed_messages}
        self.message_history.append(user_msg)
        
        # Send complete message history to LLM
        Logger.debug(f"Sending request to LLM for persona '{self.name}'")
        try:
            response = self.llm_client.invoke(self.message_history)
            Logger.debug(f"Received response from LLM for persona '{self.name}'")
        except Exception as e:
            Logger.error(f"LLM request failed for persona '{self.name}': {e}")
            raise
        
        # Add assistant response to history
        self.message_history.append({"role": "assistant", "content": response})
        
        return response
    
    def print_message_history(self):
        """
        Print the contents of the message history in a readable format.
        """
        Logger.info("=== Message History ===")
        for i, message in enumerate(self.message_history, 1):
            role = message["role"].upper()
            content = message["content"]
            
            Logger.info(f"{i}. {role}:")
            if isinstance(content, str):
                Logger.info(f"   {content}")

            elif isinstance(content, list):
                for j, item in enumerate(content):
                    if item.get("type") == "text":
                        Logger.info(f"   Text: {item['text']}")

                    elif item.get("type") == "image_url":
                        Logger.info(f"   Image: [Base64 encoded image]")

                    else:
                        Logger.info(f"   {item}")

            else:
                Logger.info(f"   {content}")

        Logger.info("=" * 23)
