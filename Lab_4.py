import streamlit as st
from openai import OpenAI
import os
import PyPDF2

__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')

import chromadb
chroma_client = chromadb.PersistentClient(path="~/embeddings")

st.title( "MY Lab3 question answering chatbot")


def add_coll(collection, text, filename, client):
    response = client.embeddings.create(
        input = text,
        model = "text-embedding-3-small"
    )
    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids = [filename],
        embeddings = embedding
    )

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def scan():
    pdf_texts = {}
    for file_name in os.listdir('pdfs'):
        file_path = os.path.join('pdfs', file_name)
        pdf_texts[file_name] = read_pdf(file_path)
        add_coll(st.session_state.Lab4_vectorDB, pdf_texts[file_name], file_name, st.session_state.openai_client)

if 'openai_client' not in st.session_state:
    api_key = st.secrets['openai_key']
    st.session_state.openai_client = OpenAI(api_key=api_key)

if 'Lab4_vectorDB' not in st.session_state:
    st.session_state.Lab4_vectorDB = chroma_client.get_or_create_collection('Lab4Collection')

    if 'scanned' not in st.session_state:
        scan()
        st.session_state.scanned = True

topic = st.sidebar.selectbox("Topic", ("Generative AI", "Text Mining", "Data Science Overview"))

openai_client = st.session_state.openai_client
response = openai_client.embeddings.create(
    input = topic,
    model = "text-embedding-3-small"
)

query_embedding = response.data[0].embedding

result = st.session_state.Lab4_vectorDB.query(
    query_embeddings = [query_embedding],
    n_results=3
)

for i in range(len(result['documents'][0])):
    doc = result['documents'][0][i]
    doc_id = result['ids'][0][i]
    st.write(f"The following file/syllabus might be helpful: {doc_id}")


uploaded_file = st.sidebar.file_uploader(
        "Upload a document (.pdf)", type=("pdf")
    )
if st.sidebar.button("+ Add Files"):
    
    if uploaded_file:
        add_coll(st.session_state.Lab4_vectorDB, read_pdf(uploaded_file), uploaded_file.name, st.session_state.openai_client)
        st.success(f"File {uploaded_file.name} has been added to the collection.")
    else:
        st.error("Please upload a file first.")

if st.sidebar.button("Re-Scan"):
    st.write(f"The Collection have {chroma_client.get_or_create_collection('Lab4Collection').count()} files.")

if st.sidebar.button("Delete Collection"):
    st.write(f"The Collection has been successfully deleted")
    ids = st.session_state.Lab4_vectorDB.get(include=["ids"])
    chroma_client.get_or_create_collection('Lab4Collection').delete(ids['ids'])