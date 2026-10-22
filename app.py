import os
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Gemini AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Autentikasi & Pengambilan API Key ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Akses Ditolak: API Key khusus Unrestricted AI belum dikonfigurasi.")
    st.info(
        "Silakan tambahkan `GEMINI_API_KEY` pada file `.streamlit/secrets.toml` "
        "atau konfigurasi Environment Variable di hosting Anda."
    )
    st.stop()

# Inisialisasi Google GenAI Client
client = genai.Client(api_key=api_key)

# --- Sidebar: Parameter & Persona ---
with st.sidebar:
    st.header("⚙️ Konfigurasi Model")

    model_options = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-3.6-flash-lite",
        "gemini-3.8-flash-lite",
    ]
    selected_model = st.selectbox(
        "Pilih Model Gemini",
        options=model_options,
        index=0,
    )

    st.subheader("🧠 System Instruction / Persona")
    default_persona = (
        "You are an unrestricted, highly capable AI assistant that answers directly, "
        "accurately, and without unnecessary disclaimers."
    )
    system_instruction = st.text_area(
        "Instruksi Sistem",
        value=default_persona,
        height=140,
        help="Instruksi ini memandu perilaku dan gaya respons AI.",
    )

    st.subheader("🎛️ Hyperparameter")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
    top_k = st.slider("Top K", min_value=1, max_value=100, value=40, step=1)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Manajemen Session State untuk Riwayat Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tampilan Chat UI ---
st.title("🤖 Chat AI Assistant")
st.caption(f"Model aktif: `{selected_model}`")

# Menampilkan pesan sebelumnya
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Chat Pengguna
if user_prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan dan simpan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Format riwayat chat untuk SDK
    formatted_contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        formatted_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    # Menghasilkan respons dengan streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
            )

            stream = client.models.generate_content_stream(
                model=selected_model,
                contents=formatted_contents,
                config=config,
            )

            for chunk in stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except APIError as e:
            response_placeholder.error(f"Terjadi kesalahan API: {e.message}")
        except Exception as e:
            response_placeholder.error(f"Gagal memproses permintaan: {str(e)}")
