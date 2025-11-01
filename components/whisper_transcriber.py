import whisper

class WhisperTranscriber:
    """
    Audio transcription service for voice-based UX evaluations.
    
    This class provides speech-to-text capabilities using OpenAI's Whisper model,
    enabling personas to process and respond to audio-based evaluation materials.
    
    Key Responsibilities:
    - Transcribe audio files to text for persona processing
    - Support multiple audio formats and quality levels
    - Provide accurate transcription for accessibility evaluations
    - Enable voice-based user feedback analysis
    
    Features:
    - Multiple Whisper model sizes (tiny, small, medium, large)
    - Support for various audio formats (wav, mp3, m4a, etc.)
    - Language detection and multilingual transcription
    - Optimized for evaluation scenario audio content
    
    Usage in Evaluation:
    - Convert user voice feedback to text for analysis
    - Process audio-based evaluation materials
    - Support accessibility testing with voice interactions
    - Enable multilingual evaluation scenarios
    """
    _default_instance = None

    def __init__(self, model_name='small'):
        self.model = whisper.load_model(model_name)

    @staticmethod
    def defaultTranscriber():
        """Returns a default instance of the WhisperTranscriber."""
        if WhisperTranscriber._default_instance is None:
            WhisperTranscriber._default_instance = WhisperTranscriber("small")
        return WhisperTranscriber._default_instance

    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result['text']
