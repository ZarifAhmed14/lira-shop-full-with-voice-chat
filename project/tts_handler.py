# Using Edge TTS (neural), Google TTS (fallback), and OpenAI TTS

import asyncio
import os
import time
from config import Config
try:
    import openai
except ImportError:
    openai = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

class TTSHandler:
    """Handles Text-to-Speech conversion using Edge TTS, Google TTS, or OpenAI TTS"""

    def __init__(self):
        # Edge TTS is FREE (neural voices)
        self.cost_per_character_edge = 0.0
        # Google TTS fallback (free)
        self.cost_per_character_gtts = 0.0

        # OpenAI TTS
        self.openai_client = None
        if Config.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

        # Pricing: $0.015 per 1K characters (standard) = $0.000015 per char
        self.cost_per_character_openai = 0.000015

        # Default neural voices
        self.default_voice_en = "en-US-JennyNeural"
        self.default_voice_bn = "bn-BD-NabanitaNeural"

    def _detect_language(self, text: str) -> str:
        return "bn" if any('\u0980' <= char <= '\u09ff' for char in text) else "en"

    def _resolve_voice(self, text: str, voice: str | None) -> str:
        if voice:
            return voice
        lang = self._detect_language(text)
        return self.default_voice_bn if lang == "bn" else self.default_voice_en

    def _run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Run in a new event loop to avoid 'already running' errors
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        return asyncio.run(coro)

    async def _synthesize_edge_tts(self, text: str, output_path: str, voice: str):
        # Use built-in rate/pitch controls to avoid SSML being read aloud
        communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="+2Hz")
        await communicate.save(output_path)

    def synthesize_speech(self, text, output_path="response.mp3", voice=None, model_service="edge-tts"):
        """
        Convert text to speech using specified service

        Args:
            text: Text to convert
            output_path: Where to save audio file
            voice: Voice model (Edge/OpenAI)
            model_service: "edge-tts", "gtts" or "openai"

        Returns:
            dict: {audio_path, character_count, cost, duration}
        """
        start_time = time.time()

        # Fallback if OpenAI requested but not available
        if model_service == "openai" and not self.openai_client:
            print("OpenAI client not ready, falling back to Edge TTS")
            model_service = "edge-tts"

        # Fallback if Edge TTS requested but not available
        if model_service == "edge-tts" and not edge_tts:
            print("edge-tts not installed, falling back to Google TTS")
            model_service = "gtts"

        try:
            character_count = len(text)
            cost = 0

            if model_service == "openai":
                # OpenAI TTS
                selected_voice = voice if voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "nova"

                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=selected_voice,
                    input=text
                )
                response.stream_to_file(output_path)
                cost = character_count * self.cost_per_character_openai
                voice_used = selected_voice

            elif model_service == "edge-tts":
                # Edge TTS (Neural)
                selected_voice = self._resolve_voice(text, voice)
                try:
                    self._run_async(self._synthesize_edge_tts(text, output_path, selected_voice))
                    cost = character_count * self.cost_per_character_edge
                    voice_used = selected_voice
                except Exception as edge_error:
                    # If Edge TTS fails (e.g., 403), fall back to Google TTS
                    print(f"Edge TTS failed ({edge_error}), falling back to Google TTS")
                    lang = self._detect_language(text)
                    if not gTTS:
                        raise Exception("gTTS not installed. Run: pip install gTTS")
                    tts = gTTS(text=text, lang=lang, slow=False)
                    tts.save(output_path)
                    cost = character_count * self.cost_per_character_gtts
                    voice_used = "Google TTS"

            else:
                # Google TTS (Fallback)
                lang = self._detect_language(text)
                print(f"Generating Google TTS with lang: {lang}")

                if not gTTS:
                    raise Exception("gTTS not installed. Run: pip install gTTS")

                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(output_path)
                cost = character_count * self.cost_per_character_gtts
                voice_used = "Google TTS"

            # Verify file was created
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception(f"TTS file not created or is empty: {output_path}")

            return {
                "audio_path": output_path,
                "character_count": character_count,
                "cost": cost,
                "voice_used": voice_used,
                "service": model_service,
                "processing_time": time.time() - start_time,
                "success": True
            }

        except Exception as e:
            error_msg = str(e)
            print(f"TTS Error: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "audio_path": None,
                "error": error_msg,
                "cost": 0,
                "success": False
            }

    def get_available_voices(self):
        """Get list of available voices"""
        return [
            {"id": "bn-BD-NabanitaNeural", "name": "Nabanita (Bangla)", "gender": "Female", "locale": "bn-BD", "service": "edge-tts"},
            {"id": "bn-BD-PradeepNeural", "name": "Pradeep (Bangla)", "gender": "Male", "locale": "bn-BD", "service": "edge-tts"},
            {"id": "en-US-JennyNeural", "name": "Jenny (English)", "gender": "Female", "locale": "en-US", "service": "edge-tts"},
            {"id": "gtts-en", "name": "Google TTS (English)", "gender": "Female", "locale": "en", "service": "gtts"},
            {"id": "gtts-bn", "name": "Google TTS (Bengali)", "gender": "Female", "locale": "bn", "service": "gtts"},
            {"id": "nova", "name": "Nova (OpenAI)", "gender": "Female", "locale": "en-US", "service": "openai"},
            {"id": "alloy", "name": "Alloy (OpenAI)", "gender": "Male", "locale": "en-US", "service": "openai"},
        ]
