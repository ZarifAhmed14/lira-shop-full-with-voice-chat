import os
import time
from stt_handler import STTHandler
from tts_handler import TTSHandler
from config import Config

def test_voice_integration():
    print("=== Testing Voice Integration (Multi-Provider) ===\n")
    
    # 1. Test TTS (Text-to-Speech)
    print("--- TTS Testing ---")
    tts = TTSHandler()
    test_text = "Hello! This is a test of the Lira Voice System."
    
    # Edge TTS (Free)
    print("\n1. Testing Edge TTS (Free)...")
    res_edge = tts.synthesize_speech(test_text, output_path="test_edge.mp3", model_service="edge-tts")
    if res_edge["success"]:
        print(f"✅ Edge TTS Success: {res_edge['audio_path']} (Cost: ${res_edge['cost']})")
    else:
        print(f"❌ Edge TTS Failed: {res_edge.get('error')}")

    # OpenAI TTS (Paid)
    print("\n2. Testing OpenAI TTS (Paid)...")
    if Config.OPENAI_API_KEY:
        res_openai = tts.synthesize_speech(test_text, output_path="test_openai.mp3", model_service="openai")
        if res_openai["success"]:
            print(f"✅ OpenAI TTS Success: {res_openai['audio_path']} (Cost: ${res_openai['cost']})")
        else:
            print(f"❌ OpenAI TTS Failed: {res_openai.get('error')}")
    else:
        print("⚠️ OpenAI API Key not found, skipping OpenAI TTS test.")

    # 2. Test STT (Speech-to-Text)
    print("\n--- STT Testing ---")
    stt = STTHandler()
    
    # Use the generated audio for transcription test
    audio_file = "test_edge.mp3" if os.path.exists("test_edge.mp3") else None
    
    if not audio_file:
        print("❌ No audio file generated to test STT.")
        return

    # Groq STT (Free)
    print(f"\n3. Testing Groq STT (Free) with {audio_file}...")
    if Config.GROQ_API_KEY:
        res_groq = stt.transcribe_audio(audio_file, model_service="groq")
        if not res_groq.get("error"):
            print(f"✅ Groq STT Success: '{res_groq['text']}' (Cost: ${res_groq['cost']})")
        else:
            print(f"❌ Groq STT Failed: {res_groq.get('error')}")
    else:
         print("⚠️ Groq API Key not found, skipping Groq STT test.")

    # OpenAI STT (Paid)
    print(f"\n4. Testing OpenAI STT (Paid) with {audio_file}...")
    if Config.OPENAI_API_KEY:
        res_openai_stt = stt.transcribe_audio(audio_file, model_service="openai")
        if not res_openai_stt.get("error"):
            print(f"✅ OpenAI STT Success: '{res_openai_stt['text']}' (Cost: ${res_openai_stt['cost']})")
        else:
            print(f"❌ OpenAI STT Failed: {res_openai_stt.get('error')}")
    else:
        print("⚠️ OpenAI API Key not found, skipping OpenAI STT test.")

    print("\n=== Test Complete ===")
    
    # Cleanup
    try:
        if os.path.exists("test_edge.mp3"): os.remove("test_edge.mp3")
        if os.path.exists("test_openai.mp3"): os.remove("test_openai.mp3")
    except:
        pass

if __name__ == "__main__":
    test_voice_integration()
