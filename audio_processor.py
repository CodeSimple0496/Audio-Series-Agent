from pydub import AudioSegment
import os
import sys

# Duplicate sys import removed
import shutil
from concurrent.futures import ThreadPoolExecutor
import config
from utils import Timer
from pydub.effects import compress_dynamic_range
from pydub.silence import detect_silence

# --- ULTRA-STABLE AUTO-DISCOVERY ENGINE ---
# This engine automatically finds FFmpeg in any environment (Local Windows or Cloud Linux)
def setup_audio_engine():
    # 1. Check if FFmpeg is in the system PATH (Standard for Cloud/Linux)
    if shutil.which("ffmpeg"):
        AudioSegment.converter = "ffmpeg"
        AudioSegment.ffprobe = "ffprobe"
        return "System PATH"
        
    # 2. Check for local binaries (Standard for Portable Windows builds)
    if os.path.exists("ffmpeg.exe"):
        AudioSegment.converter = os.path.abspath("ffmpeg.exe")
        AudioSegment.ffprobe = os.path.abspath("ffprobe.exe")
        return "Local EXE"
        
    # 3. Last resort fallback
    return "Not Found"

ENGINE_STATUS = setup_audio_engine()

def process_chunk(segment: AudioSegment) -> AudioSegment:
    """Apply a series of audio enhancements to a single chunk.

    Steps:
    1. Normalize volume.
    2. High‑pass filter at 300 Hz to reduce low‑frequency noise.
    3. Trim leading/trailing silence (detect_silence with 500 ms threshold).
    4. Dynamic range compression.
    5. Add 50 ms fade‑in and fade‑out.
    6. Ensure consistent frame rate (44.1 kHz).
    """
    # 1. Normalize
    segment = segment.normalize()
    # 2. High‑pass filter for basic noise reduction
    segment = segment.high_pass_filter(300)
    # 3. Trim silence
    silence_ranges = detect_silence(segment, min_silence_len=500, silence_thresh=-40)
    if silence_ranges:
        # Remove leading silence
        start_trim = silence_ranges[0][1] if silence_ranges[0][0] == 0 else 0
        # Remove trailing silence
        end_trim = silence_ranges[-1][0] if silence_ranges[-1][1] == len(segment) else len(segment)
        segment = segment[start_trim:end_trim]
    # 4. Dynamic range compression
    segment = compress_dynamic_range(segment)
    # 5. Fade in/out
    segment = segment.fade_in(50).fade_out(50)
    # 6. Consistent frame rate
    segment = segment.set_frame_rate(44100)
    return segment


def load_and_process_chunk(path):
    """Helper to load and process a single audio chunk."""
    if not path or not os.path.exists(path):
        return None
    try:
        raw_segment = AudioSegment.from_file(path)
        return process_chunk(raw_segment)
    except Exception as e:
        print(f"Skipping corrupted chunk {path}: {e}")
        return None


def merge_audio_files(chunk_paths, output_file, bgm_path=None, bitrate="256k", export_format="mp3"):
    """
    Concatenate a list of temporary audio chunks into a single audio track.
    The function now normalizes volume, applies noise reduction, trims silence, compresses dynamic range, adds fades, and cross‑fades chunks.
    Parameters:
        chunk_paths (list): Paths to individual audio chunks.
        output_file (str): Destination file path.
        bgm_path (str, optional): Background music to overlay.
        bitrate (str, optional): Export bitrate (default "256k").
        export_format (str, optional): Export format (default "mp3").
    Returns: (bool: success, str: message)
    """
    # 1. Intelligent Binary Validation
    if ENGINE_STATUS == "Not Found":
        return False, "FFmpeg engine not found. Locally, make sure ffmpeg.exe is in the root. On Cloud, ensure 'ffmpeg' is in packages.txt."

        
    if not chunk_paths:
        return False, "No audio chunks were generated to merge. This could be due to a TTS failure."

    try:
        combined = AudioSegment.empty()
        print(f"Merging {len(chunk_paths)} chunks with smooth crossfades...")
        previous_segment = None
        
        # Preprocess chunks concurrently
        with Timer("Audio Chunk Preprocessing", logger=print if config.VERBOSE else None):
            with ThreadPoolExecutor(max_workers=config.MAX_WORKERS_TTS) as executor:
                processed_segments = list(executor.map(load_and_process_chunk, chunk_paths))
                
        # Sequentially concatenate to maintain order and apply crossfades
        with Timer("Audio Chunk Concatenation", logger=print if config.VERBOSE else None):
            for i, processed in enumerate(processed_segments):
                if processed is None:
                    print(f"Chunk missing or corrupted: {chunk_paths[i]}")
                    continue
                if previous_segment is None:
                    combined = processed
                else:
                    combined = combined.append(processed, crossfade=100)
                previous_segment = processed

        if len(combined) == 0:
            return False, "Total combined audio duration is zero. Please check the voice generation logs."

        # Process BGM
        if bgm_path and os.path.exists(bgm_path):
            try:
                bgm = AudioSegment.from_file(bgm_path)
                if len(bgm) < len(combined):
                    loops_needed = (len(combined) // len(bgm)) + 1
                    bgm = bgm * loops_needed
                bgm = bgm[:len(combined)] - 20 
                combined = combined.overlay(bgm.fade_in(2000).fade_out(2000))
            except Exception as e:
                print(f"BGM mixing failed (skipping): {e}")

        # Final Export
        print(f"Exporting to {output_file}...")
        # Export with requested format and bitrate
        combined.export(output_file, format=export_format, bitrate=bitrate, tags={"artist": "Audio Series Agent", "album": "Cinematic Series"})
        print("Merge Complete!")
        
        # Cleanup
        for path in chunk_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
                
        return True, "Merged successfully."
    except Exception as e:
        return False, f"Export failed: {str(e)}"
