import streamlit as st
import os
import time
from executor import generate_audio_series
from llm_assistant import ScriptAssistant

st.set_page_config(page_title="Cinematic Audio Series Agent", layout="wide", page_icon="🎙️")

st.title("🎙️ Cinematic Audio Series Agent")
st.markdown("Convert massive web novel chapters into high-quality, multi-voice Hindi audio series in minutes. **Powered by AI & Concurrency.**")

assistant = ScriptAssistant(limit=500000) # 500k character limit per session

with st.sidebar:
    st.header("⚙️ Configuration")
    voice_type = st.selectbox("Select Default Voice Profile", ["Male", "Sweet Female", "Tense Male"])
    max_workers = st.slider("Concurrency (Parallel Workers)", min_value=1, max_value=100, value=25)
    
    st.markdown("---")
    st.header("🎵 Background Music")
    bgm_file = st.file_uploader("Upload BGM (mp3)", type=["mp3"])
    if bgm_file:
        with open("temp_bgm.mp3", "wb") as f:
            f.write(bgm_file.read())
        bgm_path = "temp_bgm.mp3"
    else:
        bgm_path = None

def process_and_generate(text_content):
    if not text_content.strip():
        st.error("No content to process.")
        return
        
    # Session Management: Check Character Limit
    is_valid, msg = assistant.check_length(text_content)
    if not is_valid:
        st.error(f"🛑 {msg}")
        return
        
    st.info(f"Processing ~{len(text_content)} characters...")
    
    # AI Script Assistant: Extract names and suggest mapping
    st.markdown("### 🤖 AI Script Analysis")
    with st.expander("Show AI Extracted Characters (Heuristic Mapping)"):
        mapping = assistant.suggest_voice_mapping(text_content)
        if mapping:
            st.json(mapping)
        else:
            st.write("No specific dialogue signatures detected.")
    
    progress = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Dividing and Conquering (Translating & TTS in Parallel)...")
    
    start_time = time.time()
    output_file = "output_series.mp3"
    
    def ui_progress_callback(percent, message):
        progress.progress(percent)
        status_text.text(message)
    
    # Execute Parallel Pipeline
    result = generate_audio_series(
        script_text=text_content, 
        voice_type=voice_type, 
        bgm_path=bgm_path, 
        output_file=output_file, 
        max_workers=max_workers,
        progress_callback=ui_progress_callback
    )
    
    progress.progress(100)
    end_time = time.time()
    
    if result:
        time_taken = end_time - start_time
        status_text.success(f"Generation Complete! 🎉")
        st.balloons()
        
        # Display Performance Metrics
        st.markdown("### ⚡ Performance Metrics")
        col1, col2 = st.columns(2)
        col1.metric("Total Execution Time", f"{time_taken:.2f} s")
        col2.metric("Characters Processed", f"{len(text_content):,}")
        
        if os.path.exists(output_file):
            st.audio(output_file)
            with open(output_file, "rb") as file:
                st.download_button("Download Full Episode", data=file, file_name="episode.mp3", mime="audio/mp3")
    else:
        status_text.error("Audio generation failed. Check logs for details.")

raw_text = st.text_area("Paste English Script Here", height=300)
if st.button("Generate from Text", use_container_width=True):
    process_and_generate(raw_text)
