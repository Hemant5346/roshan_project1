import time
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from chatbot_interface import chatbot_interface


# Load environment variables
load_dotenv(find_dotenv(".env"))
def main():
    st.set_page_config(page_title="Multi-Chatbot Application", layout="wide")

    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .stHeader {
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'selected_bot' not in st.session_state:
        st.session_state.selected_bot = None

    if st.session_state.selected_bot is None:
        st.markdown("<h1 class='stHeader'>Choose Your Chatbot</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Product Development"):
                st.session_state.selected_bot = "Product Development"
                st.rerun()
        
        with col2:
            if st.button("HR Assistant"):
                st.session_state.selected_bot = "HR Assistant"
                st.rerun()
    
    else:
        chatbot_interface(st.session_state.selected_bot)

    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session-{int(time.time())}"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False
        st.session_state.collection_name = None
        st.session_state.pdf_chain = None

if __name__ == "__main__":
    main()