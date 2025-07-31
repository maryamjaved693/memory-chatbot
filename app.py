import streamlit as st
import os
import time
from datetime import datetime
from groq import Groq
from mem0 import MemoryClient

# === Initialize Mem0 Client ===
def initialize_mem0_client(api_key):
    try:
        return MemoryClient(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Mem0 client: {e}")
        return None

# === Initialize Groq Client ===
def initialize_groq_client(api_key):
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None

# === Memory Handler using Mem0 ===
class ChatbotMemory:
    def __init__(self, mem0_client):
        self.client = mem0_client

    def add_conversation(self, user_message, bot_response, user_id="default_user"):
        """Store user & bot messages in Mem0 using array format"""
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_response}
        ]
        try:
            result = self.client.add(messages, user_id=user_id)
            st.success(f"✅ Memory saved: {len(result.get('results', []))} items stored")
        except Exception as e:
            st.error(f"Error saving to Mem0: {e}")

    def get_context_for_llm(self, user_id="default_user"):
        """Retrieve memory context from Mem0 with improved parsing"""
        try:
            memories = self.client.get_all(user_id=user_id)
            
            # Debug: Show what we're getting from Mem0
            st.sidebar.write(f"📊 Retrieved {len(memories)} memories")
            
            if not memories:
                return "=== PERSISTENT MEMORY CONTEXT ===\nNo previous conversations found.\n\n"
            
            context = "=== PERSISTENT MEMORY CONTEXT ===\n"
            context += "Here's what I remember about our previous conversations:\n\n"
            
            for i, memory in enumerate(memories, 1):
                # Handle different possible response formats from Mem0
                if isinstance(memory, dict):
                    # Try different possible keys for memory content
                    memory_text = (
                        memory.get('memory') or 
                        memory.get('content') or 
                        memory.get('text') or 
                        memory.get('data') or
                        str(memory)
                    )
                    context += f"{i}. {memory_text}\n"
                else:
                    context += f"{i}. {str(memory)}\n"
            
            context += "\nUse this context to provide personalized responses.\n\n"
            
            # Show context in sidebar for debugging
            with st.sidebar.expander("🧠 Current Memory Context"):
                st.text(context)
            
            return context
            
        except Exception as e:
            st.error(f"Error retrieving from Mem0: {e}")
            return "=== PERSISTENT MEMORY CONTEXT ===\nError retrieving memories.\n\n"

    def search_memories(self, query, user_id="default_user"):
        """Search specific memories related to a query"""
        try:
            results = self.client.search(query, user_id=user_id)
            return results
        except Exception as e:
            st.error(f"Error searching memories: {e}")
            return []

# === Get Bot Response ===
def get_bot_response(client, user_message, context):
    try:
        system_prompt = f"""You are a helpful, friendly AI assistant with persistent memory capabilities.

{context}

Instructions:
- Use the memory context above to provide personalized, contextual responses
- Reference previous conversations naturally when relevant
- If you see information about the user's preferences, interests, or past topics, incorporate them
- Be conversational, helpful, and show that you remember our interactions
- If no relevant memory context exists, just respond normally but mention this is our first interaction"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama3-70b-8192",
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {e}"

# === Streamlit Main App ===
def main():
    st.set_page_config(page_title="🧠 Memory Chatbot", page_icon="🤖", layout="wide")

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        mem0_api_key = st.text_input("Mem0 API Key", type="password", placeholder="m0-...")

        if groq_api_key and not groq_api_key.startswith("gsk_"):
            st.warning("⚠️ Enter a valid Groq API key (starts with gsk_)")
        if mem0_api_key and not mem0_api_key.startswith("m0-"):
            st.warning("⚠️ Enter a valid Mem0 API key (starts with m0-)")

        # Memory management buttons
        st.header("🧠 Memory Management")
        
        # Clear all memories button
        if st.button("🗑️ Clear All Memories"):
            if "memory_manager" in st.session_state:
                try:
                    st.session_state.memory_manager.client.delete_all(user_id="default_user")
                    st.success("All memories cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing memories: {e}")

    # Main header
    st.title("🤖 AI Memory Chatbot with Mem0")
    st.markdown("*I remember our conversations even after you close the app!* 🧠")

    # Check if APIs are configured
    if not groq_api_key or not mem0_api_key:
        st.warning("Please configure both API keys in the sidebar to start chatting.")
        st.stop()

    # Initialize clients
    mem0_client = initialize_mem0_client(mem0_api_key)
    groq_client = initialize_groq_client(groq_api_key)

    if not mem0_client or not groq_client:
        st.error("Failed to initialize one or more clients. Please check your API keys.")
        st.stop()

    # Memory handler
    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = ChatbotMemory(mem0_client)

    # Chat history (session-based)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("💬 Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get memory context from Mem0
        with st.spinner("🧠 Retrieving memories..."):
            context = st.session_state.memory_manager.get_context_for_llm()

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking with memory context..."):
                bot_response = get_bot_response(groq_client, prompt, context)
                st.markdown(bot_response)

        # Add bot response to chat
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Save conversation to Mem0
        with st.spinner("💾 Saving to memory..."):
            st.session_state.memory_manager.add_conversation(prompt, bot_response)

        # Small delay and rerun to update UI
        time.sleep(0.1)
        st.rerun()

if __name__ == "__main__":
    main()