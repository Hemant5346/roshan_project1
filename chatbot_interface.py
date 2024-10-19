
import streamlit as st
from openai import OpenAI
import streamlit as st
from openai import OpenAI
import os 
from chat_with_gpt import chat_with_gpt
from langchain.chains import ConversationalRetrievalChain
from qdrant_client import QdrantClient
from langchain_community.chat_models import ChatOpenAI
from config import MAX_HISTORY, MAX_MESSAGES
from process_pdf import process_pdf

# Function to initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)
    return None

@st.cache_resource
def get_qdrant_client():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if qdrant_url and qdrant_api_key:
        return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    return None

def chatbot_interface(bot_type):
    st.header(f"{bot_type} Chatbot")

    client = get_openai_client()

    pdf_file = st.file_uploader(f"Upload a PDF for {bot_type} (optional)", type="pdf")

    if pdf_file is not None and not st.session_state.pdf_processed:
        with st.spinner("Processing PDF..."):
            vector_store, collection_name = process_pdf(pdf_file)
            if vector_store is not None and collection_name is not None:
                st.session_state.pdf_processed = True
                st.session_state.collection_name = collection_name
                llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
                st.session_state.pdf_chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=vector_store.as_retriever(),
                    return_source_documents=True
                )
                st.success(f"PDF '{pdf_file.name}' processed successfully! You can now ask questions about its content.")
            else:
                st.error("Failed to process the PDF. Please try again or use a different file.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if len(st.session_state.messages) // 2 >= MAX_MESSAGES:
        st.warning(f"You have reached the maximum limit of {MAX_MESSAGES} messages. Please start a new session.")
    else:
        prompt = st.chat_input(f"Ask {bot_type} a question", key="chat_input")
        if prompt:
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner(f"The {bot_type} is thinking..."):
                response = chat_with_gpt(client, prompt, st.session_state.messages, 
                                         st.session_state.pdf_chain if st.session_state.pdf_processed else None, 
                                         bot_type)

            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            if st.session_state.pdf_processed:
                with st.expander("Relevant PDF sections"):
                    chain_history = [(msg["content"], "") for msg in st.session_state.messages[-MAX_HISTORY:] if msg["role"] == "user"]
                    pdf_response = st.session_state.pdf_chain.invoke({"question": prompt, "chat_history": chain_history})
                    for doc in pdf_response["source_documents"]:
                        st.write(doc.page_content)

    message_count = len(st.session_state.messages) // 2
    st.sidebar.write(f"Message Count: {message_count}/{MAX_MESSAGES}")

    if st.sidebar.button("Start New Session"):
        st.session_state.messages = []
        st.session_state.pdf_processed = False
        st.session_state.collection_name = None
        st.session_state.pdf_chain = None
        st.session_state.selected_bot = None
        st.rerun()