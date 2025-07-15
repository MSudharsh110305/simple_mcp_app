# == main.py ==

import asyncio
import streamlit as st
from firebase.memory import (
    load_current_chat_history,
    create_new_chat,
    update_chat_title
)
from config import config
from llm_logic import get_tools, async_handle_prompt, generate_chat_title
from ui_styles import apply_chatgpt_css, render_typing_indicator
from ui_components import display_chat_history, render_sidebar, render_input_form, initialize_session_state

def main():
    st.set_page_config(
        page_title="Nakshu: Ai assistant for Sudharsh",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_chatgpt_css()
    
    initialize_session_state()
    
    sidebar_settings = render_sidebar()
    
    if not st.session_state.get("current_chat_id"):
        st.session_state["current_chat_id"] = create_new_chat()
    
    tools = get_tools()
    
    display_chat_history()
    
    user_prompt, send, cancel = render_input_form()
    
    if cancel:
        st.warning("Input cancelled — nothing was sent or saved.")
    
    elif send and user_prompt:
        if sidebar_settings["is_url"] and not sidebar_settings["url"]:
            st.error("Please enter a URL or disable web content option.")
        else:
            typing_placeholder = st.empty()
            with typing_placeholder:
                render_typing_indicator()
            
            try:
                response = asyncio.run(
                    async_handle_prompt(
                        tools,
                        sidebar_settings["is_url"],
                        sidebar_settings["url"],
                        user_prompt,
                        sidebar_settings["use_current_memory"],
                        sidebar_settings["use_central_memory"]
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

if __name__ == "__main__":
    main()
