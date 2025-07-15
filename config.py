import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

class Config:
    """Configuration class for the application"""
    
    def __init__(self):
        self.BRD_API_KEY = os.getenv("BRD_API_KEY")
        self.llm_model = "gemma3"
        
        self.llm = OllamaLLM(model=self.llm_model)
        
        self.mcp = MultiServerMCPClient({
            "brd_mcp": {
                "command": "npx",
                "args": ["@brightdata/mcp"],
                "transport": "stdio",
                "env": {"API_TOKEN": self.BRD_API_KEY}
            }
        })

config = Config()