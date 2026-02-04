import os
import time
from config import Config
try:
    from groq import Groq
except ImportError:
    Groq = None
try:
    import openai
except ImportError:
    openai = None

class STTHandler:
    """Handles Speech-to-Text conversion using Groq Whisper or OpenAI Whisper"""
    
    def __init__(self):
        # Initialize Groq
        self.groq_client = None
        if Config.GROQ_API_KEY and Groq:
            self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        else:
            print("Warning: GROQ_API_KEY not found or SDK missing.")

        # Initialize OpenAI
        self.openai_client = None
        if Config.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            print("Warning: OPENAI_API_KEY not found or SDK missing.")
            
        # Pricing (approximate for estimation)
        self.cost_per_minute_groq = 0.00185 # $0.111 per hour
        self.cost_per_minute_openai = 0.006 # $0.006 per minute (Whisper)
    
    def transcribe_audio(self, audio_file_path, model_service="groq", language=None, translate=False):
        """
        Transcribe audio file to text using specified service
        
        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)
            model_service: "groq" or "openai"
        
        Returns:
            dict: {text, duration_seconds, cost, confidence, language}
        """
        start_time = time.time()
        
        # Fallback if requested service is not available
        if model_service == "openai" and not self.openai_client:
            print("OpenAI client not ready, falling back to Groq")
            model_service = "groq"
        
        if model_service == "groq" and not self.groq_client:
             return {
                "text": "",
                "error": "No STT service available (Keys missing)",
                "duration_seconds": 0,
                "cost": 0
            }

        try:
            text = ""
            duration_seconds = 0
            cost = 0
            
            with open(audio_file_path, 'rb') as file:
                # File size for fallback duration
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                if model_service == "openai":
                    # OpenAI Whisper
                    kwargs = {
                        "model": "whisper-1",
                        "file": file,
                        "response_format": "verbose_json",
                    }
                    if language:
                        kwargs["language"] = language
                    if translate:
                        kwargs["task"] = "translate"
                    transcription = self.openai_client.audio.transcriptions.create(**kwargs)
                    text = transcription.text
                    duration_seconds = getattr(transcription, 'duration', 0)
                    cost = (duration_seconds / 60.0) * self.cost_per_minute_openai

                else:
# Groq Whisper (Default)
                    kwargs = {
                        "file": (os.path.basename(audio_file_path), file.read()),
                        "model": "whisper-large-v3",
                        "response_format": "verbose_json",
                    }
                    if language:
                        kwargs["language"] = language
                    if translate:
                        kwargs["task"] = "translate"
                    if language == "bn":
                        kwargs["prompt"] = "বাংলা ভাষা"
                    try:
                        transcription = self.groq_client.audio.transcriptions.create(**kwargs)
                    except TypeError:
                        # Retry without language if SDK doesn't support it
                        kwargs.pop("language", None)
                        kwargs.pop("task", None)
                        kwargs.pop("prompt", None)
                        transcription = self.groq_client.audio.transcriptions.create(**kwargs)
                    text = transcription.text
                    duration_seconds = getattr(transcription, 'duration', 0)
                    cost = (duration_seconds / 60.0) * self.cost_per_minute_groq
            
            # Fallback duration calculation
            if duration_seconds == 0:
                duration_seconds = self._estimate_duration(file_size)
                if cost == 0: # Recalculate cost if it was dependent on 0 duration
                     rate = self.cost_per_minute_openai if model_service == "openai" else self.cost_per_minute_groq
                     cost = (duration_seconds / 60.0) * rate

            return {
                "text": text,
                "duration_seconds": round(duration_seconds, 2),
                "cost": round(cost, 6),
                "language": getattr(transcription, "language", None),
                "service": model_service,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"STT Error ({model_service}): {e}")
            return {
                "text": "",
                "error": str(e),
                "duration_seconds": 0,
                "cost": 0
            }
    
    def _estimate_duration(self, file_size_bytes):
        """Estimate audio duration from file size (rough approximation for 128kbps mp3/wav)"""
        # 16KB per second ~ 128kbps
        return file_size_bytes / 16000
