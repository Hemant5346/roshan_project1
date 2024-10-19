import os
import time
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

# Load environment variables
load_dotenv()

@st.cache_resource
def get_qdrant_client():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url:
        st.error("QDRANT_URL is not set in the environment variables.")
        return None
    if not qdrant_api_key:
        st.error("QDRANT_API_KEY is not set in the environment variables.")
        return None
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        # Test the connection
        client.get_collections()
        return client
    except Exception as e:
        st.error(f"Failed to connect to Qdrant: {str(e)}")
        return None

@st.cache_resource
def process_pdf(pdf_file):
    try:
        with open("temp.pdf", "wb") as f:
            f.write(pdf_file.getbuffer())
        
        loader = PyPDFLoader("temp.pdf")
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        client = get_qdrant_client()
        if client is None:
            raise ValueError("Failed to initialize Qdrant client. Check your environment variables and Qdrant Cloud settings.")
        
        collection_name = f"pdf_{int(time.time())}"
        
        # Create the collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
        
        vector_store = Qdrant(
            client=client,
            collection_name=collection_name,
            embeddings=embeddings,
        )
        
        # Add documents in batches to avoid potential size limits
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            vector_store.add_documents(texts[i:i+batch_size])
        
        st.success(f"PDF processed successfully! Created collection: {collection_name}")
        return vector_store, collection_name
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {str(e)}")
        return None, None