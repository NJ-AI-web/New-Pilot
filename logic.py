import os
import json
import requests
import random
import re
import asyncio
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
                except: 
                    pass
    return data

def load_customers():
    if not os.path.exists("customers.json"):
        with open("customers.json", "w") as f: json.dump({}, f)
        return {}
    try:
        with open("customers.json", "r") as f: return json.load(f)
    except: return {}

def save_customer(data):
    with open("customers.json", "w") as f: json.dump(data, f, indent=4)

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
            title = res.find('a', class_='result__a').text
            link = res.find('a', class_='result__a')['href']
            snippet = res.find('a', class_='result__snippet').text
            results.append(f"Source: {title}\nSummary: {snippet}")
            links.append(link)
            
        if deep_mode and links:
            extra_content = scrape_full_website(links[0])
            return f"SNIPPETS:\n{str(results)}\n\nDEEP CONTENT:\n{extra_content}"
            
        return "\n".join(results) if results else "No Data Found."
    except: return "Search Error."

# --- 3. AI BRAIN (The Response Generator) ---
def ask_bot(query, context_text, deep_mode=False):
    # API Key Handling
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try: api_key = st.secrets["GROQ_API_KEY"]
        except: return "🚨 Error: API Key Missing!"
    
    client = Groq(api_key=api_key)
    
    # Contexts
    shop_data = load_shop_data()
    web_data = ""
    
    # Keywords that trigger Internet Search
    search_triggers = ["price", "rate", "gold", "silver", "news", "today", "latest", "review", "best"]
    if any(x in query.lower() for x in search_triggers) or deep_mode:
        web_data = search_internet(query, deep_mode)
    
    date_str = datetime.now().strftime("%d-%b-%Y")
    
    # System Prompt (Tanglish & Rules)
    system_prompt = f"""
    Role: You are 'NJ Tech AI', a friendly Shop Assistant.
    Today: {date_str}.
    
    DATA SOURCES:
    1. SHOP STOCK: {json.dumps(shop_data)}
    2. INTERNET DATA: {web_data}
    3. USER CONTEXT: {context_text}
    
    RULES:
    1. **Tanglish Only:** Speak like a Tamil Nadu shop owner (Tamil + English mix).
       - Bad: "The price is 100."
       - Good: "Rate 100 ruba boss. Quality mass ah irukum."
    2. **Direct Answer:** If you searched for Rate/Price, tell the number directly. DO NOT give links.
    3. **Stock Check:** If user asks for mobile, check SHOP STOCK first.
    4. **Safety:** Don't answer illegal topics.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
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
                    
