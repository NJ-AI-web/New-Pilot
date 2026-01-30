import os
import json
import requests
import edge_tts
from bs4 import BeautifulSoup
from datetime import datetime
from groq import Groq
import streamlit as st

# --- 1. SETUP & DATA LOADING ---
def load_shop_data():
    data = {}
    if not os.path.exists("data"):
        os.makedirs("data")
        return data
    try:
        for f in os.listdir("data"):
            if f.endswith(".json"):
                try:
                    with open(os.path.join("data", f), "r", encoding="utf-8") as file:
                        data[f.replace(".json", "")] = json.load(file)
                except: pass 
    except: pass
    return data

def load_customers():
    if not os.path.exists("customers.json"):
        with open("customers.json", "w") as f: json.dump({}, f)
        return {}
    try:
        with open("customers.json", "r") as f: return json.load(f)
    except: return {}

def save_customer(data):
    try:
        with open("customers.json", "w") as f: json.dump(data, f, indent=4)
    except: pass

# --- 2. WEB SEARCH ENGINE ---
def scrape_full_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return soup.get_text(separator=' ')[:2000]
    except: return ""

def search_internet(query, deep_mode=False):
    try:
        url = "https://html.duckduckgo.com/html/"
        payload = {'q': query + " india price details"}
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.post(url, data=payload, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        links = []
        for res in soup.find_all('div', class_='result__body', limit=3):
            try:
                title = res.find('a', class_='result__a').text
                link = res.find('a', class_='result__a')['href']
                snippet = res.find('a', class_='result__snippet').text
                results.append(f"Source: {title}\nSummary: {snippet}")
                links.append(link)
            except: continue
            
        if deep_mode and links:
            extra_content = scrape_full_website(links[0])
            return f"SNIPPETS:\n{str(results)}\n\nDEEP CONTENT:\n{extra_content}"
            
        return "\n".join(results) if results else "No Data Found."
    except: return "Search Error."

# --- 3. AI BRAIN (With MEMORY POWER 🧠) ---
# history parameter சேர்க்கப்பட்டுள்ளது 👇
def ask_bot(query, context_text, history, deep_mode=False):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try: api_key = st.secrets["GROQ_API_KEY"]
        except: return "🚨 Error: API Key Missing!"
    
    client = Groq(api_key=api_key)
    shop_data = load_shop_data()
    web_data = ""
    
    # Internet Search Logic
    search_triggers = ["price", "rate", "gold", "silver", "news", "today", "latest", "review", "best"]
    if any(x in query.lower() for x in search_triggers) or deep_mode:
        web_data = search_internet(query, deep_mode)
    
    date_str = datetime.now().strftime("%d-%b-%Y")
    
    # 🧠 HISTORY FORMATTING (இதுதான் முக்கியம்!)
    # பழைய மெசேஜ்களை AI-க்கு புரியுற மாதிரி மாத்துறோம்
    chat_history_txt = ""
    for msg in history[-5:]: # கடைசி 5 மெசேஜ் மட்டும் போதும்
        role = "User" if msg["role"] == "user" else "Assistant"
        chat_history_txt += f"{role}: {msg['content']}\n"

    # System Prompt Update
    system_prompt = f"""
    Role: You are 'NJ Tech AI', a smart & friendly Mobile Shop Assistant in Erode.
    Today: {date_str}.
    
    CONTEXT DATA:
    1. 🧠 PREVIOUS CHAT HISTORY: 
    {chat_history_txt}
    
    2. 🏪 SHOP STOCK: {json.dumps(shop_data)}
    3. 🌐 WEB DATA: {web_data}
    4. 👤 USER INFO: {context_text}
    
    RULES:
    1. **STABILITY:** Stick to the topic. If user asks "What did we discuss?", look at HISTORY.
    2. **Tanglish:** Speak strictly in Tamil+English mix (Tanglish).
    3. **Direct Answers:** For Gold/Silver rates, give the number directly from WEB DATA.
    4. **Short & Sweet:** Don't give long lectures unless asked.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.6, # குறைக்கப்பட்டது - இது பதிலை Stable ஆக்கும்
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Server Busy Boss. ({str(e)})"

# --- 4. VOICE TTS ---
async def text_to_speech_edge(text):
    try:
        voice = "ta-IN-PallaviNeural"
        output = "reply.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output)
        return output
    except: return None
                
