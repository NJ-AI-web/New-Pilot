/* Main Chat Container */
.stApp {
    background-color: #f5f7f9;
}

/* Chat Message Bubbles */
.stChatMessage {
    padding: 1rem;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* Assistant Bubble (NJ Tech) */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: #ffffff;
    border-left: 5px solid #ff4b4b; /* Brand Color */
}

/* User Bubble */
.stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
    background-color: #e3f2fd;
    border-right: 5px solid #2196f3;
}

/* Title Styling */
h1 {
    color: #ff4b4b;
    font-weight: 700;
    text-align: center;
}

/* Input Box Styling */
.stTextInput input {
    border-radius: 20px;
    border: 2px solid #ddd;
    padding: 10px 15px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #eee;
}
