import time
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from chatbot_interface import chatbot_interface
from PIL import Image

# Load environment variables
load_dotenv(find_dotenv(".env"))

def main():
    st.set_page_config(page_title="Multi-Chatbot Application", layout="wide")

    # Load and display the logo
    logo = Image.open("logo.jpg")

    st.markdown("""
    <style>
    .logo-img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #ffffff;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
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
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display the logo in a circular design
    st.markdown('<div class="logo-container"><img src="data:image/png;base64,{}" class="logo-img"></div>'.format(image_to_base64(logo)), unsafe_allow_html=True)

    if 'selected_bot' not in st.session_state:
        st.session_state.selected_bot = None

    if st.session_state.selected_bot is None:
        st.markdown("<h1 class='stHeader'>Choose Your Chatbot</h1>", unsafe_allow_html=True)
        col1, col2 ,col3= st.columns(3)
        
        with col1:
            if st.button("Product Development"):
                st.session_state.selected_bot = "Product Development"
                st.rerun()
        
        with col2:
            if st.button("HR Assistant"):
                st.session_state.selected_bot = "HR Assistant"
                st.rerun()
        with col3:
            if st.button("Chat with PDF"):
                st.session_state.selected_bot = "Chat with Pdf"
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

def image_to_base64(image):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

if __name__ == "__main__":
    main()