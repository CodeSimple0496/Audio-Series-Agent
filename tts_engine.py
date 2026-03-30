import edge_tts
import asyncio
import time

VOICE_MODELS = {
    "Male": "hi-IN-MadhurNeural",
    "Sweet Female": "hi-IN-SwaraNeural",
    "Tense Male": "hi-IN-MadhurNeural"
}

async def _generate_audio_async(text, voice_type, output_path, max_retries=3):
    """Asynchronous generation with error handling and retry logic."""
    if not text or not text.strip():
        print("Skipping empty text chunk.")
        return False
        
    voice = VOICE_MODELS.get(voice_type, "hi-IN-MadhurNeural")
    
    rate = "+0%"
    pitch = "+0Hz"
    
    if voice_type == "Tense Male":
        rate = "+10%"
        pitch = "-10Hz"
        
    # Retry mechanism for network or service-side issues
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            return True # Success
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"TTS attempt {attempt+1} failed: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                print(f"TTS failed after {max_retries} attempts: {e}")
                raise e

def generate_audio(text, voice_type, output_path):
    """Synchronous wrapper to generate audio via edge-tts."""
    try:
        success = asyncio.run(_generate_audio_async(text, voice_type, output_path))
        return output_path if success else None
    except Exception as e:
        print(f"Final TTS generation failed: {e}")
        return None

