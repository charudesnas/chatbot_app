import streamlit as st
from google import genai
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬 General Chatbot")

# ── Initialize client (persist across reruns) ────────────────────────────────
if "client" not in st.session_state:
    api_key = st.secrets.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ API key not found. Please set GOOGLE_API_KEY in secrets.")
        st.stop()
    st.session_state.client = genai.Client(api_key=api_key)

# ── Load KB & create chat (only once) ────────────────────────────────────────
if "chat" not in st.session_state:
    kb_path = os.path.join(os.path.dirname(__file__), "general_chatbot_dataset.txt")
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            kb = f.read()
    except FileNotFoundError:
        st.error(f"❌ Knowledge base file not found at {kb_path}")
        st.stop()

    prompt = f"""
You are a general chatbot. Your job is to provide answers based ONLY on the knowledge base below.

Rules:
- Answer politely and clearly
- Only use the information from the KB
- If the answer is not in the KB, say: "I don't have that information in my knowledge base."

Knowledge Base:
{kb}
"""

    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.0-flash",
        config={"system_instruction": prompt},
    )

chat = st.session_state.chat

# ── Message history ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display previous messages ────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ───────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask something..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate response safely
    try:
        response = chat.send_message(user_input)
        reply = response.text
    except ValueError as e:
        reply = f"⚠️ Validation Error: {str(e)}"
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        reply = "⚠️ Unable to generate response. Please try again."

    # Store and display assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
