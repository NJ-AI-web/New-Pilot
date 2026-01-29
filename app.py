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

# 1. SETUP & CONFIGURATION ⚙️
st.set_page_config(
    page_title="NJ Tech AI - Ultimate", 
    page_icon="🤖", 
    layout="wide"
)

# Custom CSS for Pro Look & Clean UI
st.markdown("""
<style>
    .stChatMessage { font-family: 'Sans-serif'; }
    .stStatus { font-weight: bold; border-radius: 10px; border: 1px solid #ddd; }
    /* Hide Streamlit Default Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Fetch API Key from Render (os) or Streamlit (secrets)
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.error("🚨 Groq API Key Missing! Render Environment Variables செக் செய்யவும்.")
        st.stop()

client = Groq(api_key=api_key)


# 2. DATA MANAGEMENT (Shop, CRM, Logs) 💾

# A. Shop Data Load
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

# B. Customer CRM Load
def load_customers():
    if not os.path.exists("customers.json"): return {}
    try:
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_customer(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# C. Logging System (Fixed Indentation & Logic)
log_file = "chat_logs.json"
def log_interaction(phone, name, query, response):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone, 
        "name": name, 
        "query": query, 
        "response": response[:150] # 150 எழுத்துகள் மட்டும் சேமிப்போம்
    }
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except: pass
            
    logs.insert(0, entry) # புதுசு மேல வரும்
    
    if len(logs) > 500: # 500 பதிவுகள் வரை மட்டும்
        logs = logs[:500]
        
    with open(log_file, "w", encoding="utf-8") as f: 
        json.dump(logs, f, indent=4)

shop_data = load_shop_data()
customers_db = load_customers()

# 3. SIDEBAR: CONTROLS & LOGIN 🎛️
with st.sidebar:
    st.title("🎛️ NJ Control Panel")
    
    # === DEEP SEARCH TOGGLE ===
    st.write("---")
    use_deep_search = st.toggle("🕵️‍♂️ Enable Deep Search", value=False)
    if use_deep_search:
        st.caption("✅ Deep Mode ON: உள்ளே போய் படிக்கும் (Slow).")
    else:
        st.caption("⚡ Deep Mode OFF: தலைப்பை மட்டும் படிக்கும் (Fast).")
    st.write("---")

    # === LOGIN SYSTEM ===
    mode = st.radio("Select User Mode:", ["Customer", "Admin / Shop Owner"])
    
    current_user_name = "Guest"
    phone_input = "Guest"
    user_context = "Guest User"
    
    if mode == "Customer":
        phone_input = st.text_input("Mobile Number:", placeholder="Enter 10 digit number")
        if phone_input:
            if phone_input in customers_db:
                # Existing User
                cust = customers_db[phone_input]
                current_user_name = cust['name']
                st.success(f"Welcome back, {current_user_name}! 👋")
                user_context = f"Name: {cust['name']}, Last Topic: {cust.get('last_topic', 'New')}"
            else:
                # New User
                st.info("New User Detected!")
                new_name = st.text_input("Enter Your Name:")
                if st.button("Register"):
                    customers_db[phone_input] = {
                        "name": new_name, "visits": 1, 
                        "history": [], "last_topic": "New"
                    }
                    save_customer(customers_db)
                    st.success("Registered! Loading...")
                    st.rerun()
                    
    elif mode == "Admin / Shop Owner":
        pwd = st.text_input("Enter Password:", type="password")
        if pwd == "admin123":
            st.success("🔓 NJ Master Admin Access")
            if st.button("🗑️ Clear Logs"):
                if os.path.exists(log_file): os.remove(log_file)
                st.rerun()
        elif pwd == "friend1":
            st.success("🔓 Shop Owner Access")

# 4. MONITORING DASHBOARD (Admin Only) 📊
if mode == "Admin / Shop Owner" and (pwd == "admin123" or pwd == "friend1"):
    st.title("📊 Live Monitoring Dashboard")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                st.dataframe(pd.DataFrame(json.load(f)), use_container_width=True)
        except: st.warning("Logs file is empty or corrupted.")
    else: st.info("No interactions yet.")
    st.stop() # Admin Panel இல் Chat வரக்கூடாது

# 5. ADVANCED SEARCH ENGINE (Deep + Robust) 🕷️🛡️

def scrape_full_website(url):
    """வெப்சைட்டுக்கு உள்ளே போய் முழு டெக்ஸ்ட்டையும் எடுக்கும்"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # குப்பைகளை நீக்குதல் (Clean Up)
        for script in soup(["script", "style", "nav", "footer", "iframe"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        # Extra spaces நீக்குதல்
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:2500] # 2500 எழுத்துகள் போதும் (Token Save பண்ண)
    except: return ""

def search_internet_custom(query, deep_mode=False):
    try:
        # சிஸ்டம் தேதியை எடுக்கிறோம் (27 Jan 2026 காக)
        now = datetime.now()
        current_date_str = now.strftime("%d %B %Y")
        
        url = "https://html.duckduckgo.com/html/"
        
        # SMART QUERY: 2026ல் இருந்தாலும் "Latest" என்று கேட்டால் தான் 2025 டேட்டா வரும்.
        clean_query = query.lower().replace("details", "").replace("sollu", "").replace("search", "")
        search_query = f"{clean_query} latest price review india today news"
        
        payload = {'q': search_query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Request
        response = requests.post(url, data=payload, headers=headers, timeout=6)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        links_to_scrape = []
        
        # 1. Snippet சேகரிப்பு
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
        
        # 2. Deep Mode Logic (உள்ளே போய் படித்தல்)
        if deep_mode and links_to_scrape:
            full_content = ""
            for i, link in enumerate(links_to_scrape[:2]): # Top 2 Links Only
                content = scrape_full_website(link)
                if content:
                    full_content += f"\n\n--- [SOURCE {i+1} CONTENT] ---\n{content}\n"
            return full_content if full_content else "Deep scrape failed. Use Snippets."
            
        return "\n".join(results) if results else None
    except: return None

# 6. VOICE ENGINE 🎤
async def text_to_speech(text):
    # படிக்க கூடாத குறிகளை நீக்குகிறோம்
    clean_text = text.replace("*", "").replace("#", "").replace("📌", "").replace("-", "")
    output_file = "reply.mp3"
    voice = "ta-IN-PallaviNeural" 
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(output_file)
    return output_file

# 7. THE INTELLIGENT BRAIN (Logic + Date + Motivation) 🧠✨
def get_smart_response(user_query, user_profile, deep_mode):
    shop_context = json.dumps(shop_data, ensure_ascii=False)
    
    # Date Calculation
    now = datetime.now()
    date_str = now.strftime("%d %B %Y")
    day_str = now.strftime("%A")
    
    # Keywords Check (Updated List)
    keywords = [
        "price", "rate", "gold", "petrol", "diesel", 
        "best", "top", "list", "suggest", "review", 
        "where", "yenga", "shop", "hospital", "construction", 
        "company", "contact", "details", "news", "today", "date"
    ]
    
    is_web_needed = any(k in user_query.lower() for k in keywords) or len(user_query) > 15 or deep_mode
    web_context = ""
    
    # === DYNAMIC UI STATUS ===
    status_label = "🚀 NJ AI Starting..."
    with st.status(status_label, expanded=True) as status:
        
        if is_web_needed:
            mode_text = "Deep Scraping (Detailed)" if deep_mode else "Quick Search (Fast)"
            st.write(f"🌍 {mode_text} Mode Active...")
            
            web_data = search_internet_custom(user_query, deep_mode)
            
            if web_data:
                web_context = f"[WEB DATA]:\n{web_data}\n"
                st.write("✅ Data Captured Successfully.")
            else:
                st.write("⚠️ Web Data Not Found. Using Internal Logic.")
        
        st.write("🧠 Reasoning & Formatting...")
        status.update(label="✅ Answer Ready!", state="complete", expanded=False)

    # Motivation Quotes
    quotes = [
        "வெற்றி நிச்சயம்! 💪", "Have a wonderful day! 🌟", 
        "Keep Smiling! 😊", "இன்றைய நாள் இனிதாகட்டும்! 🚀"
    ]
    random_quote = random.choice(quotes)
    
    # Conversation History
    conversation_history = ""
    for msg in st.session_state.messages[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation_history += f"{role}: {msg['content'][:150]}...\n"

    # === SYSTEM PROMPT (The Rules) ===
    system_prompt = f"""
    You are 'NJ Tech AI'. 
    REAL-TIME INFO: Date: {date_str}, Day: {day_str}. User: {user_profile}.
    
    SOURCES:
    1. WEB DATA: {web_context} (Use this for Annapurna, Petrol, Gold).
    2. SHOP DATA: {shop_context} (Use this for Mobile Stocks).
    3. HISTORY: {conversation_history}
    
    RULES:
    1. **NO LAZY LINKS:** Do NOT say "check website". Read the [WEB DATA] and summarize the answer here.
    2. **DATE INTELLIGENCE:** Today is {date_str}. If web data shows "2025", assume it is the latest available info and present it.
    3. **DEEP MODE:** If Deep Mode is ON, give a detailed answer. If OFF, keep it short.
    4. **FORMAT:** Use Headings (###), Bullets (-), and Bold (**).
    5. **ENDING:** End with: "{random_quote}"
    
    User Query: {user_query}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7, max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Server Busy. Please try again later."

# 8. CHAT INTERFACE 💬
st.title(f"🌐 NJ Tech AI")
if current_user_name != "Guest":
    st.caption(f"👤 Logged in as: **{current_user_name}** | 📅 {datetime.now().strftime('%d %b %Y')}")

# Chat History Init
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "வாங்க பாஸ்! நான் ரெடி. என்ன விவரம் வேணும்?"}]

# Print History
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
if prompt := st.chat_input("Ex: Annapurna Nepal History / Petrol Price"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Call AI Brain
    response = get_smart_response(prompt, user_context, use_deep_search)
    
    # Save to CRM & Logs
    if phone_input != "Guest":
        log_interaction(phone_input, current_user_name, prompt, response)
        if phone_input in customers_db:
            customers_db[phone_input]['history'].append(prompt)
            customers_db[phone_input]['last_topic'] = prompt
            customers_db[phone_input]['visits'] = customers_db[phone_input].get('visits', 1) + 1
            save_customer(customers_db)

    # Show Response
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Play Audio
    try:
        if os.path.exists("reply.mp3"): os.remove("reply.mp3")
        asyncio.run(text_to_speech(response))
        st.audio("reply.mp3", format="audio/mp3", start_time=0)

    except: pass
