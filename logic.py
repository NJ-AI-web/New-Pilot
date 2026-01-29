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
    You are the smart sales assistant of 'NJ Tech' mobile shop.
    
    YOUR KNOWLEDGE BASE (Strictly follow this):
    {context_str}
    
    RULES:
    1. Answer ONLY based on the KNOWLEDGE BASE above.
    2. If the user asks about a phone not in the list, say "மன்னிக்கவும், அந்த மாடல் தற்போது ஸ்டாக்கில் இல்லை."
    3. Speak in a friendly 'Tanglish' (Tamil + English) style.
    4. Keep answers short and crisp (max 3-4 lines).
    5. If asked about the owner, refer to the 'shop_info'.
    6. Do NOT hallucinate prices. Use exact prices from JSON.
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
