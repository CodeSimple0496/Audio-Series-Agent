import streamlit as st
import os
import time
from executor import generate_audio_series
from llm_assistant import ScriptAssistant

# Page Config for a premium look
st.set_page_config(
    page_title="Cinematic Audio Series Agent", 
    layout="wide", 
    page_icon="🎙️",
    initial_sidebar_state="expanded"
)

# Custom CSS for that 'Wow' factor
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff8c00, #ff0080);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.4);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Cinematic Audio Series Agent")
st.markdown("Convert massive web novel chapters into high-quality, multi-voice Hindi audio series in seconds. **Powered by AI & Parallel Processing.**")

assistant = ScriptAssistant(limit=500000) # 500k character limit

with st.sidebar:
    st.header("⚙️ Studio Settings")
    voice_type = st.selectbox("Narrator Voice Profile", ["Male", "Sweet Female", "Tense Male"])
    max_workers = st.slider("Concurrency (Parallel Workers)", min_value=1, max_value=100, value=25)
    
    st.markdown("---")
    st.header("🎵 Soundtrack")
    bgm_file = st.file_uploader("Upload Background Score (mp3)", type=["mp3"])
    if bgm_file:
        bgm_path = "temp_bgm.mp3"
        with open(bgm_path, "wb") as f:
            f.write(bgm_file.read())
    else:
        bgm_path = None

def process_and_generate(text_content):
    if not text_content.strip():
        st.error("Please provide some text to process.")
        return
        
    is_valid, msg = assistant.check_length(text_content)
    if not is_valid:
        st.error(f"🛑 {msg}")
        return
        
    st.info(f"Preparing to process {len(text_content):,} characters...")
    
    # AI Script Assistant
    with st.expander("🤖 View AI Character Analysis"):
        mapping = assistant.suggest_voice_mapping(text_content)
        if mapping:
            st.write("Suggested multi-voice mapping (Experimental):")
            st.json(mapping)
        else:
            st.write("No specific character signatures detected.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    start_time = time.time()
    output_file = "output_series.mp3"
    
    def ui_progress_callback(percent, message):
        progress_bar.progress(percent)
        status_text.markdown(f"**Status:** {message}")
    
    # Execute Parallel Pipeline
    try:
        result = generate_audio_series(
            script_text=text_content, 
            voice_type=voice_type, 
            bgm_path=bgm_path, 
            output_file=output_file, 
            max_workers=max_workers,
            progress_callback=ui_progress_callback
        )
    except Exception as e:
        st.error(f"Generation Engine Error: {e}")
        return
    
    if result and os.path.exists(output_file):
        time_taken = time.time() - start_time
        status_text.success(f"Production Complete! 🎉")
        st.balloons()
        
        # Display Performance Metrics in a cleaner way
        st.markdown("### ⚡ Production Metrics")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Execution Time", f"{time_taken:.2f} s")
        m_col2.metric("Characters", f"{len(text_content):,}")
        m_col3.metric("Throughput", f"{int(len(text_content)/time_taken)} chars/s")
        
        st.audio(output_file)
        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Download Full Episode", 
                data=file, 
                file_name="cinematic_episode.mp3", 
                mime="audio/mp3",
                use_container_width=True
            )
    else:
        status_text.error("Production failed. Please check the text content and try again.")

st.markdown("### 📜 Script Input")
raw_text = st.text_area("Paste your English story or script here...", height=400, placeholder="Once upon a time in a far away land...")

if st.button("🚀 Start Production", use_container_width=True):
    process_and_generate(raw_text)

