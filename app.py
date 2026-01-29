import streamlit as st
import json
import os
import requests
import asyncio 
import edge_tts 
import random
import pandas as pd
import time 
import re 
from bs4 import BeautifulSoup
from groq import Groq
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 1. PAGE CONFIGURATION & THEME
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="NJ Tech AI Assistant", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# 2. ENHANCED CSS STYLING - Modern & Professional
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* === GLOBAL THEME === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* === MAIN CONTAINER === */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* === CHAT MESSAGES - WhatsApp Style === */
    .stChatMessage {
        background-color: rgba(30, 30, 30, 0.95);
        border-radius: 15px;
        padding: 15px 20px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* User messages (right side feel) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-left: 4px solid #FFD700;
        margin-left: 10%;
    }
    
    /* Assistant messages (left side feel) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background-color: rgba(40, 44, 52, 0.95);
        border-left: 4px solid #00D9FF;
        margin-right: 10%;
    }

    /* === BUTTONS - Modern Glassmorphism === */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: #00D9FF;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 217, 255, 0.3);
    }
    
    /* === QUICK ACTION BUTTONS === */
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    
    div.stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* === SIDEBAR - Dark Glass === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(30, 30, 30, 0.95) 0%, rgba(20, 20, 20, 0.95) 100%);
        backdrop-filter: blur(20px);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* === TEXT INPUTS - Futuristic === */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
        padding: 12px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00D9FF;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
    }

    /* === HEADER STYLING === */
    .main-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 8px;
    }

    /* === STATUS WIDGET === */
    div[data-testid="stStatus"] {
        background: rgba(0, 217, 255, 0.1);
        border-radius: 12px;
        border: 1px solid rgba(0, 217, 255, 0.3);
    }

    /* === DIVIDER === */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        margin: 20px 0;
    }

    /* === DATAFRAME (Admin Panel) === */
    .stDataFrame {
        background: rgba(30, 30, 30, 0.95);
        border-radius: 12px;
        padding: 10px;
    }

    /* === SUCCESS/INFO/WARNING MESSAGES === */
    .stSuccess {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
    }
    
    .stInfo {
        background: rgba(0, 217, 255, 0.2);
        border-left: 4px solid #00D9FF;
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.2);
        border-left: 4px solid #FF9800;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.2);
        border-left: 4px solid #F44336;
    }

    /* === TOGGLE SWITCH === */
    .st-emotion-cache-1wivap2 {
        background-color: rgba(255, 255, 255, 0.1);
    }

    /* === RADIO BUTTONS === */
    div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }

    /* === CHAT INPUT - Bottom Bar === */
    .stChatInputContainer {
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.7);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(118, 75, 162, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3. HEADER WITH ENHANCED DESIGN
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <h1>🤖 NJ Tech AI Assistant</h1>
    <p>🚀 Your Intelligent Mobile Partner | Real-Time Market Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 4. API KEY CONFIGURATION (Unchanged)
# ═══════════════════════════════════════════════════════════════

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.error("🚨 Groq API Key Missing! Check Render Environment Variables.")
        st.stop()

client = Groq(api_key=api_key)

# ═══════════════════════════════════════════════════════════════
# 5. DATA MANAGEMENT FUNCTIONS (Unchanged)
# ═══════════════════════════════════════════════════════════════

@st.cache_data
def load_shop_data():
    data = {}
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if f.endswith(".json"):
                try:
                    with open(os.path.join("data", f), "r", encoding="utf-8") as file:
                        data[f.replace(".json", "")] = json.load(file)
                except: pass
    return data

def load_customers():
    if not os.path.exists("customers.json"): return {}
    try:
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_customer(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

log_file = "chat_logs.json"
def log_interaction(phone, name, query, response):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone, 
        "name": name, 
        "query": query, 
        "response": response[:150]
    }
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except: pass
            
    logs.insert(0, entry)
    
    if len(logs) > 500:
        logs = logs[:500]
        
    with open(log_file, "w", encoding="utf-8") as f: 
        json.dump(logs, f, indent=4)

shop_data = load_shop_data()
customers_db = load_customers()

# ═══════════════════════════════════════════════════════════════
# 6. ENHANCED SIDEBAR WITH BETTER UX
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🎛️ Control Panel")
    st.divider()
    
    # === DEEP SEARCH TOGGLE WITH BETTER EXPLANATION ===
    st.markdown("#### 🕵️‍♂️ Search Mode")
    use_deep_search = st.toggle("Enable Deep Scraping", value=False, key="deep_toggle")
    
    if use_deep_search:
        st.success("✅ **Deep Mode Active**\n\n🔍 Full website content extraction\n⏱️ Slower but more detailed")
    else:
        st.info("⚡ **Quick Mode Active**\n\n📋 Title & snippets only\n⚡ Fast responses")
    
    st.divider()

    # === USER MODE SELECTION ===
    st.markdown("#### 👤 User Authentication")
    mode = st.radio(
        "Select Mode:",
        ["🛍️ Customer", "🔐 Admin / Shop Owner"],
        label_visibility="collapsed"
    )
    
    current_user_name = "Guest"
    phone_input = "Guest"
    user_context = "Guest User"
    
    if mode == "🛍️ Customer":
        st.markdown("##### Customer Login")
        phone_input = st.text_input(
            "📱 Mobile Number:", 
            placeholder="Enter 10 digits",
            max_chars=10
        )
        
        if phone_input and len(phone_input) == 10:
            if phone_input in customers_db:
                # Existing customer
                cust = customers_db[phone_input]
                current_user_name = cust['name']
                
                # Enhanced welcome message
                st.success(f"👋 Welcome back, **{current_user_name}**!")
                
                # Show user stats in expander
                with st.expander("📊 Your Stats"):
                    st.metric("Total Visits", cust.get('visits', 1))
                    st.caption(f"Last Topic: {cust.get('last_topic', 'New User')}")
                
                user_context = f"Name: {cust['name']}, Visits: {cust.get('visits', 1)}, Last: {cust.get('last_topic', 'New')}"
            else:
                # New user registration
                st.info("🆕 New Customer Detected!")
                new_name = st.text_input("✏️ Your Name:", placeholder="Enter full name")
                
                if new_name:
                    if st.button("📝 Register Now", use_container_width=True):
                        customers_db[phone_input] = {
                            "name": new_name,
                            "visits": 1,
                            "history": [],
                            "last_topic": "New Registration",
                            "registered_on": datetime.now().strftime("%Y-%m-%d")
                        }
                        save_customer(customers_db)
                        st.success(f"✅ Welcome {new_name}! Reloading...")
                        time.sleep(1)
                        st.rerun()
                    
    elif mode == "🔐 Admin / Shop Owner":
        st.markdown("##### Admin Authentication")
        pwd = st.text_input("🔑 Password:", type="password", placeholder="Enter admin password")
        
        if pwd == "admin123":
            st.success("🔓 **NJ Master Admin**\n\nFull system access granted")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Logs", use_container_width=True):
                    st.session_state.show_logs = True
            with col2:
                if st.button("🗑️ Clear Logs", use_container_width=True):
                    if os.path.exists(log_file):
                        os.remove(log_file)
                        st.success("Logs cleared!")
                        st.rerun()
                        
        elif pwd == "friend1":
            st.success("🔓 **Shop Owner Access**\n\nMonitoring enabled")
        elif pwd:
            st.error("❌ Invalid password")

    st.divider()
    
    # === QUICK STATS (If Admin) ===
    if mode == "🔐 Admin / Shop Owner" and pwd in ["admin123", "friend1"]:
        st.markdown("#### 📈 Quick Stats")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
                    st.metric("Total Interactions", len(logs))
                    st.metric("Registered Users", len(customers_db))
            except: pass

# ═══════════════════════════════════════════════════════════════
# 7. ADMIN MONITORING DASHBOARD (Enhanced)
# ═══════════════════════════════════════════════════════════════

if mode == "🔐 Admin / Shop Owner" and pwd in ["admin123", "friend1"]:
    if st.session_state.get('show_logs', False):
        st.markdown("## 📊 Live Monitoring Dashboard")
        
        tabs = st.tabs(["📝 Recent Logs", "👥 Customer Database", "📈 Analytics"])
        
        with tabs[0]:
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                        df = pd.DataFrame(logs)
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Logs (CSV)",
                            csv,
                            "nj_tech_logs.csv",
                            "text/csv"
                        )
                except:
                    st.warning("⚠️ Logs file is empty or corrupted")
            else:
                st.info("📭 No interactions recorded yet")
        
        with tabs[1]:
            if customers_db:
                cust_df = pd.DataFrame([
                    {
                        "Phone": phone,
                        "Name": data['name'],
                        "Visits": data.get('visits', 1),
                        "Last Topic": data.get('last_topic', 'N/A')
                    }
                    for phone, data in customers_db.items()
                ])
                st.dataframe(cust_df, use_container_width=True)
            else:
                st.info("👥 No customers registered yet")
        
        with tabs[2]:
            st.markdown("### 📊 System Analytics")
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        logs = json.load(f)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Queries", len(logs))
                        col2.metric("Unique Users", len(set(log['phone'] for log in logs)))
                        col3.metric("Registered Customers", len(customers_db))
                        
                        # Today's activity
                        today = datetime.now().strftime("%Y-%m-%d")
                        today_logs = [log for log in logs if log['timestamp'].startswith(today)]
                        st.metric("Today's Interactions", len(today_logs))
                except: pass
        
        st.stop()  # Don't show chat in admin panel

