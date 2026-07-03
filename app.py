import streamlit as st
from audio_recorder_streamlit import audio_recorder
from transformers import AutoModelForCTC, AutoProcessor, pipeline
import hashlib
import io
import numpy as np
import soundfile as sf
import torch

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Voice Translator UI",
    page_icon="🎙️",
    layout="wide",
)

# ------------------ STATE INITIALIZATION ------------------
if "transcript" not in st.session_state:
    st.session_state.transcript = "Your speech will appear here..."
if "translation" not in st.session_state:
    st.session_state.translation = "Translation will appear here..."
if "status" not in st.session_state:
    st.session_state.status = "Ready to record"
if "last_audio_signature" not in st.session_state:
    st.session_state.last_audio_signature = None

# ------------------ STYLES ------------------
st.markdown("""
<style>
    :root{
        --bg: #f7f8fc;
        --border: #ececf4;
        --text: #1f2430;
        --muted: #7b8191;
        --primary: #5f6af2;
        --primary-2: #7a84ff;
        --green: #22a55b;
        --green-bg: #e9f8ef;
    }

    .stApp {
        background: radial-gradient(1200px 500px at -10% -20%, #f3f4ff 0%, transparent 55%),
                    radial-gradient(1200px 500px at 110% -10%, #f0f8ff 0%, transparent 55%),
                    var(--bg);
        color: var(--text);
    }

    .container{
        max-width: 1100px;
        margin: 0 auto;
        padding: 10px 8px 40px;
    }

    .title{
        text-align:center;
        font-size: 52px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 10px 0 4px;
        color: #1a1f2f;
    }

    .subtitle{
        text-align:center;
        font-size: 28px;
        color: #737a8c;
        margin-bottom: 28px;
    }

    .topbar{
        padding: 10px 0px;
        margin-bottom: 18px;
    }

    .lbl{
        font-size: 20px;
        color: #3a3f50;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .select-wrap{
        border: 1px solid #e6e8f0;
        border-radius: 16px;
        padding: 8px 10px;
        background: #fff;
        box-shadow: 0 4px 12px rgba(20, 24, 40, 0.02);
    }

    .swap{
        width: 58px; height:58px; border-radius:50%;
        border: 1px solid #e3e6f2;
        display:flex; align-items:center; justify-content:center;
        margin-top: 30px;
        color: var(--primary);
        font-size: 26px;
        background: #fff;
    }

    .record-card{
        padding: 24px 0px;
        margin-bottom: 18px;
    }

    .record-wrap{
        display:flex; align-items:center; justify-content:center;
        gap: 40px;
        min-height: 120px;
    }

    .record-title{
        font-size: 44px;
        font-weight: 800;
        line-height: 1.2;
        color:#171d2e;
        margin-bottom: 6px;
    }

    .record-sub{
        color:#737b90;
        font-size:24px;
        margin-bottom: 14px;
    }

    .pill{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:10px 16px;
        border-radius:12px;
        background: var(--green-bg);
        color:#22884f;
        font-weight: 600;
        font-size:20px;
    }

    .dot{
        width:10px; height:10px; border-radius:50%;
        background:#1e9f4d;
    }

    .panel{
        padding: 16px 0px;
        min-height: 280px;
    }

    .panel-head{
        display:flex;
        align-items:center;
        justify-content:space-between;
        font-size: 36px;
        font-weight:700;
        margin-bottom: 12px;
    }

    .copy-btn{
        border: 1px solid #e4e6ef;
        border-radius: 12px;
        padding: 8px 14px;
        color:#3c4257;
        font-size:18px;
        background:#fff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .textbox{
        border:1px solid #e7e8f0;
        border-radius:16px;
        min-height:180px;
        padding:14px 16px;
        font-size:28px;
        line-height:1.3;
        margin-bottom:8px;
        background:#fff;
        box-shadow: 0 4px 12px rgba(20, 24, 40, 0.02);
    }

    .textbox.green{
        border-color:#dbeedc;
        background:#f7fdf8;
    }

    .chars{
        color:#9198a8;
        font-size:18px;
        margin-top: 4px;
    }

    .stSelectbox label {display:none;}
</style>
""", unsafe_allow_html=True)

# ------------------ REAL AI FUNCTIONS ------------------
SUPPORTED_ETHIO_LANGS = {
    "Amharic (አማርኛ)": "Amharic",
    "Afaan Oromo (Oromiffa)": "Afaan Oromo",
    "Tigrinya (ትግርኛ)": "Tigrinya",
}


def resample_audio(audio_data, source_rate, target_rate=16000):
    if source_rate == target_rate:
        return audio_data.astype("float32")

    if len(audio_data) < 2:
        return audio_data.astype("float32")

    target_length = max(1, int(round(len(audio_data) * target_rate / source_rate)))
    source_positions = np.linspace(0.0, 1.0, num=len(audio_data), endpoint=True)
    target_positions = np.linspace(0.0, 1.0, num=target_length, endpoint=True)
    return np.interp(target_positions, source_positions, audio_data).astype("float32")


