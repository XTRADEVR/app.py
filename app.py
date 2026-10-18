import streamlit as st
from google import genai
import time

st.set_page_config(page_title="XTRADE AI", page_icon="⚡", layout="wide")

# CSS MEWAH RGB + GLASSMORPHISM
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
.stApp { background: radial-gradient(ellipse at top, #0f172a, #020617); color: white; }
h1 { font-family: 'Orbitron'; text-align: center; background: linear-gradient(90deg, #00f5ff, #a855f7, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-size: 200% auto; animation: shine 3s linear infinite; }
@keyframes shine { to { background-position: 200% center; } }
.chat-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(0,245,255,0.2); border-radius: 15px; padding: 15px; backdrop-filter: blur(10px); }
.stChatInput > div { background: rgba(255,255,255,0.05) !important; border: 1px solid #00f5ff !important; border-radius: 30px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ XTRADE AI NEURAL INTELLIGENCE PROTOCOL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; letter-spacing:3px;'>XTRADE VR // MARKET INTELLIGENCE SYSTEM</p>", unsafe_allow_html=True)

# SIDEBAR CONFIG
with st.sidebar:
    st.markdown("### ⚙️ XTRADE CONFIG")
    api_key = st.text_input("Gemini API Key (AQ...):", type="password", placeholder="Paste AQ... disini")
    st.markdown("---")
    st.markdown("**Status:**")
    if api_key:
        st.success("🟢 API Terhubung")
    else:
        st.error("🔴 Masukkan API Key Anda")
    st.markdown("---")
    st.caption("XTRADE VR FYP CLEAN V9")

if not api_key:
    st.stop()

# CLIENT BARU SUPPORT AQ
client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "XTRADE AI online. Sistem siap menerima instruksi. 🚀"}]

# TAMPILKAN CHAT DENGAN BOX MEWAH
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-box'>{m['content']}</div>", unsafe_allow_html=True)

prompt = st.chat_input("Tanyakan analisis pasar, strategi, atau topik apa...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='chat-box'>{prompt}</div>", unsafe_allow_html=True)
    
    try:
        with st.chat_message("assistant"):
            with st.spinner("⚡ XTRADE AI sedang menganalisis..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"Kamu adalah XTRADE AI, asisten trading cerdas, analitis, dan mewah. Jawab dengan gaya profesional tapi keren. Pertanyaan: {prompt}"
                )
                answer = response.text
                st.markdown(f"<div class='chat-box'>{answer}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
