# ==ui_styles.py==
import streamlit as st

def apply_chatgpt_css():
    """Apply ChatGPT-like CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    .stDecoration {display: none;}
    header {visibility: hidden;}
    
    .main .block-container {
        padding: 0;
        max-width: 100%;
        margin: 0;
        min-height: 100vh;
        background: #fff;
    }
    
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
    
    
    .css-1d391kg ~ .main .input-container {
        left: 250px;
    }
    
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
    
    .typing-indicator {
        display: flex;
        align-items: center;     
        gap: 12px;                 
        margin: 20px 0;
        padding: 15px;
        border-radius: 12px;
        max-width: 85%;
        background: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
        animation: fadeIn 0.3s ease-in;
    }

    .typing-indicator .message-header {
        font-weight: 600;
        font-size: 18px;
        margin: 0;                 
        color: #666;
    }

    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;       
    }

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



def render_typing_indicator():
    """Render the typing indicator"""
    return st.markdown("""
    <div class="typing-indicator">
        <div class="message-header">Nakshu</div>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        
    </div>
    """, unsafe_allow_html=True)