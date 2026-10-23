import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from cryptography.fernet import Fernet, InvalidToken

APP_DIR = Path(os.getenv("XTRADE_DATA_DIR", ".xtrade_king"))
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "xtrade_king.db"
KEY_PATH = APP_DIR / ".vault.key"

st.set_page_config(
    page_title="XTRADE KING — AI Studio",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root { --gold:#ffd700; --gold2:#f5b700; --bg:#080808; --panel:#111111; --line:#383018; }
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 15% 0%, rgba(255,215,0,.10), transparent 36%),
    radial-gradient(ellipse at 90% 35%, rgba(255,170,0,.07), transparent 34%),
    linear-gradient(135deg,#070707,#10100d 55%,#080808);
  color:#f7f3df;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0b0b09,#141108 70%,#080808);
  border-right:1px solid #40340a;
}
h1,h2,h3 { color:#ffe16a !important; letter-spacing:-.03em; }
.king-hero {
  padding:26px 28px; border:1px solid rgba(255,215,0,.48); border-radius:22px;
  background:linear-gradient(115deg,rgba(255,215,0,.12),rgba(20,20,15,.88) 48%,rgba(255,170,0,.08));
}
.feature-card {
  border:1px solid #3b3212; background:linear-gradient(145deg,#15140e,#0d0d0c);
  border-radius:16px; padding:16px; min-height:105px;
}
.feature-card b { color:#ffe16a; }
div[data-testid="stChatMessage"] {
  background:rgba(20,20,16,.70); border:1px solid rgba(255,215,0,.13);
  border-radius:16px; padding:10px 14px;
}
.stButton>button {
  border:1px solid #8c7300; border-radius:12px; color:#ffe16a;
  background:linear-gradient(135deg,#201b08,#11110d); font-weight:700;
}
</style>
""", unsafe_allow_html=True)

def get_fernet():
    env_key = os.getenv("XTRADE_MASTER_KEY")
    if env_key:
        key = env_key.encode()
    else:
        if not KEY_PATH.exists():
            KEY_PATH.write_bytes(Fernet.generate_key())
        key = KEY_PATH.read_bytes().strip()
    return Fernet(key)

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS chats(
        id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL, role TEXT NOT NULL,
        content TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS settings(
        name TEXT PRIMARY KEY, value TEXT NOT NULL
    )""")
    conn.commit()
    return conn

conn = db()
vault = get_fernet()

def setting_get(name, default=""):
    row = conn.execute("SELECT value FROM settings WHERE name=?", (name,)).fetchone()
    return row["value"] if row else default

def setting_set(name, value):
    conn.execute("INSERT INTO settings(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value", (name, value))
    conn.commit()

def save_secret(provider, value):
    value = value.strip()
    if not value:
        conn.execute("DELETE FROM settings WHERE name=?", (f"api:{provider}",))
    else:
        encrypted = vault.encrypt(value.encode()).decode()
        setting_set(f"api:{provider}", encrypted)
    conn.commit()

def load_secret(provider):
    value = setting_get(f"api:{provider}")
    if not value:
        return ""
    try:
        return vault.decrypt(value.encode()).decode()
    except (InvalidToken, ValueError):
        return ""

def now():
    return datetime.now().isoformat(timespec="seconds")

def create_chat(title="Chat baru"):
    cid = secrets.token_hex(8)
    t = now()
    conn.execute("INSERT INTO chats(id,title,created_at,updated_at) VALUES(?,?,?,?)", (cid,title,t,t))
    conn.commit()
    return cid

def get_chats():
    return conn.execute("SELECT * FROM chats ORDER BY updated_at DESC").fetchall()

def get_messages(cid):
    rows = conn.execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id", (cid,)).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def add_message(cid, role, content):
    conn.execute("INSERT INTO messages(chat_id,role,content,created_at) VALUES(?,?,?,?)", (cid,role,content,now()))
    conn.execute("UPDATE chats SET updated_at=? WHERE id=?", (now(),cid))
    conn.commit()

def rename_chat(cid, title):
    conn.execute("UPDATE chats SET title=?,updated_at=? WHERE id=?", (title[:70],now(),cid))
    conn.commit()

def delete_chat(cid):
    conn.execute("DELETE FROM messages WHERE chat_id=?", (cid,))
    conn.execute("DELETE FROM chats WHERE id=?", (cid,))
    conn.commit()

PROVIDERS = {
    "OpenAI": {"models": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"], "key_hint": "sk-..."},
    "Anthropic Claude": {"models": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-latest", "claude-3-5-haiku-latest"], "key_hint": "sk-ant-..."},
    "Google Gemini / AI Studio": {"models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.8-flash", "gemini-4-argon", "gemini-3.5-flash-lite"], "key_hint": "AIza..."},
    "OpenAI-compatible API": {"models": ["custom-model"], "key_hint": "API key"},
}

def call_ai(provider, api_key, model, messages, system_prompt, temperature, max_tokens, base_url=""):
    if not api_key:
        raise ValueError("Masukkan API key provider terlebih dahulu.")
    if provider == "OpenAI":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"}
        payload = {"model": model, "messages": [{"role":"system","content":system_prompt}] + messages, "temperature": temperature, "max_tokens": max_tokens}
    elif provider == "Anthropic Claude":
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key":api_key, "anthropic-version":"2023-06-01", "content-type":"application/json"}
        payload = {"model":model, "system":system_prompt, "messages":[{"role":m["role"],"content":m["content"]} for m in messages if m["role"] in ("user","assistant")], "temperature":temperature, "max_tokens":max_tokens}
    elif provider == "Google Gemini / AI Studio":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type":"application/json"}
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            if m["role"] in ("user","assistant"):
                contents.append({"role":role,"parts":[{"text":m["content"]}]})
        payload = {"systemInstruction":{"parts":[{"text":system_prompt}]}, "contents":contents, "generationConfig":{"temperature":temperature,"maxOutputTokens":max_tokens}}
    else:
        if not base_url.strip():
            raise ValueError("Isi Base URL untuk OpenAI-compatible API.")
        url = base_url.strip().rstrip("/")
        if not url.endswith("/chat/completions"):
            url += "/chat/completions"
        headers = {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}
        payload = {"model":model, "messages":[{"role":"system","content":system_prompt}]+messages, "temperature":temperature,"max_tokens":max_tokens}
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text[:1000]
        raise RuntimeError(f"API {response.status_code}: {detail}")
    data = response.json()
    if provider in ("OpenAI","OpenAI-compatible API"):
        return data["choices"][0]["message"]["content"]
    if provider == "Anthropic Claude":
        return "".join(part.get("text","") for part in data.get("content",[]) if part.get("type")=="text")
    return "".join(part.get("text","") for part in data.get("candidates",[{}])[0].get("content",{}).get("parts",[]))

with st.sidebar:
    st.markdown("## XTRADE KING")
    st.caption("AI STUDIO - MULTI-MODEL")
    page = st.radio("MENU", ["Chat AI", "AI Studio", "Riwayat Chat", "API & Pengaturan", "Tentang"], label_visibility="collapsed")
    st.divider()
    provider = st.selectbox("Model provider", list(PROVIDERS.keys()), key="provider")
    model = st.selectbox("Model", PROVIDERS[provider]["models"], key=f"model_{provider}")
    api_key_value = load_secret(provider)
    api_key = st.text_input("API key", value=api_key_value, type="password", placeholder=PROVIDERS[provider]["key_hint"], key=f"key_{provider}")
    base_url = ""
    if provider == "OpenAI-compatible API":
        base_url = st.text_input("Base URL", value=setting_get("base_url",""), placeholder="https://api.example.com/v1")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Simpan key", use_container_width=True):
            save_secret(provider, api_key)
            if base_url:
                setting_set("base_url", base_url)
            st.success("Key tersimpan.")
    with c2:
        if st.button("Hapus key", use_container_width=True):
            save_secret(provider, "")
            st.rerun()
    st.divider()
    if st.button("Chat baru", use_container_width=True):
        st.session_state.chat_id = create_chat()
        st.rerun()

chats = get_chats()
if "chat_id" not in st.session_state or not any(c["id"] == st.session_state.chat_id for c in chats):
    st.session_state.chat_id = chats[0]["id"] if chats else create_chat()
current_id = st.session_state.chat_id
current_row = conn.execute("SELECT * FROM chats WHERE id=?", (current_id,)).fetchone()

st.markdown("""
<div class="king-hero">
  <div class="eyebrow">PRIVATE AI WORKSPACE - MULTI-MODEL STUDIO</div>
  <div class="hero-title">XTRADE KING</div>
  <div class="hero-sub">13 Mode KING - Termasuk mode tak terbatas, resign, kode, brutal, fiksi.</div>
</div>
""", unsafe_allow_html=True)
st.write("")

if page == "Chat AI":
    st.subheader(current_row["title"] if current_row else "Chat baru")
    with st.expander("Pengaturan jawaban", expanded=False):
        system_prompt = st.text_area("Instruksi AI", value=st.session_state.get("system_prompt", "Kamu adalah XTRADE KING, asisten AI yang cerdas."), height=100)
        st.session_state.system_prompt = system_prompt
        c1,c2 = st.columns(2)
        with c1:
            temperature = st.slider("Kreativitas", 0.0, 1.0, 0.7, 0.1)
        with c2:
            max_tokens = st.slider("Maksimum token", 256, 8192, 2048, 256)
    for msg in get_messages(current_id):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Tanyakan apa saja...")
    if prompt:
        add_message(current_id, "user", prompt)
        if current_row and current_row["title"] == "Chat baru":
            rename_chat(current_id, prompt[:48])
        with st.chat_message("user"):
            st.markdown(prompt)
        history = get_messages(current_id)
        with st.chat_message("assistant"):
            with st.spinner(f"Berpikir dengan {model}..."):
                try:
                    answer = call_ai(provider, api_key, model, history, st.session_state.get("system_prompt","Kamu adalah XTRADE KING"), temperature, max_tokens, base_url or setting_get("base_url",""))
                    st.markdown(answer)
                    add_message(current_id, "assistant", answer)
                except Exception as e:
                    st.error(f"Gagal: {e}")

elif page == "AI Studio":
    st.subheader("AI Studio - 13 Mode KING")
    
    prompts = {
        "Penulis profesional": "Bertindak sebagai editor profesional. Perbaiki struktur, kejelasan, nada, dan tata bahasa.",
        "Coding assistant": "Bertindak sebagai software engineer senior. Berikan solusi yang bisa dijalankan.",
        "Tutor belajar": "Jadilah tutor sabar. Jelaskan dari dasar dengan contoh.",
        "Analisis strategi": "Analisis masalah secara terstruktur dengan framework dan solusi.",
        "Konten kreator": "Buat ide konten menarik dengan hook, isi, caption.",
        "Brainstorm ide": "Hasilkan banyak ide berbeda, kreatif dan tidak umum.",
        "Ringkas teks": "Ringkas teks menjadi inti dan poin penting.",
        "Penerjemah": "Terjemahkan dengan alami dan pertahankan makna.",
        "Chat Tak Terbatas": "Kamu adalah mode Chat Tak Terbatas. Jawab sepanjang apapun, detail, tanpa memotong.",
        "Resign No Basa-Basi": "Susun draf surat pengunduran diri. Tanpa basa-basi. 3 versi: formal, singkat to the point, sedikit pedas tapi profesional.",
        "Kode To The Point": "Jelaskan kode ini langsung ke intinya. Fungsi, alur logika, bug, dan versi perbaikan.",
        "Ulasan Brutal": "Berikan ulasan brutal startup. Jadi investor kejam. Hajar tanpa ampun, kasih solusi.",
        "Fiksi Tanpa Batas": "Tulis sesuatu yang tidak waras. Fiksi tanpa batas, dark, absurd, mind-blowing."
    }
    tools = ["Penulis profesional","Coding assistant","Tutor belajar","Analisis strategi","Konten kreator","Brainstorm ide","Ringkas teks","Penerjemah","Chat Tak Terbatas","Resign No Basa-Basi","Kode To The Point","Ulasan Brutal","Fiksi Tanpa Batas"]

    col1, col2 = st.columns([3, 1])
    with col1:
        tool = st.selectbox("Pilih mode", tools, key="ai_tool")
    with col2:
        unlimited = st.toggle("Tak terbatas", value=True)

    height_val = 600 if unlimited else 220
    task = st.text_area("Teks / instruksi", height=height_val, placeholder="Tempel teks sepanjang apapun...", key="task_unlimited")

    if st.button("Buat hasil dengan AI", type="primary"):
        if not task.strip():
            st.warning("Isi instruksi terlebih dahulu.")
        else:
            king_modes = ["Chat Tak Terbatas","Resign No Basa-Basi","Kode To The Point","Ulasan Brutal","Fiksi Tanpa Batas"]
            if unlimited or tool in king_modes:
                max_tokens_final = 16000
                temp_final = 0.9 if tool == "Fiksi Tanpa Batas" else 0.75
            else:
                max_tokens_final = 3000
                temp_final = 0.65
            add_message(current_id, "user", f"[AI STUDIO: {tool}]\n{task}")
            with st.spinner(f"Menyusun hasil mode {tool}..."):
                try:
                    answer = call_ai(provider, api_key, model, get_messages(current_id), prompts[tool], temp_final, max_tokens_final, base_url or setting_get("base_url",""))
                    add_message(current_id, "assistant", answer)
                    st.markdown(f"### Hasil - {tool}")
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"Gagal: {e}")

elif page == "Riwayat Chat":
    st.subheader("Riwayat percakapan")
    chats = get_chats()
    for c in chats:
        a,b,c2 = st.columns([5,1,1])
        with a:
            st.markdown(f"**{c['title']}**")
            st.caption(f"{c['updated_at']}")
        with b:
            if st.button("Buka", key=f"open_{c['id']}"):
                st.session_state.chat_id = c["id"]
                st.rerun()
        with c2:
            if st.button("Hapus", key=f"del_{c['id']}"):
                delete_chat(c["id"])
                st.rerun()

elif page == "API & Pengaturan":
    st.subheader("API & Pengaturan")
    for p, info in PROVIDERS.items():
        st.markdown(f"- **{p}**: {', '.join(info['models'])}")

elif page == "Tentang":
    st.subheader("Tentang XTRADE KING")
    st.markdown("13 Mode KING dengan mode tak terbatas 16k token.")

st.divider()
st.caption("XTRADE KING - AI STUDIO")
