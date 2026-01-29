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
# Import our logic file
import logic 

# --- 1. PAGE CONFIG & CSS ---
st.set_page_config(page_title="NJ Tech AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern Chat Bubble */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2b313e; 
        border-left: 5px solid #4CAF50;
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #111; 
        border-left: 5px solid #FF5722;
    }
    
    /* Gradient Button */
    div.stButton > button {
        border-radius: 10px;
        background: linear-gradient(90deg, #1E1E1E, #333);
        color: white;
        border: 1px solid #555;
    }
    div.stButton > button:hover {
        border-color: #4CAF50;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR (Login & Settings) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("NJ Tech Control")
    
    # Feature: Deep Search Toggle
    deep_mode = st.toggle("🕵️‍♂️ Deep Search Mode", value=False)
    if deep_mode: st.caption("🔍 Slower but detailed.")
    
    st.divider()
    
    # Mode Selection
    mode = st.radio("Select Mode:", ["🛍️ Customer", "🔐 Admin Panel"])
    
    user_info = "Guest"
    
    # Customer Logic
    if mode == "🛍️ Customer":
        phone = st.text_input("📱 Mobile Number (Optional):")
        if phone:
            db = logic.load_customers()
            if phone in db:
                st.success(f"Welcome back, {db[phone]['name']}!")
                user_info = f"{db[phone]['name']} ({phone})"
            else:
                name = st.text_input("New User? Enter Name:")
                if st.button("Register"):
                    db[phone] = {"name": name, "visits": 1, "history": []}
                    logic.save_customer(db)
                    st.success("Registered!")
                    st.rerun()

# --- 3. MAIN AREA ---

# === ADMIN PANEL MODE ===
if mode == "🔐 Admin Panel":
    st.title("🛠️ Admin Dashboard")
    pwd = st.text_input("Enter Admin Password:", type="password")
    
    if pwd == "admin123": # Password
        st.success("Access Granted ✅")
        
        tab1, tab2, tab3 = st.tabs(["📂 Update Stock", "📝 View Logs", "👥 Customers"])
        
        with tab1:
            st.subheader("Upload Shop Data")
            col1, col2 = st.columns(2)
            with col1:
                st.info("Mobile Json")
                up1 = st.file_uploader("Upload mobile.json", type="json")
                if up1:
                    with open("data/mobile.json", "wb") as f: f.write(up1.getbuffer())
                    st.success("Updated!")
            with col2:
                st.info("Shop Info Json")
                up2 = st.file_uploader("Upload shop_info.json", type="json")
                if up2:
                    with open("data/shop_info.json", "wb") as f: f.write(up2.getbuffer())
                    st.success("Updated!")
                    
        with tab2:
            if os.path.exists("chat_logs.json"):
                st.json(pd.read_json("chat_logs.json").head(10).to_dict())
            else: st.warning("No logs yet.")
            
    elif pwd:
        st.error("Wrong Password!")
    st.stop() # Stop here if Admin

# === CUSTOMER CHAT MODE ===
col_h1, col_h2 = st.columns([1,5])
with col_h1: st.image("https://cdn-icons-png.flaticon.com/512/8943/8943377.png", width=60)
with col_h2: 
    st.title("NJ Tech AI Assistant")
    st.caption("🚀 Best Mobile Shop in Erode | Live Market Rates")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Vanakkam Boss! Enna mobile paakureenga?"}]

# Quick Buttons
c1, c2, c3 = st.columns(3)
if c1.button("📉 Gold/Silver Rate"): st.session_state.messages.append({"role": "user", "content": "Today Gold and Silver rate?"})
if c2.button("📱 Best 5G Mobiles"): st.session_state.messages.append({"role": "user", "content": "Best 5G phones under 20k?"})
if c3.button("📍 Shop Address"): st.session_state.messages.append({"role": "user", "content": "Shop address kudunga"})

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask about Mobile, Price, or Offers..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking..."):
            # Call Logic File
            response = logic.ask_bot(prompt, user_info, deep_mode)
            st.markdown(response)
            
            # Optional: Log the chat
            # logic.log_interaction(user_info, prompt, response) (Optional)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Audio
    audio_file = asyncio.run(logic.text_to_speech_edge(response))
    if audio_file:
        st.audio(audio_file, format="audio/mp3")
        
