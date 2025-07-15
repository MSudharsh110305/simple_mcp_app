import os
import uuid
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import List, Dict, Any, Optional

# ✅ Load Firebase from local JSON file (no base64)
config_path = os.path.join("firebase", "firebase_config.json")
cred = credentials.Certificate(config_path)

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

def get_current_chat_id():
    return st.session_state.get("current_chat_id")

def set_current_chat(chat_id: str):
    st.session_state["current_chat_id"] = chat_id

# ===== CURRENT CHAT MEMORY FUNCTIONS =====

def save_message_to_current_chat(prompt: str, response: str):
    chat_id = get_current_chat_id()
    if not chat_id:
        return
    
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    
    # Get existing chat data
    doc = doc_ref.get()
    if doc.exists:
        chat_data = doc.to_dict()
        history = chat_data.get("history", [])
    else:
        history = []
        chat_data = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "title": "New Chat",
            "history": []
        }
    
    # Add new message
    history.append({
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now()
    })
    
    # Update chat data
    chat_data["history"] = history
    chat_data["updated_at"] = datetime.now()
    
    # Save to Firestore
    doc_ref.set(chat_data)

def load_current_chat_history() -> List[Dict[str, Any]]:
    chat_id = get_current_chat_id()
    if not chat_id:
        return []
    
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("history", [])
    return []

def create_new_chat() -> str:
    chat_id = str(uuid.uuid4())
    session_id = get_session_id()
    
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    doc_ref.set({
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "title": "New Chat",
        "history": []
    })
    
    return chat_id

def get_all_chats() -> List[Dict[str, Any]]:
    session_id = get_session_id()
    
    try:
        docs = db.collection("sessions").document(session_id).collection("chats").order_by("updated_at", direction=firestore.Query.DESCENDING).get()
        
        chats = []
        for doc in docs:
            data = doc.to_dict()
            chats.append({
                "id": doc.id,
                "title": data.get("title", "Untitled Chat"),
                "created_at": data.get("created_at", datetime.now()),
                "updated_at": data.get("updated_at", datetime.now()),
                "message_count": len(data.get("history", []))
            })
        
        return chats
    except Exception as e:
        st.error(f"Error loading chats: {str(e)}")
        return []

def delete_chat(chat_id: str):
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    doc_ref.delete()

def get_chat_title(chat_id: str) -> str:
    if not chat_id:
        return "No Chat Selected"
    
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("title", "Untitled Chat")
    return "Chat Not Found"

def update_chat_title(chat_id: str, new_title: str):
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
    doc_ref.update({
        "title": new_title,
        "updated_at": datetime.now()
    })

# ===== CENTRAL MEMORY FUNCTIONS =====

def save_message_to_central_memory(prompt: str, response: str):
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("central_memory").document("memory")
    
    # Get existing central memory
    doc = doc_ref.get()
    if doc.exists:
        history = doc.to_dict().get("history", [])
    else:
        history = []
    
    # Add new message
    history.append({
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now()
    })
    
    # Keep only last 100 messages in central memory to avoid bloating
    if len(history) > 100:
        history = history[-100:]
    
    # Save to Firestore
    doc_ref.set({
        "history": history,
        "updated_at": datetime.now()
    })

def load_central_memory() -> List[Dict[str, Any]]:
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("central_memory").document("memory")
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("history", [])
    return []

def clear_central_memory():
    session_id = get_session_id()
    doc_ref = db.collection("sessions").document(session_id).collection("central_memory").document("memory")
    doc_ref.delete()

# ===== UTILITY FUNCTIONS =====

def get_memory_stats() -> Dict[str, int]:
    current_chat_count = len(load_current_chat_history())
    central_memory_count = len(load_central_memory())
    total_chats = len(get_all_chats())
    
    return {
        "current_chat_messages": current_chat_count,
        "central_memory_messages": central_memory_count,
        "total_chats": total_chats
    }

def search_chats(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    session_id = get_session_id()
    
    try:
        docs = db.collection("sessions").document(session_id).collection("chats").get()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            chat_id = doc.id
            chat_title = data.get("title", "Untitled Chat")
            history = data.get("history", [])
            
            # Search through messages in this chat
            for message in history:
                if (query.lower() in message["prompt"].lower() or 
                    query.lower() in message["response"].lower()):
                    results.append({
                        "chat_id": chat_id,
                        "chat_title": chat_title,
                        "message": message,
                        "relevance_score": message["prompt"].lower().count(query.lower()) + 
                                         message["response"].lower().count(query.lower())
                    })
        
        # Sort by relevance score (descending) and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    except Exception as e:
        st.error(f"Error searching chats: {str(e)}")
        return []

def export_chat_history(chat_id: Optional[str] = None) -> Dict[str, Any]:
    session_id = get_session_id()
    
    export_data = {
        "session_id": session_id,
        "export_timestamp": datetime.now().isoformat(),
        "chats": [],
        "central_memory": load_central_memory()
    }
    
    if chat_id:
        # Export specific chat
        doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
        doc = doc_ref.get()
        if doc.exists:
            export_data["chats"].append({
                "chat_id": chat_id,
                "data": doc.to_dict()
            })
    else:
        # Export all chats
        docs = db.collection("sessions").document(session_id).collection("chats").get()
        for doc in docs:
            export_data["chats"].append({
                "chat_id": doc.id,
                "data": doc.to_dict()
            })
    
    return export_data

def import_chat_history(import_data: Dict[str, Any]):
    session_id = get_session_id()
    
    try:
        # Import chats
        for chat in import_data.get("chats", []):
            chat_id = chat["chat_id"]
            chat_data = chat["data"]
            
            doc_ref = db.collection("sessions").document(session_id).collection("chats").document(chat_id)
            doc_ref.set(chat_data)
        
        # Import central memory
        central_memory = import_data.get("central_memory", [])
        if central_memory:
            doc_ref = db.collection("sessions").document(session_id).collection("central_memory").document("memory")
            doc_ref.set({
                "history": central_memory,
                "updated_at": datetime.now()
            })
        
        return True
    except Exception as e:
        st.error(f"Error importing chat history: {str(e)}")
        return False

def cleanup_old_chats(days_old: int = 30):
    session_id = get_session_id()
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    try:
        docs = db.collection("sessions").document(session_id).collection("chats").where(
            "updated_at", "<=", cutoff_date
        ).get()
        
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        
        return deleted_count
    except Exception as e:
        st.error(f"Error cleaning up old chats: {str(e)}")
        return 0

# ===== LEGACY COMPATIBILITY FUNCTIONS =====

def save_message_to_memory(prompt: str, response: str):
    save_message_to_current_chat(prompt, response)

def load_conversation_history():
    return load_current_chat_history()

def clear_memory():
    chat_id = get_current_chat_id()
    if chat_id:
        delete_chat(chat_id)