# ═══════════════════════════════════════════════════════════════
# 8. SEARCH ENGINE FUNCTIONS (Unchanged Logic)
# ═══════════════════════════════════════════════════════════════

def scrape_full_website(url):
    """Full website content extraction"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style", "nav", "footer", "iframe"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:2500]
    except: return ""

def search_internet_custom(query, deep_mode=False):
    try:
        now = datetime.now()
        current_date_str = now.strftime("%d %B %Y")
        
        url = "https://html.duckduckgo.com/html/"
        
        clean_query = query.lower().replace("details", "").replace("sollu", "").replace("search", "")
        search_query = f"{clean_query} latest price review india today news"
        
        payload = {'q': search_query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.post(url, data=payload, headers=headers, timeout=6)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        links_to_scrape = []
        
        for result in soup.find_all('div', class_='result__body', limit=3):
            title_tag = result.find('a', class_='result__a')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                title = title_tag.get_text()
                link = title_tag['href']
                snippet = snippet_tag.get_text()
                
                if deep_mode:
                    links_to_scrape.append(link)
                    results.append(f"📌 Found Source: {title}")
                else:
                    results.append(f"📌 **{title}**\n   - {snippet}\n   - [Link]({link})")
        
        if deep_mode and links_to_scrape:
            full_content = ""
            for i, link in enumerate(links_to_scrape[:2]):
                content = scrape_full_website(link)
                if content:
                    full_content += f"\n\n--- [SOURCE {i+1} CONTENT] ---\n{content}\n"
            return full_content if full_content else "Deep scrape failed. Using snippets."
            
        return "\n".join(results) if results else None
    except: return None

# ═══════════════════════════════════════════════════════════════
# 9. VOICE ENGINE (Unchanged)
# ═══════════════════════════════════════════════════════════════

async def text_to_speech(text):
    clean_text = text.replace("*", "").replace("#", "").replace("📌", "").replace("-", "")
    output_file = "reply.mp3"
    voice = "ta-IN-PallaviNeural"
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(output_file)
    return output_file

# ═══════════════════════════════════════════════════════════════
# 10. AI BRAIN WITH ENHANCED STATUS DISPLAY
# ═══════════════════════════════════════════════════════════════

def get_smart_response(user_query, user_profile, deep_mode):
    shop_context = json.dumps(shop_data, ensure_ascii=False)
    
    now = datetime.now()
    date_str = now.strftime("%d %B %Y")
    day_str = now.strftime("%A")
    
    keywords = [
        "price", "rate", "gold", "petrol", "diesel",
        "best", "top", "list", "suggest", "review",
        "where", "yenga", "shop", "hospital", "construction",
        "company", "contact", "details", "news", "today", "date"
    ]
    
    is_web_needed = any(k in user_query.lower() for k in keywords) or len(user_query) > 15 or deep_mode
    web_context = ""
    
    # === ENHANCED ST
