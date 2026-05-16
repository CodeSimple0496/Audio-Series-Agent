import edge_tts
import asyncio
import time
import aiohttp
import os

EDGE_VOICE_MODELS = {
    "Male": "hi-IN-MadhurNeural",
    "Sweet Female": "hi-IN-SwaraNeural",
    "Tense Male": "hi-IN-MadhurNeural",
    "Relaxed Male": "hi-IN-MadhurNeural",
    "Relaxed Female": "hi-IN-SwaraNeural"
}

ELEVENLABS_VOICES = {
    "Adam (Deep Male)": "pNInz6obpgDQGcFmaJgB",
    "Rachel (Soft Female)": "21m00Tcm4TlvDq8ikWAM",
    "Antony (Expressive)": "ErXwobaYiN019PkySvjV",
    "Bella (Bright Female)": "EXAVITQu4vr4xnSDxMaL"
}

OPENAI_VOICES = {
    "Alloy (Neutral)": "alloy",
    "Echo (Warm Male)": "echo",
    "Onyx (Deep Male)": "onyx",
    "Nova (Bright Female)": "nova"
}

async def _generate_edge_tts(text, voice_type, output_path, max_retries=3):
    voice = EDGE_VOICE_MODELS.get(voice_type, "hi-IN-MadhurNeural")
    rate = "+0%"
    pitch = "+0Hz"
    
    if voice_type == "Tense Male":
        rate = "+10%"
        pitch = "-10Hz"
    elif "Relaxed" in voice_type:
        rate = "-15%"
        pitch = "-10Hz"
        
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                print(f"Edge TTS failed: {e}")
                raise e

async def _generate_elevenlabs(text, voice_type, api_key, output_path, max_retries=3):
    if not api_key:
        raise ValueError("ElevenLabs API Key is missing. Please enter it in the sidebar.")
    voice_id = ELEVENLABS_VOICES.get(voice_type, "pNInz6obpgDQGcFmaJgB")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return True
                    else:
                        error_text = await response.text()
                        if response.status == 401:
                            raise ValueError("Invalid ElevenLabs API Key.")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                        else:
                            raise Exception(f"ElevenLabs API Error: {error_text}")
        except Exception as e:
            if attempt < max_retries - 1 and "Invalid" not in str(e):
                await asyncio.sleep(2)
            else:
                raise e

async def _generate_openai(text, voice_type, api_key, output_path, max_retries=3):
    if not api_key:
        raise ValueError("OpenAI API Key is missing. Please enter it in the sidebar.")
    voice = OPENAI_VOICES.get(voice_type, "alloy")
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": voice
    }
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return True
                    else:
                        error_text = await response.text()
                        if response.status == 401:
                            raise ValueError("Invalid OpenAI API Key.")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                        else:
                            raise Exception(f"OpenAI API Error: {error_text}")
        except Exception as e:
            if attempt < max_retries - 1 and "Invalid" not in str(e):
                await asyncio.sleep(2)
            else:
                raise e

async def _generate_audio_async(text, voice_type, engine, api_key, output_path):
    if not text or not text.strip():
        print("Skipping empty text chunk.")
        return False
        
    if "ElevenLabs" in engine:
        return await _generate_elevenlabs(text, voice_type, api_key, output_path)
    elif "OpenAI" in engine:
        return await _generate_openai(text, voice_type, api_key, output_path)
    else:
        return await _generate_edge_tts(text, voice_type, output_path)

def generate_audio(text, voice_type, engine, api_key, output_path):
    try:
        success = asyncio.run(_generate_audio_async(text, voice_type, engine, api_key, output_path))
        return output_path if success else None
    except Exception as e:
        print(f"Final TTS generation failed: {e}")
        return None
