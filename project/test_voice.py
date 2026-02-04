#!/usr/bin/env python3
import requests
import tempfile
import wave
import numpy as np

def create_test_audio():
    """Create a simple test WAV file"""
    # Generate a simple sine wave
    sample_rate = 16000
    duration = 2  # seconds
    frequency = 440  # Hz (A4 note)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    
    # Create WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return temp_file.name

def test_voice_api():
    """Test voice transcription API"""
    print("Creating test audio...")
    audio_file = create_test_audio()
    print(f"Test audio created: {audio_file}")
    
    try:
        print("Testing voice transcription...")
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post('http://localhost:5000/api/voice/transcribe', 
                                 files=files)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        import os
        os.unlink(audio_file)
        print("Test audio cleaned up")

if __name__ == "__main__":
    test_voice_api()