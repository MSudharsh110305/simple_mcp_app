import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_mcp_adapters.client import MultiServerMCPClient

from firebase.memory import (
    save_message_to_memory,
    load_conversation_history,
    clear_memory,
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

@st.cache_resource(show_spinner="Loading MCP tools...")
def get_tools():
    return asyncio.run(mcp.get_tools())

def get_scraper_tool(tools, url):
    if url.startswith("https://x.com/"):
        return tools[16]
    elif url.startswith("https://www.linkedin.com/in/"):
        return tools[6]
    else:
        return tools[1]

async def async_handle_prompt(tools, is_url, url, user_prompt, use_memory):
    result = ""
    if is_url:
        if url == st.session_state.get("last_url"):
            result = st.session_state["last_result"]
        else:
            scraper = get_scraper_tool(tools, url)
            result = await scraper.ainvoke({"url": url})
            st.session_state["last_url"] = url
            st.session_state["last_result"] = result

    full_prompt = ""
    if use_memory:
        history = load_conversation_history()
        for h in history:
            full_prompt += f"User: {h['prompt']}\nAI: {h['response']}\n"
    if is_url:
        full_prompt += f"Context:\n{result.strip()}\n\n"
    full_prompt += f"User: {user_prompt}"

    response = llm.invoke(full_prompt)

    if use_memory:
        save_message_to_memory(user_prompt, response)

    return response

st.set_page_config(page_title="🌐 LLM Web Search", layout="centered")
st.title("🌐 LLM Web Search")

if "last_url" not in st.session_state:
    st.session_state["last_url"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

tools = get_tools()

use_memory = st.toggle("🧠 Enable Memory", value=False)
is_url = st.checkbox("Use context from URL?", value=True)
url = st.text_input("Enter URL:", placeholder="https://example.com") if is_url else None
user_prompt = st.text_area("Enter your question")

if st.button("Submit"):
    if not user_prompt:
        st.warning("Please enter a prompt.")
    elif is_url and not url:
        st.warning("Please enter a URL to scrape or uncheck the box.")
    else:
        with st.spinner("Thinking..."):
            response = asyncio.run(
                async_handle_prompt(tools, is_url, url, user_prompt, use_memory)
            )
            st.success("Done!")
            st.markdown("### ✨ Answer:")
            st.write(response)

if use_memory and st.button("❌ Clear Memory"):
    clear_memory()
    st.success("Memory cleared.")
