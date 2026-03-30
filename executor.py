import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from translator import split_into_chunks, GoogleTranslator
from tts_engine import generate_audio
from audio_processor import merge_audio_files

def process_chunk(idx, chunk_text, voice_type, temp_dir):
    """
    Worker function to translate and generate audio for a single text chunk.
    """
    if not chunk_text or not chunk_text.strip():
        print(f"[{idx}] Skipping empty chunk.")
        return idx, None
        
    start = time.time()
    
    # 1. Translate
    try:
        translator = GoogleTranslator(source='en', target='hi')
        hi_text = translator.translate(chunk_text)
        if not hi_text:
            print(f"[{idx}] Translation returned empty. Using fallback.")
            hi_text = chunk_text
    except Exception as e:
        print(f"[{idx}] Translation failed: {e}")
        hi_text = chunk_text # fallback

    # 2. TTS
    out_path = os.path.join(temp_dir, f"chunk_{idx:04d}.mp3")
    result_path = generate_audio(hi_text, voice_type, out_path)
    
    if result_path:
        print(f"[{time.time()-start:.2f}s] Processed chunk {idx}")
    else:
        print(f"[{time.time()-start:.2f}s] Failed to generate audio for chunk {idx}")
        
    return idx, result_path


def generate_audio_series(script_text, voice_type="Male", bgm_path=None, output_file="final_audio.mp3", max_workers=20, progress_callback=None):
    """
    Main orchestration function.
    Splits the script, processes chunks concurrently, and merges the final result.
    Invokes progress_callback(progress_percentage, status_text) if provided.
    """
    print(f"Starting generation. Max workers: {max_workers}")
    start_time = time.time()
    
    temp_dir = "temp_audio_chunks"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Split Text into smaller chunks suitable for TTS (edge-tts likes smaller chunks)
    if progress_callback: progress_callback(5, "Splitting text into chunks...")
    chunks = split_into_chunks(script_text, max_chars=400) 
    print(f"Total chunks to process: {len(chunks)}")
    total_chunks = len(chunks)
    
    # 2. Process concurrently
    if progress_callback: progress_callback(10, f"Translating and generating audio for {total_chunks} chunks...")
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
                print(f"Error processing a chunk: {e}")
            finally:
                completed_count += 1
                if progress_callback:
                    # Map chunk progress from 10% to 90%
                    percent = 10 + int((completed_count / total_chunks) * 80)
                    progress_callback(percent, f"Processing chunks: {completed_count}/{total_chunks} completed...")
                
    # Ensure chronological order
    valid_files = [audio_files_map[i] for i in range(len(chunks)) if i in audio_files_map]
    
    if not valid_files:
        print("Failed to generate any audio chunks.")
        return None
        
    # 3. Merge
    if progress_callback: progress_callback(95, "Merging all generated audio chunks...")
    print("Merging generated chunks...")
    merge_audio_files(valid_files, output_file, bgm_path)
    
    if progress_callback: progress_callback(100, "Finalizing output...")
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")
    return output_file
