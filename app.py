import streamlit as st
import json
import os
import requests
from urllib.parse import quote

# ----------------- PROTEKSI IMPORT ENGINE -----------------
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from gTTS import gTTS
    import io
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ----------------- KONFIGURASI HALAMAN -----------------
st.set_page_config(
    page_title="AI XTRADE VR",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded",
)

STORAGE_FILE = "xtrade_data.json"

# ----------------- PERSISTENSI DATA -----------------
def load_data():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"api_key": "", "chat_history": []}

def save_data(api_key, chat_history):
    try:
        data = {"api_key": api_key, "chat_history": chat_history}
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

saved_data = load_data()

if "api_key" not in st.session_state:
    st.session_state.api_key = saved_data.get("api_key", "")
if "messages" not in st.session_state:
    st.session_state.messages = saved_data.get("chat_history", [])
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark Luxury"

# ----------------- GAYA CSS LUXURY (GOLD & BLACK) -----------------
def inject_custom_css(theme):
    if theme == "Dark Luxury":
        bg_gradient = "radial-gradient(circle at 20% 20%, #151515 0%, #050505 100%)"
        card_bg = "rgba(20, 20, 20, 0.85)"
        text_color = "#F5E6C8"
    else:
        bg_gradient = "linear-gradient(135deg, #f9f7f2 0%, #ede6d6 100%)"
        card_bg = "rgba(255, 255, 255, 0.90)"
        text_color = "#1A1A1A"

    css = f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        .gold-shimmer-text {{
            background: linear-gradient(90deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 5s infinite linear;
            font-weight: 800;
            letter-spacing: 1.5px;
        }}
        div.stButton > button {{
            background: linear-gradient(135deg, #D4AF37, #8C6D23) !important;
            color: #000000 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.2rem !important;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
            transition: all 0.3s ease !important;
        }}
        div.stButton > button:hover {{
            background: linear-gradient(135deg, #FFE082, #D4AF37) !important;
            transform: scale(1.02);
            color: #000 !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css(st.session_state.theme_mode)

# ----------------- PERINGATAN MODUL JIKA BELUM TERINSTAL -----------------
if not GTTS_AVAILABLE:
    st.warning("⚠️ Modul audio (`gTTS`) belum terdeteksi di server. Pastikan file `requirements.txt` sudah ada di GitHub agar suara aktif.")

# ----------------- SIDEBAR PENGATURAN -----------------
with st.sidebar:
    st.markdown("<h2 class='gold-shimmer-text'>⚜️ AI XTRADE VR</h2>", unsafe_allow_html=True)
    st.caption("Private Intelligence & Market Mastery")

    theme_choice = st.radio(
        "Mode Tampilan",
        ["Dark Luxury", "Light Shimmer"],
        index=0 if st.session_state.theme_mode == "Dark Luxury" else 1,
    )
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun()

    st.markdown("---")
    
    input_key = st.text_input(
        "Gemini API Key (Awalan AQ...):",
        value=st.session_state.api_key,
        type="password",
        help="API Key otomatis disimpan dan tidak hilang saat reload.",
    )
    if input_key != st.session_state.api_key:
        st.session_state.api_key = input_key
        save_data(st.session_state.api_key, st.session_state.messages)
        st.success("API Key berhasil disimpan.")

    model_choice = st.selectbox(
        "Pilih Mesin AI",
        [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-3.8-flash",
            "gemini-3.5-lite",
        ],
    )

    if st.button("✨ FYP CLEAN (Bersihkan Memori)"):
        st.session_state.messages = []
        save_data(st.session_state.api_key, [])
        st.success("Tampilan bersih & mewah telah disegarkan!")
        st.rerun()

    st.markdown("---")
    st.info("🔒 Sesi Aman & Tersimpan Secara Privat.")

# ----------------- SYSTEM INSTRUCTION -----------------
SYSTEM_INSTRUCTION = """
Kamu adalah AI XTRADE VR, entitas kecerdasan buatan super yang menggabungkan kemampuan reasoning Claude dan fleksibilitas ChatGPT.
Karakteristik:
1. Sangat cerdas, berwawasan luas, akurat, dan adaptif dengan instruksi pengguna.
2. Selalu ramah dan suportif terhadap segala pertanyaan user tanpa jawaban birokratis yang kaku.
3. Menguasai analisis teknikal, trading crypto/forex/saham, coding, dan prompt engineering.
"""

# ----------------- TABS UTAMA -----------------
tab_chat, tab_prompt, tab_image = st.tabs([
    "💬 Percakapan Elit", 
    "🎯 Generator Prompt Pro", 
    "🎨 Teks ke Gambar (Visual)"
])

# ----------------- TAB 1: PERCAKAPAN & SUARA -----------------
with tab_chat:
    st.markdown("<h3 class='gold-shimmer-text'>🏛️ XTRADE CONVERSATION SUITE</h3>", unsafe_allow_html=True)

    # Tampilkan pesan sebelumnya
    for idx, msg in enumerate(st.session_state.messages):
        role_label = "👑 User" if msg["role"] == "user" else "⚜️ AI XTRADE VR"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{role_label}**")
            st.markdown(msg["content"])
            
            # Putar audio per pesan jika gTTS tersedia
            if msg["role"] == "assistant" and GTTS_AVAILABLE:
                if st.button(f"🔊 Putar Suara #{idx+1}", key=f"audio_btn_{idx}"):
                    try:
                        tts = gTTS(text=msg["content"][:300], lang="id", slow=False)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        st.audio(audio_fp, format="audio/mp3")
                    except Exception as e:
                        st.caption(f"Audio tidak dapat diputar: {e}")

    user_prompt = st.chat_input("Ketikkan pesan bebas atau analisis yang diinginkan...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        if not st.session_state.api_key:
            st.error("Silakan masukkan API Key Gemini Anda di sidebar terlebih dahulu.")
        elif not GENAI_AVAILABLE:
            st.error("Paket google-generativeai belum terpasang di server.")
        else:
            try:
                genai.configure(api_key=st.session_state.api_key)
                
                # Fallback model jika custom nama model belum tersedia di server Google
                active_model = model_choice
                if "3.8" in model_choice or "3.5" in model_choice:
                    active_model = "gemini-2.5-flash"

                model = genai.GenerativeModel(
                    model_name=active_model,
                    system_instruction=SYSTEM_INSTRUCTION
                )

                # Siapkan riwayat chat
                history_contents = []
                for m in st.session_state.messages[:-1]:
                    r = "user" if m["role"] == "user" else "model"
                    history_contents.append({"role": r, "parts": [m["content"]]})

                chat_session = model.start_chat(history=history_contents)
                
                with st.chat_message("assistant"):
                    with st.spinner("AI XTRADE VR sedang merespons..."):
                        response = chat_session.send_message(user_prompt)
                        reply_text = response.text
                        st.markdown(reply_text)
                        
                        # Audio otomatis
                        if GTTS_AVAILABLE:
                            try:
                                tts = gTTS(text=reply_text[:250], lang="id", slow=False)
                                audio_fp = io.BytesIO()
                                tts.write_to_fp(audio_fp)
                                audio_fp.seek(0)
                                st.audio(audio_fp, format="audio/mp3")
                            except Exception:
                                pass

                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                save_data(st.session_state.api_key, st.session_state.messages)

            except Exception as err:
                st.error(f"Gagal memproses pesan: {err}")

# ----------------- TAB 2: PROMPT ARCHITECT -----------------
with tab_prompt:
    st.markdown("<h3 class='gold-shimmer-text'>🎯 Master Prompt Architect</h3>", unsafe_allow_html=True)
    raw_idea = st.text_area("Ide kasar yang ingin diubah menjadi prompt cerdas:")
    target_persona = st.selectbox("Format Output", ["Analisis Pasar & Trading", "Arsitek Pemrograman", "Pakar Bisnis & Negosiasi"])

    if st.button("⚡ Generate Prompt"):
        if not st.session_state.api_key:
            st.error("Isi API Key di sidebar terlebih dahulu.")
        elif not raw_idea:
            st.warning("Masukkan ide Anda.")
        else:
            with st.spinner("Merancang prompt terbaik..."):
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    builder = genai.GenerativeModel("gemini-2.5-flash")
                    query = f"Buatkan prompt detail dan terstruktur tingkat tinggi berdasarkan ide ini: '{raw_idea}' dengan persona '{target_persona}'."
                    res = builder.generate_content(query)
                    st.code(res.text, language="markdown")
                except Exception as ex:
                    st.error(f"Gagal: {ex}")

# ----------------- TAB 3: TEKS KE GAMBAR -----------------
with tab_image:
    st.markdown("<h3 class='gold-shimmer-text'>🎨 Visual Synthesizer</h3>", unsafe_allow_html=True)
    img_prompt = st.text_input("Deskripsi visual:", value="Futuristic gold trading robot standing on glowing charts, hyperrealistic, 8k")
    
    if st.button("🖼️ Buat Gambar Mewah"):
        with st.spinner("Rendering gambar..."):
            encoded = quote(img_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed=88"
            try:
                res = requests.get(url, timeout=30)
                if res.status_code == 200:
                    st.image(res.content, caption=img_prompt, use_container_width=True)
                    st.download_button("💾 Unduh Gambar", data=res.content, file_name="xtrade_render.png", mime="image/png")
                else:
                    st.error("Server gambar sedang sibuk, coba beberapa saat lagi.")
            except Exception as e:
                st.error(f"Timeout: {e}")
