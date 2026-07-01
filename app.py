import streamlit as st

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Voice Translator UI",
    page_icon="🎙️",
    layout="wide",
)

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

    /* Flat layouts replacing the white cards */
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
        min-height: 220px;
    }

    .mic-outer{
        width: 160px; height:160px; border-radius:50%;
        background: radial-gradient(circle at 30% 30%, #8f97ff, #5f6af2 68%);
        display:flex; align-items:center; justify-content:center;
        color:white;
        font-size:64px;
        box-shadow: 0 8px 25px rgba(95,106,242,0.35),
                    0 0 0 14px rgba(95,106,242,0.08),
                    0 0 0 28px rgba(95,106,242,0.05);
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
        color:#8b90a0;
        font-size:28px;
        line-height:1.3;
        margin-bottom:8px;
        background:#fff;
        box-shadow: 0 4px 12px rgba(20, 24, 40, 0.02);
    }

    .textbox.green{
        border-color:#dbeedc;
        background:#f7fdf8;
        color:#7ea089;
    }

    .chars{
        color:#9198a8;
        font-size:18px;
        margin-top: 4px;
    }

    .listen{
        display:flex;
        align-items:center;
        gap:14px;
        margin-top: 24px;
        color:#30364a;
        font-size:28px;
    }

    .play{
        width:48px; height:48px; border-radius:50%;
        border:2px solid #7480f8;
        color:#7480f8;
        display:flex; align-items:center; justify-content:center;
        font-weight:700;
        font-size:22px;
        background: #fff;
    }

    .wave{
        flex:1;
        height:8px;
        background: repeating-linear-gradient(
          to right,
          #d9dcff 0px, #d9dcff 3px,
          transparent 3px, transparent 6px
        );
        border-radius: 999px;
        opacity: 0.9;
    }

    .time{
        color:#8f96a8; font-size:28px;
    }

    .bottom{
        display:flex; justify-content:center;
        margin-top: 18px;
    }

    .record-again{
        background: #eef0ff;
        color:#5f6af2;
        border: none;
        border-radius: 18px;
        padding: 14px 28px;
        font-size: 30px;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(95,106,242,0.1);
    }

    .stSelectbox label {display:none;}
</style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.markdown('<div class="container">', unsafe_allow_html=True)

st.markdown('<div class="title">Translate your voice instantly</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Speak now and break the language barrier</div>', unsafe_allow_html=True)

# Top language block (Cleaned from card)
st.markdown('<div class="topbar">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.05, 0.22, 1.05])

with c1:
    st.markdown('<div class="lbl">From</div>', unsafe_allow_html=True)
    st.markdown('<div class="select-wrap">', unsafe_allow_html=True)
    st.selectbox("From", ["English", "Amharic (አማርኛ)", "Afaan Oromo (Oromiffa)", "Somali", "Tigrinya (ትግርኛ)"], index=0)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="swap">⇄</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="lbl">To</div>', unsafe_allow_html=True)
    st.markdown('<div class="select-wrap">', unsafe_allow_html=True)
    st.selectbox("To", ["🇪🇹  አማርኛ (Amharic)", "🇺🇸  English", "🇫🇷  French", "🇪🇸  Spanish"], index=0)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Record hero block (Cleaned from card)
st.markdown('<div class="record-card">', unsafe_allow_html=True)
st.markdown("""
<div class="record-wrap">
  <div class="mic-outer">🎙️</div>
  <div>
    <div class="record-title">Tap to start recording</div>
    <div class="record-sub">Speak clearly for better results</div>
    <div class="pill"><span class="dot"></span>Ready to record</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Two panels (Cleaned from card)
left, right = st.columns(2)

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-head"><span>📄 Transcript</span><span class="copy-btn">📋 Copy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="textbox">Your speech will appear here...</div>', unsafe_allow_html=True)
    st.markdown('<div class="chars">0 characters</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-head"><span>🌍 Translation</span><span class="copy-btn">📋 Copy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="textbox green">Translation will appear here...</div>', unsafe_allow_html=True)
    st.markdown('<div class="chars">0 characters</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="listen">
      <div class="play">▶</div>
      <div>Listen Translation</div>
      <div class="wave"></div>
      <div class="time">00:00</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom button
st.markdown('<div class="bottom"><button class="record-again">⟳&nbsp;&nbsp;Record Again</button></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