@st.cache_resource
def load_speech_models(lang):
    if lang == "English" or lang == "Somali":
        model_name = "openai/whisper-base"
        try:
            return {
                "backend": "whisper",
                "model_name": model_name,
                "pipeline": pipeline(
                    "automatic-speech-recognition",
                    model=model_name,
                    generate_kwargs={
                        "language": "english" if lang == "English" else "somali",
                        "task": "transcribe",
                    },
                ),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model '{model_name}': {str(e)}") from e

    if lang not in SUPPORTED_ETHIO_LANGS:
        raise ValueError(f"Unsupported source language: {lang}")

    model_name = "badrex/Ethio-ASR-multilingual-600M"

    try:
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForCTC.from_pretrained(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        return {
            "backend": "ethio_ctc",
            "model_name": model_name,
            "processor": processor,
            "model": model,
            "device": device,
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load ASR model '{model_name}' for {lang}: {str(e)}") from e

# ------------------ UI RENDERING ------------------
st.markdown('<div class="container">', unsafe_allow_html=True)

st.markdown('<div class="title">Translate your voice instantly</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Speak now and break the language barrier</div>', unsafe_allow_html=True)

st.markdown('<div class="topbar">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.05, 0.22, 1.05])

with c1:
    st.markdown('<div class="lbl">From</div>', unsafe_allow_html=True)
    st.markdown('<div class="select-wrap">', unsafe_allow_html=True)
    src_lang = st.selectbox("From", ["English", "Amharic (አማርኛ)", "Afaan Oromo (Oromiffa)", "Somali", "Tigrinya (ትግርኛ)"], index=0, key="src_lang")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="swap">⇄</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="lbl">To</div>', unsafe_allow_html=True)
    st.markdown('<div class="select-wrap">', unsafe_allow_html=True)
    tgt_lang = st.selectbox("To", ["English", "Amharic (አማርኛ)", "Afaan Oromo (Oromiffa)", "Somali", "Tigrinya (ትግርኛ)"], index=1, key="tgt_lang")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Interactive Recording Component
st.markdown('<div class="record-card">', unsafe_allow_html=True)
rec_col1, rec_col2 = st.columns([0.4, 0.6])

with rec_col1:
    # Explicit key added to keep component frontend anchor rock solid
    audio_bytes = audio_recorder(text="", recording_color="#5f6af2", neutral_color="#7b8191", key="voice_translator_recorder")

with rec_col2:
    st.markdown(f'<div class="record-title">Voice Control Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="record-sub">Click the component on the left to handle recording streams</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pill"><span class="dot"></span>{st.session_state.status}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Processing execution block (In-Memory Soundfile Approach)
if audio_bytes:
    audio_signature = hashlib.sha1(audio_bytes).hexdigest()

    if audio_signature != st.session_state.last_audio_signature:
        st.session_state.last_audio_signature = audio_signature
        st.session_state.status = "Processing Speech..."

        try:
            # 1. Read raw audio bytes directly into a numpy array via soundfile
            audio_file = io.BytesIO(audio_bytes)
            data, samplerate = sf.read(audio_file)

            # 2. Flatten array channels if audio stream records in stereo
            if len(data.shape) > 1:
                data = data.mean(axis=1)

            data = data.astype("float32")

            # 3. Spin up/retrieve cached model with visible feedback for large downloads/caching
            with st.spinner(f"Loading ASR model for {src_lang}..."):
                asr_bundle = load_speech_models(src_lang)

            # 4. Process transcription with the architecture that matches the selected language.
            if asr_bundle["backend"] == "whisper":
                audio_input = {
                    "raw": data,
                    "sampling_rate": samplerate,
                }
                result = asr_bundle["pipeline"](audio_input)
                transcript_res = result.get("text", "").strip()
            else:
                ethio_audio = resample_audio(data, samplerate, 16000)
                processor = asr_bundle["processor"]
                model = asr_bundle["model"]
                device = asr_bundle["device"]

                inputs = processor(
                    ethio_audio,
                    sampling_rate=16000,
                    return_tensors="pt",
                )
                inputs = {key: value.to(device) for key, value in inputs.items()}

                with torch.no_grad():
                    logits = model(**inputs).logits

                pred_ids = torch.argmax(logits, dim=-1)
                transcript_res = processor.batch_decode(pred_ids, skip_special_tokens=True)[0].strip()

            if not transcript_res:
                transcript_res = "System captured audio, but no speech text was recognized."

            # 5. Save and set values
            st.session_state.transcript = transcript_res
            st.session_state.translation = f"[Translated to {tgt_lang}]: Running translation matching engine..."
            st.session_state.status = "Translation Complete"
        except (ValueError, KeyError, TypeError) as e:
            st.session_state.status = f"ASR configuration error: {str(e)}"
        except Exception as e:
            error_text = str(e).lower()
            if "out of memory" in error_text or "cuda" in error_text:
                st.session_state.status = "Multilingual model hit a memory limit. Try a smaller input or restart the app."
            elif "unsupported source language" in error_text:
                st.session_state.status = str(e)
            else:
                st.session_state.status = f"Error processing audio: {str(e)}"

# Reactive Data Panels
left, right = st.columns(2)

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-head"><span>📄 Transcript</span><span class="copy-btn">📋 Copy</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="textbox">{st.session_state.transcript}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chars">{len(st.session_state.transcript)} characters</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-head"><span>🌍 Translation</span><span class="copy-btn">📋 Copy</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="textbox green">{st.session_state.translation}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chars">{len(st.session_state.translation)} characters</div>', unsafe_allow_html=True)
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)