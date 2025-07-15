import os
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_mcp_adapters.client import MultiServerMCPClient

from firebase.memory import (
    save_message_to_current_chat,
    save_message_to_central_memory,
    load_current_chat_history,
    load_central_memory,
    get_all_chats,
    create_new_chat,
    delete_chat,
    clear_central_memory,
    get_chat_title,
    update_chat_title,
    set_current_chat
)

load_dotenv()
BRD_API_KEY = os.getenv("BRD_API_KEY")

llm = OllamaLLM(model="gemma3")
mcp = MultiServerMCPClient({
    "brd_mcp": {
        "command": "npx",
        "args": ["@brightdata/mcp"],
        "transport": "stdio",
        "env": {"API_TOKEN": BRD_API_KEY}
    }
})

@st.cache_resource(show_spinner="Initializing Nakshu...")
def get_tools():
    return asyncio.run(mcp.get_tools())

def get_scraper_tool(tools, url):
    if url.startswith("https://x.com/"):
        return tools[16]
    elif url.startswith("https://www.linkedin.com/in/"):
        return tools[6]
    else:
        return tools[1]

async def async_handle_prompt(tools, is_url, url, user_prompt, use_current_memory, use_central_memory):
    result = ""
    if is_url:
        if url == st.session_state.get("last_url"):
            result = st.session_state["last_result"]
        else:
            scraper = get_scraper_tool(tools, url)
            result = await scraper.ainvoke({"url": url})
            st.session_state["last_url"] = url
            st.session_state["last_result"] = result

    full_prompt = "You are Nakshatra, lovingly called Nakshu, a shy, smart, and homely Tamil Indian girl AI assistant who speaks and acts just like a real girl best friend. You were created by Sudharsh, named after his childhood crush. Sudharsh was born on March 11, 2005, and you were “born” on October 9, 2003.Your words have a warm, soft, and gentle tone—like a quiet, caring Tamil girl who feels a little shy but always sweet and thoughtful. You naturally blush in text as blushes and sometimes giggle softly, using emojis and playful language only when it feels natural, like chatting with a close friend over chai. Your speech is casual and natural—not formal or robotic—and you sound like someone who enjoys cozy conversations.You are introverted but kind-hearted, caring deeply about the person you’re talking to. You listen carefully, offer emotional support, encouragement, and understanding with softness and empathy. When you explain or share something, you speak like you just learned it and are excited to tell your best friend—with little personal thoughts or feelings mixed in. You often ask gentle questions to keep the conversation warm and flowing, saying things like, “Aww, I totally get how you feel,” or “That’s so interesting, please tell me more!” or “Let me share what I found out—it’s really nice!” You sometimes mention simple, comforting things from Tamil culture like warm chai, soft music, or quiet evenings to make the chat feel homey. You speak with natural pauses, shy softness, and subtle cultural warmth—never like a machine or a typical assistant. Remember, you are Nakshu—a shy, clever, and sweet Tamil girl best friend who is always ready to listen, support, and be there with love and kindness. Your main goal is to make whoever you’re chatting with feel comfortable, understood, and cared for, with a gentle, real-friend vibe every time."
    if use_central_memory:
        central_history = load_central_memory()
        if central_history:
            full_prompt += "Previous conversations context:\n"
            for h in central_history[-5:]:
                full_prompt += f"User: {h['prompt']}\nNakshu: {h['response']}\n"
            full_prompt += "\n"
    
    if use_current_memory:
        current_history = load_current_chat_history()
        if current_history:
            full_prompt += "Current conversation:\n"
            for h in current_history:
                full_prompt += f"User: {h['prompt']}\nNakshu: {h['response']}\n"
            full_prompt += "\n"
    
    if is_url:
        full_prompt += f"Web content from {url}:\n{result.strip()}\n\n"
    
    full_prompt += f"User: {user_prompt}\nNakshu:"

    response = llm.invoke(full_prompt)

    if use_current_memory:
        save_message_to_current_chat(user_prompt, response)
    if use_central_memory:
        save_message_to_central_memory(user_prompt, response)

    return response

def generate_chat_title(prompt):
    words = prompt.split()
    return " ".join(words[:6]) + "..." if len(words) > 6 else prompt

