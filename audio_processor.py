from pydub import AudioSegment
import os

# Set explicit paths for ffmpeg and ffprobe from the current directory
# This assumes they are provided as binaries in the project root for portability
AudioSegment.converter = os.path.abspath("ffmpeg.exe")
AudioSegment.ffprobe = os.path.abspath("ffprobe.exe")

def merge_audio_files(chunk_paths, output_file, bgm_path=None):
    """
    Concatenate a list of temporary audio chunks into a single audio track.
    Adds a short silence (e.g. 500ms) between paragraphs.
    Optionally overlays background music with volume normalization.
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
                # Load with extra care
                segment = AudioSegment.from_file(path)
                # Normalize voice volume for consistency
                segment = segment.normalize()
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
            
            # Memory-efficient looping: only loop if it's shorter than the combined audio
            if len(bgm) < len(combined):
                loops_needed = (len(combined) // len(bgm)) + 1
                bgm = bgm * loops_needed
            
            bgm = bgm[:len(combined)] # Trim to exact length

            # Lower the volume of BGM so it doesn't overpower voice
            # -20 dB is typically a good sweet spot for narration
            bgm = bgm - 20 

            # Overlay with slight fade-in/out for smooth transition
            combined = combined.overlay(bgm.fade_in(2000).fade_out(2000))
        except Exception as e:
            print(f"Error mixing BGM layer: {e}")

    # Export final
    try:
        print(f"Exporting final audio to {output_file}...")
        # Use tags for basic SEO/Metadata
        combined.export(output_file, format="mp3", bitrate="192k", tags={"artist": "Audio Series Agent", "album": "Cinematic Series"})
        print("Merge Complete!")
    except Exception as e:
        print(f"Export failed: {e}")
        return False
    
    # Clean up temp chunks only after successful export
    for path in chunk_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
                
    return True

