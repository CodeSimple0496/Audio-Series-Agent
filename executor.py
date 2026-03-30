import os
import time
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from translator import split_into_chunks, translate_chunk, TRANSLATION_BLOCK_SIZE, TTS_CHUNK_SIZE
from tts_engine import generate_audio
from audio_processor import merge_audio_files

def generate_audio_series(script_text, voice_type="Male", bgm_path=None, output_file="final_audio.mp3", max_workers=25, progress_callback=None):

    """
    Two-Stage Orchestration for High Accuracy.
    Returns: (output_path, error_message)
    """
    start_time = time.time()
    temp_dir = "temp_audio_chunks"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
    except Exception as e:
        return None, f"Failed to initialize workspace: {e}"
    
    # --- STAGE 1: HIGH-ACCURACY CONTEXTUAL TRANSLATION ---
    if progress_callback: progress_callback(5, "Analyzing script context for high-accuracy translation...")
    
    context_blocks = split_into_chunks(script_text, max_chars=TRANSLATION_BLOCK_SIZE)
    total_blocks = len(context_blocks)
    
    if total_blocks == 0:
        return None, "The provided script is empty or could not be parsed into sections."
    
    if progress_callback: progress_callback(10, f"Translating {total_blocks} contextual blocks...")
    
    translated_script_parts = [None] * total_blocks
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(translate_chunk, block): i 
            for i, block in enumerate(context_blocks)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                translated_script_parts[idx] = future.result()
            except Exception as e:
                print(f"Block {idx} translation failed: {e}")
                translated_script_parts[idx] = context_blocks[idx] 
            
            if progress_callback:
                percent = 10 + int(((idx + 1) / total_blocks) * 40)
                progress_callback(percent, f"Contextual Translation: {idx+1}/{total_blocks} done...")

    full_hindi_script = " ".join([p for p in translated_script_parts if p])
    if not full_hindi_script.strip():
        return None, "Translation engine returned an empty script. Please check your internet connection."
    
    # --- STAGE 2: STABLE SMALL-CHUNK TTS GENERATION ---
    if progress_callback: progress_callback(55, "Preparing Hindi audio chunks...")
    
    tts_chunks = split_into_chunks(full_hindi_script, max_chars=TTS_CHUNK_SIZE)
    total_tts_chunks = len(tts_chunks)
    
    if total_tts_chunks == 0:
        return None, "The translated script could not be split into voice synthesis chunks."
    
    if progress_callback: progress_callback(60, f"Generating high-quality audio for {total_tts_chunks} chunks...")
    
    audio_files_map = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(generate_audio, chunk, voice_type, os.path.join(temp_dir, f"chunk_{i:04d}.mp3")): i 
            for i, chunk in enumerate(tts_chunks)
        }
        
        completed_count = 0
        for future in as_completed(futures):
            idx = futures[future]
            try:
                path = future.result()
                if path and os.path.exists(path):
                    audio_files_map[idx] = path
            except Exception as e:
                print(f"TTS Chunk {idx} failed: {e}")
            finally:
                completed_count += 1
                if progress_callback:
                    percent = 60 + int((completed_count / total_tts_chunks) * 30)
                    progress_callback(percent, f"Voice Synthesis: {completed_count}/{total_tts_chunks} done...")

    valid_files = [audio_files_map[i] for i in range(total_tts_chunks) if i in audio_files_map]
    
    if not valid_files:
        return None, "All voice synthesis attempts failed. This might be a temporary service outage."
        
    # --- STAGE 3: MERGE & CINEMATIC MIXING ---
    if progress_callback: progress_callback(95, "Final cinematic mastering and BGM mixing...")
    try:
        success, message = merge_audio_files(valid_files, output_file, bgm_path)
        if not success:
            return None, f"Mixing Phase Failed: {message}"
    except Exception as e:
        return None, f"System Mastering Failure: {e}"
    
    if progress_callback: progress_callback(100, f"Production Finished in {time.time() - start_time:.1f}s")
    return output_file, "Success"



