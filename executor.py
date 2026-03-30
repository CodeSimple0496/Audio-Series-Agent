import os
import time
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from translator import split_into_chunks, translate_chunk
from tts_engine import generate_audio
from audio_processor import merge_audio_files

def process_chunk(idx, chunk_text, voice_type, temp_dir):
    """
    Worker function to translate and generate audio for a single text chunk.
    """
    if not chunk_text or not chunk_text.strip():
        return idx, None
        
    start = time.time()
    
    # 1. Translate using the robust logic in translator.py
    try:
        hi_text = translate_chunk(chunk_text)
        if not hi_text:
            hi_text = chunk_text # fallback
    except Exception as e:
        print(f"[{idx}] Translation error: {e}")
        hi_text = chunk_text # fallback

    # 2. TTS
    out_path = os.path.join(temp_dir, f"chunk_{idx:04d}.mp3")
    result_path = generate_audio(hi_text, voice_type, out_path)
    
    if result_path:
        print(f"[{time.time()-start:.2f}s] Processed chunk {idx}")
    else:
        print(f"[{time.time()-start:.2f}s] Failed chunk {idx}")
        
    return idx, result_path

def generate_audio_series(script_text, voice_type="Male", bgm_path=None, output_file="final_audio.mp3", max_workers=20, progress_callback=None):
    """
    Main orchestration function.
    Splits the script, processes chunks concurrently, and merges the final result.
    """
    start_time = time.time()
    
    temp_dir = "temp_audio_chunks"
    
    # Clear and recreate temp directory to ensure a clean run
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Split Text
    if progress_callback: progress_callback(5, "Analyzing and splitting script...")
    chunks = split_into_chunks(script_text, max_chars=400) 
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        return None

    # 2. Process concurrently
    if progress_callback: progress_callback(10, f"Generating audio for {total_chunks} chunks...")
    audio_files_map = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_chunk, i, chunk, voice_type, temp_dir): i 
            for i, chunk in enumerate(chunks)
        }
        
        completed_count = 0
        for future in as_completed(futures):
            try:
                idx, path = future.result()
                if path and os.path.exists(path):
                    audio_files_map[idx] = path
            except Exception as e:
                print(f"Error in worker thread: {e}")
            finally:
                completed_count += 1
                if progress_callback:
                    percent = 10 + int((completed_count / total_chunks) * 80)
                    progress_callback(percent, f"Translation & TTS: {completed_count}/{total_chunks} done...")
                
    # Ensure chronological order
    valid_files = [audio_files_map[i] for i in range(len(chunks)) if i in audio_files_map]
    
    if not valid_files:
        print("No audio chunks were generated successfully.")
        return None
        
    # 3. Merge
    if progress_callback: progress_callback(95, "Merging audio and adding background music...")
    try:
        success = merge_audio_files(valid_files, output_file, bgm_path)
        if not success:
            return None
    except Exception as e:
        print(f"Merge failed: {e}")
        return None
    
    if progress_callback: progress_callback(100, f"Finished in {time.time() - start_time:.1f}s")
    return output_file

