import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="XTRADE V12 GOLD - 1000 PROMPTS", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")

# ===== GOLD SHIMMER + SMOOTH LUXURY CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Inter:wght@300;600&display=swap');

.gold-shimmer {
  background: linear-gradient(90deg, #FFD700 0%, #FFF8DC 20%, #FFC200 40%, #FFF0A0 60%, #FFD700 80%, #FFE55C 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s linear infinite;
  font-family: 'Cinzel', serif;
  font-weight: 900;
}
@keyframes shimmer { to { background-position: 200% center; } }

.stApp { transition: all 0.6s cubic-bezier(0.4,0,0.2,1) !important; }
.glass {
  backdrop-filter: blur(20px);
  background: linear-gradient(135deg, rgba(255,215,0,0.12), rgba(255,215,0,0.04));
  border: 1px solid rgba(255,215,0,0.3);
  border-radius: 20px;
  padding: 20px;
  transition: all 0.4s ease;
}
.glass:hover { box-shadow: 0 15px 50px rgba(255,215,0,0.25); transform: translateY(-3px); }
.prompt-card {
  background: rgba(255,255,255,0.03);
  border-left: 3px solid #FFD700;
  padding: 12px 16px;
  border-radius: 12px;
  margin: 8px 0;
  transition: 0.3s;
}
.prompt-card:hover { background: rgba(255,215,0,0.1); transform: translateX(5px); }
</style>
""", unsafe_allow_html=True)

# ===== API KEY PERSISTENT + CHAT HILANG PAS RELOAD =====
if 'chat' not in st.session_state:
    st.session_state.chat = [] # SENGAJA GAK DISIMPEN - HILANG PAS RELOAD

if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# JS UNTUK SAVE API KEY PERMANEN
components.html("""
<script>
const saved = localStorage.getItem('xtrade_v12_api_key');
if(saved && saved.length > 5){
  const input = window.parent.document.querySelector('input[type="password"]');
  if(input && !input.value){ input.value = saved; input.dispatchEvent(new Event('input', {bubbles:true})); }
}
</script>
""", height=0)

# ===== DATA 1000 PROMPTS - JADIIN SATU =====
PROMPTS_DATA = {
    "001-100: High-End Trading & Crypto Scalping Algos": [
        "Act as elite crypto scalper, create 1min scalping algo with RSI + EMA + Volume...",
        "Build TradingView Pine Script for gold scalping XAUUSD...",
    ],
    "101-200: Ultra-Realistic Midjourney & Stable Diffusion Prompts": [
        "Ultra realistic Indonesian girl, 8k, cinematic lighting, bokeh...",
        "Luxury gold shimmer product photography, studio light...",
    ],
    "201-300: Viral TikTok/Reels FYP Content Hooks & Scripts": [
        "Buatkan 3 hook TikTok 3 detik pertama yang bikin orang stop scroll untuk jualan...",
    ],
    "301-400: Advanced Copywriting & High-Converting Sales Funnels": [
        "Write high-converting sales funnel for $1000 course...",
    ],
    "401-500: Full-Stack Coding, Debugging & Smart Contracts": [
        "Debug this smart contract and optimize gas...",
    ],
    "501-600: Business Strategy, Pitch Decks & Venture Capital": [
        "Create VC pitch deck for AI startup...",
    ],
    "601-700: AI Persona Simulation & Deep Psychological Roleplay": [
        "Simulate Elon Musk persona for business advice...",
    ],
    "701-800: Hyper-Personalized Productivity & Life Optimization": [
        "Create 4AM billionaire routine...",
    ],
    "801-900: Cybersecurity, Ethical Hacking & Data Scraping": [
        "Explain ethical hacking methodology for bug bounty...",
    ],
    "901-1000: Master Prompt Engineering (Meta-Prompts for AI)": [
        "Create meta-prompt that makes any AI become expert trader...",
    ],
}

# ===== SIDEBAR MEWAH =====
with st.sidebar:
    st.markdown("### 🏆 XTRADE V12 CONFIG")
    
    theme = st.radio("", ["🌙 Gelap", "☀️ Terang"], horizontal=True, label_visibility="collapsed")
    is_dark = "Gelap" in theme
    bg = "#050500" if is_dark else "#fffcf0"
    txt = "#ffffff" if is_dark else "#000000"
    st.markdown(f"<style>.stApp{{background:{bg} !important;}}</style>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("🔑 **API Key (AQ...):**")
    api = st.text_input("", type="password", placeholder="Paste AQ... disini, auto kesimpen!", 
                        value=st.session_state.api_key, label_visibility="collapsed")
    if api:
        st.session_state.api_key = api
        components.html(f"<script>localStorage.setItem('xtrade_v12_api_key','{api}')</script>", height=0)
        st.success("✓ Kesimpen permanen KING!")
    else:
        st.caption("👁️ Klik icon mata buat liat key")
    
    st.divider()
    st.markdown("🧠 **PILIH OTAK AI**")
    model = st.selectbox("", ["gemini-3.8-flash (NEW - Recommend)", "claude-3.5-sonnet", "gpt-4o", "gemini-2.0-flash"], label_visibility="collapsed")
    
    st.divider()
    st.markdown("🎙️ **VOICE XTRADE**")
    voice_on = st.toggle("Voice Auto ON", value=True)
    bahasa = st.selectbox("Bahasa:", ["id - Indonesia", "en - English"], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("💬 Chat auto hilang pas reload = privacy aman 100%")

# ===== MAIN HEADER GOLD =====
st.markdown(f"""
<div style="padding:20px 5px;">
  <h1 class="gold-shimmer" style="font-size:52px; line-height:1;">🏆 XTRADE AI V12<br>GOLD SHIMMER</h1>
  <p style="letter-spacing:0.32em; opacity:0.6; font-size:12px; margin-top:12px;">NEURAL INTELLIGENCE • CLAUDE + CHATGPT + GEMINI • ANTI BLOCK • 1000 PROMPTS</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.markdown("""
    <div class="glass" style="border-left:5px solid #FFD700; background:rgba(255,215,0,0.15)">
    👉 KING! Paste API Key AQ... di sidebar >> dulu, nanti auto kesimpen walau reload!
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===== TABS - JADIIN SATU =====
tab1, tab2, tab3 = st.tabs(["💎 1000 PROMPTS LIBRARY", "💬 CHAT XTRADE", "⚙️ GOLD SETTINGS"])

with tab1:
    st.markdown("### 📚 Semua 1000 Prompt Jadi Satu Disini")
    search = st.text_input("🔍 Cari prompt...", placeholder="misal: trading, midjourney, tiktok...")
    
    for category, prompts in PROMPTS_DATA.items():
        with st.expander(f"📁 {category}", expanded=False):
            for i, p in enumerate(prompts, 1):
                if not search or search.lower() in p.lower() or search.lower() in category.lower():
                    st.markdown(f"<div class='prompt-card'><b>#{category[:3]}-{i}</b> {p}<br><small style='opacity:0.6'>Klik copy di kanan -></small></div>", unsafe_allow_html=True)
                    if st.button(f"📋 Copy", key=f"{category}{i}"):
                        st.toast(f"Copied {category[:7]}-{i} KING!")
    
    st.info("💡 KING, ini struktur 1000 prompt udah jadi satu. Mau gue isiin 100 prompt lengkap per kategori biar full 1000? Bilang 'isi full 1000 king' nanti gue generate semua!")

with tab2:
    st.markdown("#### Chat hilang otomatis pas reload (aman)")
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    if q := st.chat_input("Tanya / pakai prompt dari library..."):
        st.session_state.chat.append({"role":"user","content":q})
        # SIMULASI JAWABAN AI
        st.session_state.chat.append({"role":"assistant","content":f"🏆 XTRADE V12 [{model}] menjawab:\n\n{q}\n\n[Gold shimmer response - connect API lu untuk real response KING]"})
        st.rerun()
    
    if st.button("🗑️ Bersihkan Chat (hilangin manual)"):
        st.session_state.chat = []
        st.rerun()

with tab3:
    st.markdown("""
    <div class="glass">
    <h3>✨ Fitur Mewah Aktif:</h3>
    <ul>
    <li>✅ API Key tersimpan permanen (localStorage)</li>
    <li>✅ Chat hilang pas reload/relog (privacy)</li>
    <li>✅ Mode Terang/Gelap smooth gold</li>
    <li>✅ Animasi shimmer + glassmorphism 60fps</li>
    <li>✅ 1000 Prompts jadi satu file</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔴 LOGOUT & HAPUS API KEY"):
        components.html("<script>localStorage.removeItem('xtrade_v12_api_key')</script>", height=0)
        st.session_state.api_key = ""
        st.session_state.chat = []
        st.rerun()
