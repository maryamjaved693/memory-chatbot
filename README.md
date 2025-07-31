# 🧠 AI Memory Chatbot with Mem0 & Groq

This project is an **AI-powered chatbot** built with **Streamlit** that integrates the **Groq API** for intelligent, context-aware responses and **Mem0** for persistent memory storage.  
The chatbot remembers previous conversations and uses them to generate more personalized replies over time.

---

## 🚀 Features
- Persistent conversational memory using **Mem0**
- Context-aware responses powered by **Groq API**
- Real-time chat interface with **Streamlit**
- Ability to view, search, and clear stored memories
- Personalized interactions across multiple chat sessions

---

## 📌 Workflow
1. **API Configuration**: Enter your **Groq API key** and **Mem0 API key** in the sidebar.
2. **Memory Retrieval**: The chatbot retrieves previous conversations from **Mem0**.
3. **Context-Aware Reply**: The chatbot uses both stored memory and your new message to generate a response.
4. **Memory Storage**: The conversation is saved back into Mem0 for future interactions.
5. **Memory Management**: You can search, view, and clear stored memories from the sidebar.

---

## 🛠️ Requirements
- Python 3.8+
- Streamlit
- Groq Python SDK
- Mem0 Python SDK

---

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-memory-chatbot.git
   cd ai-memory-chatbot
