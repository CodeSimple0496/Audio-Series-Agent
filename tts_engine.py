import edge_tts
import asyncio

VOICE_MODELS = {
    "Male": "hi-IN-MadhurNeural",
    "Sweet Female": "hi-IN-SwaraNeural",
    "Tense Male": "hi-IN-MadhurNeural"
}

async def _generate_audio_async(text, voice_type, output_path):
    # Select voice, defaulting to Madhur Neural
    voice = VOICE_MODELS.get(voice_type, "hi-IN-MadhurNeural")
    
    rate = "+0%"
    pitch = "+0Hz"
    
    # Simple heuristic for a tense mood
    if voice_type == "Tense Male":
        rate = "+10%"
        pitch = "-10Hz"
        
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def generate_audio(text, voice_type, output_path):
    """Synchronous wrapper to generate audio via edge-tts."""
    try:
        asyncio.run(_generate_audio_async(text, voice_type, output_path))
        return output_path
    except Exception as e:
        print(f"TTS generation failed for text chunk: {e}")
        return None
