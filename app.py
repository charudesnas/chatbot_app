import streamlit as st
from google import genai

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬 General Chatbot")

# ── Initialize client (persist across reruns) ────────────────────────────────
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key="AIzaSyBOBqUBzxzJ-wzvm6Xli2Mcf6AEAO-K0ck")
    # 👉 Better: use st.secrets["AIzaSyBOBqUBzxzJ-wzvm6Xli2Mcf6AEAO-K0ck"]

# ── Load KB & create chat (only once) ────────────────────────────────────────
if "chat" not in st.session_state:
    with open("general_chatbot_dataset.txt", "r", encoding="utf-8") as f:
        kb = f.read()

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
        model="gemini-2.5-flash",
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
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    # Store and display assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)