from pydub import AudioSegment
import os
import sys

import sys
import shutil

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


def merge_audio_files(chunk_paths, output_file, bgm_path=None):
    """
    Concatenate a list of temporary audio chunks into a single audio track.
    Returns: (bool: success, str: message)
    """
    # 1. Intelligent Binary Validation
    if ENGINE_STATUS == "Not Found":
        return False, "FFmpeg engine not found. Locally, make sure ffmpeg.exe is in the root. On Cloud, ensure 'ffmpeg' is in packages.txt."

        
    if not chunk_paths:
        return False, "No audio chunks were generated to merge. This could be due to a TTS failure."

    try:
        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=500) # 500ms between chunks

        print(f"Merging {len(chunk_paths)} chunks...")
        for i, path in enumerate(chunk_paths):
            if path and os.path.exists(path):
                try:
                    segment = AudioSegment.from_file(path)
                    segment = segment.normalize()
                    combined += segment + silence
                except Exception as e:
                    print(f"Skipping corrupted chunk {path}: {e}")
            else:
                print(f"Chunk missing: {path}")

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
        combined.export(output_file, format="mp3", bitrate="192k", tags={"artist": "Audio Series Agent", "album": "Cinematic Series"})
        print("Merge Complete!")
        
        # Cleanup
        for path in chunk_paths:
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
                
        return True, "Merged successfully."
    except Exception as e:
        return False, f"Export failed: {str(e)}"
