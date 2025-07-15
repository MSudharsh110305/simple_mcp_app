import streamlit as st
from firebase.memory import (
    load_current_chat_history,
    get_all_chats,
    create_new_chat,
    delete_chat,
    clear_central_memory,
    set_current_chat
)

def display_chat_history():
    """Display the chat history messages"""
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
        # Usermessage
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-header">You</div>
            <div>{message["prompt"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # response
        st.markdown(f"""
        <div class="message assistant-message">
            <div class="message-header">Nakshu</div>
            <div>{message["response"]}</div>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Render the complete sidebar with all components"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h1 class="sidebar-title">Nakshu</h1></div>', unsafe_allow_html=True)
        
        if st.button("+ New Chat", key="new_chat"):
            new_chat_id = create_new_chat()
            st.session_state["current_chat_id"] = new_chat_id
            st.rerun()
        
        # Settings
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
        
        # history
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
        
        # Memory
        if st.button("Clear Global Memory"):
            clear_central_memory()
            st.success("Global memory cleared!")
            st.rerun()
        
        if st.session_state.get("current_chat_id") and st.button("Delete Current Chat"):
            delete_chat(st.session_state["current_chat_id"])
            st.session_state["current_chat_id"] = None
            st.success("Chat deleted!")
            st.rerun()
    
    return {
        "use_current_memory": use_current_memory,
        "use_central_memory": use_central_memory,
        "is_url": is_url,
        "url": url
    }

def render_input_form():
    """Render the chat input form"""
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Chat input form
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
    
    return user_prompt, send, cancel

def initialize_session_state():
    if "last_url" not in st.session_state:
        st.session_state["last_url"] = None
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None
    if "current_chat_id" not in st.session_state:
        st.session_state["current_chat_id"] = None