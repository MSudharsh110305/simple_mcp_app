import os
import uuid
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

config_path = os.path.join("firebase", "firebase_config.json")
cred = credentials.Certificate(config_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

def save_message_to_memory(prompt, response):
    session_id = get_session_id()
    doc_ref = db.collection("conversations").document(session_id)
    doc = doc_ref.get()
    history = doc.to_dict()["history"] if doc.exists else []
    history.append({"prompt": prompt, "response": response})
    doc_ref.set({"history": history})

def load_conversation_history():
    session_id = get_session_id()
    doc = db.collection("conversations").document(session_id).get()
    if doc.exists:
        return doc.to_dict()["history"]
    return []

def clear_memory():
    session_id = get_session_id()
    db.collection("conversations").document(session_id).delete()
