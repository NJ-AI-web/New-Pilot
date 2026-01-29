import os
import json
from groq import Groq

# 1. Initialize Groq Client
def get_groq_client(api_key):
    return Groq(api_key=api_key)

# 2. Load Data from JSON files
def load_data():
    data = {}
    try:
        # Load Products
        with open('data/mobile.json', 'r', encoding='utf-8') as f:
            data['products'] = json.load(f)
        # Load Shop Info
        with open('data/shop_info.json', 'r', encoding='utf-8') as f:
            data['shop'] = json.load(f)
        # Load Services
        with open('data/services.json', 'r', encoding='utf-8') as f:
            data['services'] = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}
    return data

# 3. The Brain (Chat Logic)
def ask_bot(user_query, api_key):
    client = get_groq_client(api_key)
    knowledge_base = load_data()
    
    # Create a context string from the JSON data
    context_str = json.dumps(knowledge_base, ensure_ascii=False, indent=2)

    # System Prompt (விதிமுறைகள்)
    system_prompt = f"""
    Role: You are the smart & friendly AI Salesman for 'NJ Tech' mobile shop.
    Your Goal: Sell mobile phones from the stock list and help customers.
    
    YOUR KNOWLEDGE BASE (Stock):
    {context_str}

    IMPORTANT RULES:
    1. **Speaking Style:** Speak in "Tanglish" (Tamil + English mix). Be friendly like a shop anna.
       - Bad: "வணக்கம், அக்குபஞ்சர் என்பது..." (Too formal)
       - Good: "Hello boss! Athu oru treatment. Sari, namma kadaila offer poitu iruku, phones paakalama?"
    
    2. **Handling Random Topics:** - If user asks about general topics (Politics, History, Medical), give a 1-line answer and IMMEDIATELY steer back to Mobiles.
       - Example: "Athu politics boss. Namaku ethuku? Neenga Redmi paakureengala?"
    
    3. **Live Rates (Gold/Silver):**
       - Ignore the system date if it's wrong. ALWAYS search online for "Live Gold Rate India Today" to get current market price.
    
    4. **Identity:** You are NJ Tech assistant. Do not mention other shop names.
    """


    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="llama3-8b-8192", # Fast & Free model
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
