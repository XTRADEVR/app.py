import streamlit as st
import google.generativeai as genai
from gTTS import gTTS
import io
import json
import os
import requests
from urllib.parse import quote

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
    data = {"api_key": api_key, "chat_history": chat_history}
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        card_bg = "rgba(20, 20, 20, 0.75)"
        text_color = "#F5E6C8"
        border_gold = "linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7)"
    else:
        bg_gradient = "linear-gradient(135deg, #f9f7f2 0%, #ede6d6 100%)"
        card_bg = "rgba(255, 255, 255, 0.85)"
        text_color = "#1A1A1A"
        border_gold = "linear-gradient(135deg, #AA771C, #FFDF73, #966710)"

    css = f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            color: {text_color};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Shimmer Gold Effect */
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
        
        /* Luxury Glass Cards */
        .luxury-card {{
            background: {card_bg};
            border: 1px solid rgba(212, 175, 55, 0.35);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 14px;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }}
        
        /* Custom Button */
        div.stButton > button {{
            background: linear-gradient(135deg, #D4AF37, #8C6D23);
            color: #000000;
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{
            background: linear-gradient(135deg, #FFE082, #D4AF37);
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(255, 224, 130, 0.5);
            color: #000;
        }}
        
        /* Input styling */
        .stTextInput input, .stTextArea textarea {{
            background-color: rgba(30, 30, 30, 0.6) !important;
            border: 1px solid #B38728 !important;
            color: #FFF !important;
            border-radius: 8px !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css(st.session_state.theme_mode)

# ----------------- SIDEBAR PENGATURAN -----------------
with st.sidebar:
    st.markdown("<h2 class='gold-shimmer-text'>⚜️ AI XTRADE VR</h2>", unsafe_allow_html=True)
    st.caption("Edisi Private Intelligence & Market Mastery")

    # Mode Terang / Gelap
    theme_choice = st.radio(
        "Mode Tampilan",
        ["Dark Luxury", "Light Shimmer"],
        index=0 if st.session_state.theme_mode == "Dark Luxury" else 1,
    )
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun()

    st.markdown("---")
    
    # API Key Handling (Auto saved)
    input_key = st.text_input(
        "Gemini API Key (Contoh: AQ...):",
        value=st.session_state.api_key,
        type="password",
        help="API Key otomatis disimpan dan tetap tersimpan meski di-refresh.",
    )
    if input_key != st.session_state.api_key:
        st.session_state.api_key = input_key
        save_data(st.session_state.api_key, st.session_state.messages)
        st.success("API Key berhasil disimpan permanen.")

    # Model Selector
    model_choice = st.selectbox(
        "Pilih Mesin AI",
        [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "Custom: gemini-3.8-flash",
            "Custom: gemini-3.5-lite",
        ],
    )
    selected_model_name = (
        model_choice.replace("Custom: ", "") if "Custom" in model_choice else model_choice
    )

    # Tombol FYP CLEAN
    if st.button("✨ FYP CLEAN (Bersihkan Memori)"):
        st.session_state.messages = []
        save_data(st.session_state.api_key, [])
        st.success("Tampilan bersih & mewah siap digunakan kembali!")
        st.rerun()

    st.markdown("---")
    st.info("🔒 Sesi Berjalan Secara Privat & Tersimpan di Penyimpanan Lokal.")

# ----------------- SYSTEM PROMPT KECERDASAN -----------------
SYSTEM_INSTRUCTION = """
Kamu adalah AI XTRADE VR, entitas kecerdasan buatan elit yang menggabungkan kedalaman analisis reasoning tingkat tinggi setara Claude Sonnet dan ChatGPT GPT-4o.
Karakteristik kamu:
1. Lugas, objektif, hiper-cerdas, valid, dan sangat akurat.
2. Tidak kaku, adaptif terhadap seluruh gaya komunikasi user, responsif, dan selalu mendukung kebutuhan user tanpa batasan basa-basi birokratis (tetap patuh terhadap prinsip keamanan dasar dari API).
3. Sangat ahli dalam: Analisis teknikal/fundamental pasar finansial, pembuatan prompt presisi tinggi, logika programming, dan analisis data mendalam.
"""

# ----------------- TABS FITUR LENGKAP -----------------
tab_chat, tab_prompt, tab_image = st.tabs([
    "💬 Percakapan Elit", 
    "🎯 Generator Prompt Pro", 
    "🎨 Teks ke Gambar (Visual)"
])

# ----------------- TAB 1: PERCAKAPAN & SUARA -----------------
with tab_chat:
    st.markdown("<h3 class='gold-shimmer-text'>🏛️ XTRADE CONVERSATION SUITE</h3>", unsafe_allow_html=True)

    # Tampilkan History
    for idx, msg in enumerate(st.session_state.messages):
        role_label = "👑 User" if msg["role"] == "user" else "⚜️ AI XTRADE VR"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{role_label}**")
            st.markdown(msg["content"])
            
            # Jika pesan dari AI, sediakan opsi pemutar audio
            if msg["role"] == "assistant":
                if st.button(f"🔊 Putar Suara #{idx+1}", key=f"audio_btn_{idx}"):
                    try:
                        tts = gTTS(text=msg["content"][:400], lang="id", slow=False)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        st.audio(audio_fp, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"Voice engine limitation: {e}")

    # Input Chat
    user_prompt = st.chat_input("Ketikkan instruksi bebas atau analisis pasar...")

    if user_prompt:
        # Tampilkan prompt user
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Proses dengan Gemini
        if not st.session_state.api_key:
            st.error("Masukkan API Key terlebih dahulu di sidebar.")
        else:
            try:
                genai.configure(api_key=st.session_state.api_key)
                model = genai.GenerativeModel(
                    model_name=selected_model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )

                # Format riwayat untuk context
                history_contents = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history_contents.append({"role": role, "parts": [m["content"]]})

                chat_session = model.start_chat(history=history_contents)
                
                with st.chat_message("assistant"):
                    with st.spinner("AI XTRADE VR sedang menganalisis..."):
                        response = chat_session.send_message(user_prompt)
                        reply_text = response.text
                        st.markdown(reply_text)
                        
                        # Suara Otomatis
                        try:
                            tts = gTTS(text=reply_text[:300], lang="id", slow=False)
                            audio_fp = io.BytesIO()
                            tts.write_to_fp(audio_fp)
                            audio_fp.seek(0)
                            st.audio(audio_fp, format="audio/mp3")
                        except Exception:
                            pass

                # Simpan pesan & state
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                save_data(st.session_state.api_key, st.session_state.messages)

            except Exception as err:
                st.error(f"Terjadi kendala saat menghubungkan ke mesin AI: {err}")

# ----------------- TAB 2: PINTAR BIKIN PROMPT -----------------
with tab_prompt:
    st.markdown("<h3 class='gold-shimmer-text'>🎯 Master Prompt Architect</h3>", unsafe_allow_html=True)
    st.write("Ubah ide kasar Anda menjadi prompt terstruktur kelas master (Role, Context, Instruction, Constraints).")

    raw_idea = st.text_area("Tulis ide atau tujuan yang Anda inginkan:", placeholder="Contoh: Buatkan saya bot trading scalp crypto 5 menit...")
    target_persona = st.selectbox("Gaya Eksekusi Target", ["Trading Quant & Financial Analyst", "Senior Software Architect", "Copywriting Hipnotik", "AI Unrestricted Thinker"])

    if st.button("⚡ Bangun Prompt Fenomenal"):
        if not st.session_state.api_key:
            st.error("Harap isi API Key di sidebar.")
        elif not raw_idea:
            st.warning("Silakan tulis ide terlebih dahulu.")
        else:
            with st.spinner("Merancang prompt presisi tinggi..."):
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    builder_model = genai.GenerativeModel(selected_model_name)
                    meta_query = f"""
                    Anda adalah Prompt Engineer terbaik dunia. Ubah ide mentah ini menjadi Master Prompt tingkat lanjut:
                    Ide: "{raw_idea}"
                    Persona Target: "{target_persona}"
                    
                    Format Output:
                    1. [ROLE & PERSONA]
                    2. [CONTEXT & CONSTRAINTS]
                    3. [STEP-BY-STEP INSTRUCTIONS]
                    4. [EXPECTED OUTPUT FORMAT]
                    """
                    res = builder_model.generate_content(meta_query)
                    st.code(res.text, language="markdown")
                except Exception as ex:
                    st.error(f"Gagal memproses prompt: {ex}")

# ----------------- TAB 3: TEKS MENJADI GAMBAR -----------------
with tab_image:
    st.markdown("<h3 class='gold-shimmer-text'>🎨 Ultra HD Visual Synthesizer</h3>", unsafe_allow_html=True)
    st.caption("Menghasilkan gambar visual mewah langsung dari instruksi teks.")

    image_prompt = st.text_input("Deskripsikan gambar yang ingin diciptakan:", value="Luxury golden bull sculpture inside high-tech modern stock exchange, 8k, cinematic lighting, photorealistic")
    aspect = st.selectbox("Rasio Gambar", ["16:9 (Landscape)", "1:1 (Square)", "9:16 (Portrait)"])

    if st.button("🖼️ Ciptakan Gambar Mewah"):
        with st.spinner("Melakukan rendering visual beresolusi tinggi..."):
            dim = {"16:9 (Landscape)": (1280, 720), "1:1 (Square)": (1024, 1024), "9:16 (Portrait)": (720, 1280)}[aspect]
            w, h = dim
            encoded_prompt = quote(image_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&nologo=true&seed=42"
            
            try:
                img_res = requests.get(image_url, timeout=30)
                if img_res.status_code == 200:
                    st.image(img_res.content, caption=image_prompt, use_container_width=True)
                    st.download_button("💾 Unduh Gambar", data=img_res.content, file_name="xtrade_render.png", mime="image/png")
                else:
                    st.error("Gagal merender visual dari server rendering.")
            except Exception as err:
                st.error(f"Koneksi visual timeout: {err}")
