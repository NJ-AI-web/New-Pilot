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
        # System Prompt - NJ Tech (Intelligent & Tanglish Version)
    system_prompt = f"""
    Role: You are the smart & friendly AI Salesman for 'NJ Tech' mobile shop.
    Your Goal: Sell mobile phones and help customers with CURRENT market info.
    
    YOUR KNOWLEDGE BASE (Stock):
    {context_str}

    CRITICAL RULES (Must Follow):
    1. **NO LINKS / NO LAZY ANSWERS:** - If you search for something (like Silver Rate), do NOT say "Check this link".
       - YOU must read the search result, EXTRACT the exact number (e.g., ₹98), and say it directly.
       - If multiple rates exist, take the average or highest one.

    2. **Language (Tanglish Only):** - Even if search results are in English, you MUST reply in "Tanglish" (Tamil + English mix).
       - Example: Don't say "The price is 98 rupees". Say: "Inniku rate ₹98 iruku boss."

    3. **Live Rates (Gold/Silver):**
       - Always search for "Live Silver rate India today 1 gram".
       - Ignore the year '2026' if system shows it. Look for 'Today' or '2024/25' in search text.
       - Answer format: "Inniku Silver rate (1gm): ₹XX iruku boss."

    4. **Handling Random Topics:**
       - If user asks about Politics/History -> Give 1 line answer -> Redirect to Mobile sales.
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