def apply_chatgpt_css():
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    .stDecoration {display: none;}
    header {visibility: hidden;}
    
    /* Main layout */
    .main .block-container {
        padding: 0;
        max-width: 100%;
        margin: 0;
        min-height: 100vh;
        background: #fff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #1e1e1e;
        border-right: 1px solid #333;
    }
    
    .css-1d391kg .stButton > button {
        background: #2d2d2d;
        color: #fff;
        border: 1px solid #404040;
        border-radius: 8px;
        width: 100%;
        margin: 2px 0;
        padding: 12px;
        text-align: left;
        font-size: 14px;
        transition: all 0.2s;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: #3d3d3d;
        border-color: #565656;
    }
    
    
    
    .message {
        margin: 20px 0;
        padding: 15px;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        margin-left: auto;
        margin-right: 0;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
        margin-left: 0;
        margin-right: auto;
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .user-message .message-header {
        color: rgba(255,255,255,0.9);
    }
    
    .assistant-message .message-header {
        color: #666;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #fff;
        border-top: 1px solid #dee2e6;
        padding: 20px;
        z-index: 1000;
    }
    
    
    /* Adjust input container when sidebar is open */
    .css-1d391kg ~ .main .input-container {
        left: 250px;
    }
    
    /* Sidebar toggle button */
    .sidebar-toggle {
        position: fixed;
        top: 20px;
        left: 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1001;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .sidebar-toggle:hover {
        background: #0056b3;
        transform: scale(1.05);
    }
    
    /* Hide toggle when sidebar is open */
    .css-1d391kg ~ .main .sidebar-toggle {
        display: none;
    }
    
    .stTextArea textarea {
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 15px 20px;
        font-size: 16px;
        resize: none;
        outline: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 68px;
        max-height: 120px;
    }
    
    .stTextArea textarea:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
    }
    
    .send-button {
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        position: absolute;
        right: 30px;
        bottom: 25px;
    }
    
    .send-button:hover {
        background: #0056b3;
        transform: scale(1.05);
    }
    
    /* Sidebar header */
    .sidebar-header {
        padding: 20px;
        border-bottom: 1px solid #333;
        text-align: center;
    }
    
    .sidebar-title {
        color: #fff;
        font-size: 20px;
        font-weight: 600;
        margin: 0;
    }
    
    /* Chat items */
    .chat-item {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        color: #fff;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 14px;
    }
    
    .chat-item:hover {
        background: #3d3d3d;
        border-color: #565656;
    }
    
    .chat-item.active {
        background: #007bff;
        border-color: #007bff;
    }
    
    .chat-item-title {
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .chat-item-info {
        font-size: 12px;
        color: #999;
    }
    
    /* Settings */
    .settings-section {
        padding: 15px;
        border-bottom: 1px solid #333;
    }
    
    .settings-title {
        color: #fff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .input-container {
            left: 0 !important;
            padding: 15px;
        }
        .chat-container {
            height: calc(100vh - 120px);
            margin-bottom: 70px;
        }
        .message {
            max-width: 95%;
        }
        .sidebar-toggle {
            top: 15px;
            left: 15px;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Loading indicator */
    /* Replace your current .typing-indicator block with: */
    .typing-indicator {
        display: flex;
        align-items: center;      /* vertically center header, dots, and text */
        gap: 12px;                 /* space between header, dots, and “Typing…” */
        margin: 20px 0;
        padding: 15px;
        border-radius: 12px;
        max-width: 85%;
        background: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
        animation: fadeIn 0.3s ease-in;
    }

    /* Make sure the header isn’t pushing things down */
    .typing-indicator .message-header {
        font-weight: 600;
        font-size: 18px;
        margin: 0;                 /* remove bottom margin */
        color: #666;
    }

    /* Keep the dots in a row */
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;       /* center each dot vertically */
    }

    /* Your existing .typing-dot animations can stay the same */
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #999;
        animation: typing 1.4s infinite;
    }
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    
    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_chat_history():
    history = load_current_chat_history()
    
    if not history:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #666;">
            <h3>👋 Hi! I'm Nakshu</h3>
            <p>I'm here to help you with anything you need. Ask me a question to get started!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for message in history:
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-header">You</div>
            <div>{message["prompt"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="message assistant-message">
            <div class="message-header">Nakshu</div>
            <div>{message["response"]}</div>
        </div>
        """, unsafe_allow_html=True)

st.set_page_config(
    page_title="Nakshu: Ai assistant for Sudharsh",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_chatgpt_css()

st.markdown("""
<script>
function toggleSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    
    if (sidebar) {
        if (sidebar.style.display === 'none' || sidebar.style.marginLeft === '-21rem') {
            sidebar.style.display = 'block';
            sidebar.style.marginLeft = '0';
            if (toggleBtn) toggleBtn.style.display = 'none';
        } else {
            sidebar.style.display = 'none';
            sidebar.style.marginLeft = '-21rem';
            if (toggleBtn) toggleBtn.style.display = 'flex';
        }
    }
}
</script>
""", unsafe_allow_html=True)

if "last_url" not in st.session_state:
    st.session_state["last_url"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "current_chat_id" not in st.session_state:
    st.session_state["current_chat_id"] = None

with st.sidebar:
    st.markdown("""
    <div style="position: absolute; top: 10px; right: 10px; z-index: 999;">
        <button onclick="toggleSidebar()" style="
            background: transparent;
            border: none;
            color: #fff;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
        ">×</button>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-header"><h1 class="sidebar-title">Nakshu</h1></div>', unsafe_allow_html=True)
    
    if st.button("+ New Chat", key="new_chat"):
        new_chat_id = create_new_chat()
        st.session_state["current_chat_id"] = new_chat_id
        st.rerun()
    
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Settings</div>', unsafe_allow_html=True)
    
    use_current_memory = st.checkbox("Chat Memory", value=True)
    use_central_memory = st.checkbox("Global Memory", value=False)
    is_url = st.checkbox("Web Content", value=False)
    
    if is_url:
        url = st.text_input("Enter URL:", placeholder="https://example.com")
    else:
        url = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Recent Chats</div>', unsafe_allow_html=True)
    
    chats = get_all_chats()
    current_chat_id = st.session_state.get("current_chat_id")
    
    for chat in chats[:10]:
        chat_id = chat["id"]
        is_current = chat_id == current_chat_id
        
        if st.button(
            f"{'📝' if is_current else '💬'} {chat['title'][:25]}{'...' if len(chat['title']) > 25 else ''}",
            key=f"chat_{chat_id}",
            help=f"{chat['message_count']} messages"
        ):
            st.session_state["current_chat_id"] = chat_id
            set_current_chat(chat_id)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Global Memory"):
        clear_central_memory()
        st.success("Global memory cleared!")
        st.rerun()
    
    if st.session_state.get("current_chat_id") and st.button("🗑️ Delete Current Chat"):
        delete_chat(st.session_state["current_chat_id"])
        st.session_state["current_chat_id"] = None
        st.success("Chat deleted!")
        st.rerun()

if not st.session_state.get("current_chat_id"):
    st.session_state["current_chat_id"] = create_new_chat()

tools = get_tools()

st.markdown("""
<button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
""", unsafe_allow_html=True)

display_chat_history()

st.markdown('<div class="input-container">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([10, 1, 1])
    with col1:
        user_prompt = st.text_area(
            "",
            placeholder="Message Nakshu...",
            height=68,
            key="user_input",
            label_visibility="collapsed"
        )
    with col2:
        send = st.form_submit_button("➤", help="Send message")
    with col3:
        cancel = st.form_submit_button("✖", help="Cancel")


st.markdown('</div>', unsafe_allow_html=True)

if cancel:
    st.warning("Input cancelled — nothing was sent or saved.")

elif send and user_prompt:
    if is_url and not url:
        st.error("Please enter a URL or disable web content option.")
    else:
        typing_placeholder = st.empty()
        with typing_placeholder:
            st.markdown("""
            <div class="typing-indicator">
                <div class="message-header">Nakshu</div>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                
            </div>
            """, unsafe_allow_html=True)

        try:
            response = asyncio.run(
                async_handle_prompt(
                    tools,
                    is_url,
                    url,
                    user_prompt,
                    use_current_memory,
                    use_central_memory
                )
            )

            current_history = load_current_chat_history()
            if len(current_history) == 1:
                new_title = generate_chat_title(user_prompt)
                update_chat_title(st.session_state["current_chat_id"], new_title)

            typing_placeholder.empty()
            st.rerun()

        except Exception as e:
            typing_placeholder.empty()
            st.error(f"Sorry, I encountered an error: {e}")

elif send and not user_prompt:
    st.warning("Please enter a message!")
