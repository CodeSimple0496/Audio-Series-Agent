from pydub import AudioSegment
import os

def merge_audio_files(chunk_paths, output_file, bgm_path=None):
    """
    Concatenate a list of temporary audio chunks into a single audio track.
    Adds a short silence (e.g. 500ms) between paragraphs.
    Optionally overlays background music.
    """
    if not chunk_paths:
        print("No audio files provided to merge.")
        return False

    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=500) # 500ms between chunks

    print(f"Merging {len(chunk_paths)} chunks...")
    for path in chunk_paths:
        if path and os.path.exists(path):
            try:
                segment = AudioSegment.from_file(path)
                combined += segment + silence
            except Exception as e:
                print(f"Error loading {path}: {e}")
        else:
            print(f"Missing chunk: {path}")

    # Process Background Music if available
    if bgm_path and os.path.exists(bgm_path):
        print(f"Adding Background Music: {bgm_path}")
        try:
            bgm = AudioSegment.from_file(bgm_path)
            
            # Loop bgm to match the length of combined audio
            loops_needed = int(len(combined) / len(bgm)) + 1
            bgm = bgm * loops_needed
            bgm = bgm[:len(combined)] # Trim to exact length

            # Lower the volume of BGM so it doesn't overpower voice
            # Decrease by 15 dB
            bgm = bgm - 15 

            # Overlay
            combined = combined.overlay(bgm)
        except Exception as e:
            print(f"Error mixing BGM layer: {e}")

    # Export final
    print(f"Exporting final audio to {output_file}...")
    combined.export(output_file, format="mp3", bitrate="128k")
    print("Merge Complete!")
    
    # Clean up temp chunks
    for path in chunk_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
                
    return True
