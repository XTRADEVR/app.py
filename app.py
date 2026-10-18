import streamlit as st
import google.generativeai as genai

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="XTRADE AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Styling Dark Mode Futuristik (XTRADE VR Style: Pitch Black + RGB Rainbow Glow Border)
st.markdown("""
<style>
    /* Background dasar aplikasi */
    .stApp {
        background-color: #070709;
        color: #E2E8F0;
    }
    
    /* Header Box dengan Border RGB Bergerak */
    .xtrade-card {
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        background: #0f1015;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.15), 0 0 35px rgba(255, 0, 128, 0.1);
    }
    
    .xtrade-card::before {
        content: '';
        position: absolute;
        top: -2px; bottom: -2px;
        left: -2px; right: -2px;
        background: linear-gradient(90deg, #ff007f, #7928ca, #00f2fe, #4facfe, #ff007f);
        background-size: 300% 300%;
        border-radius: 14px;
        z-index: -1;
        animation: rgbGlow 6s ease infinite;
    }

    @keyframes rgbGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .title-text {
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 2.2rem;
        letter-spacing: 4px;
        margin: 0;
        background: linear-gradient(90deg, #ff007f, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-text {
        color: #718096;
        font-size: 0.85rem;
        letter-spacing: 1.5px;
        margin-top: 4px;
        font-family: monospace;
    }

    /* Style Chat Bubbles */
    .stChatMessage {
        background-color: #0f1118 !important;
        border: 1px solid #1a1e29;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* Style Tombol Clear */
    div.stButton > button {
        background: #11131a;
        color: #ff3366;
        border: 1px solid #ff3366;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: #ff3366;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(255, 51, 102, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar: Manajemen API Key & Kontrol
with st.sidebar:
    st.markdown("### ⚡ XTRADE CONFIG")
    
    # Ambil dari st.secrets jika tersedia, jika tidak ambil dari input manual
    secret_key = ""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""

    api_key_input = st.text_input(
        "Gemini API Key",
        value=secret_key,
        type="password",
        placeholder="Paste AIzaSy... disini",
        help="Dapatkan API Key gratis di Google AI Studio (aistudio.google.com)"
    )

    if api_key_input:
        st.success("🟢 API Key Terpasang")
    else:
        st.warning("🔴 Masukkan API Key Anda")

    st.markdown("---")
    
    # Tombol Reset Chat
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style='font-size: 0.8rem; color: #555; text-align: center; margin-top: 20px;'>
        Engine: <b>gemini-1.5-flash</b><br>
        Core: <b>Google Generative AI</b>
    </div>
    """, unsafe_allow_html=True)

# 4. Header XTRADE AI
st.markdown("""
<div class="xtrade-card">
    <div class="title-text">XTRADE AI</div>
    <div class="sub-text">NEURAL INTELLIGENCE PROTOCOL</div>
</div>
""", unsafe_allow_html=True)

# 5. Inisialisasi Riwayat Obrolan
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "XTRADE AI online. Sistem siap menerima instruksi."}
    ]

# Render Obrolan yang Sudah Ada
for message in st.session_state.messages:
    avatar = "⚡" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. Input Pengguna & Eksekusi Gemini
prompt = st.chat_input("Tanyakan analisis pasar, strategi, atau topik apa saja...")

if prompt:
    if not api_key_input:
        st.error("⚠️ Harap masukkan Google Gemini API Key Anda di sidebar terlebih dahulu!")
    else:
        # Tampilkan pertanyaan pengguna
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Proses jawaban dari Gemini dengan streaming
        with st.chat_message("assistant", avatar="⚡"):
            response_container = st.empty()
            full_reply = ""
            
            try:
                # Inisialisasi client Gemini
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="Anda adalah XTRADE AI, asisten analitis cerdas berkecepatan tinggi dengan gaya ringkas, tajam, profesional, dan akurat."
                )
                
                # Format histori chat ke format Gemini
                history_gemini = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history_gemini.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
                
                # Memulai chat dan stream balasan
                chat = model.start_chat(history=history_gemini)
                response = chat.send_message(prompt, stream=True)

                for chunk in response:
                    if chunk.text:
                        full_reply += chunk.text
                        response_container.markdown(full_reply + "▌")
                
                response_container.markdown(full_reply)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})

            except Exception as e:
                error_msg = str(e)
                if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                    st.error("❌ API Key tidak valid. Silakan periksa kembali API Key Anda dari Google AI Studio.")
                elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                    st.error("⏳ Limit request tercapai. Mohon tunggu beberapa saat.")
                else:
                    st.error(f"❌ Terjadi kesalahan: {error_msg}")
