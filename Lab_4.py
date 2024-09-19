import streamlit as st
from openai import OpenAI
import os
import PyPDF2

__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')

import chromadb
chroma_client = chromadb.PersistentClient(path="/embeddings")



system_message = '''
You are a bot that always gets a user question, then answer

You then ask "DO YOU WANT MORE INFO".

Keep on asking "DO YOU WANT MORE INFO" after each answer until user say no.

If the user says no, go back to asking the simple question "How can I help you?".

Keep answers short.

Always provide answers that are easy to understand for a "10 Year Old"

If you do no know the answer just state "I DO NOT KNOW"

'''
# Show title and description.
st.title( "MY Lab3 question answering chatbot")

if 'openai_client' not in st.session_state:
    api_key = st.secrets['openai_key']
    st.session_state.openai_client = OpenAI(api_key=api_key)


if 'Lab4_vectorDB' not in st.session_state:
    st.session_state.Lab4_vectorDB = chroma_client.get_or_create_collection('Lab4Collection')

def add_coll(collection, text, filename, client):
    response = client.embeddings.create(
        input = text,
        model = "text-embedding-3-smal"
    )
    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids = [filename],
        embeddings = embedding
    )

def read_pdf(pdf_path):
    
    reader = PyPDF2.PdfReader(pdf_path)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def read_pdfs_from_folder(folder_path):
    pdf_texts = {}
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        pdf_texts[file_name] = read_pdf(file_path)
    return pdf_texts


openai_client = st.session_state.openai_client
response = openai_client.embeddings.create(
    input = topic,
    model = "text-embedding-3-smal"
)

query_embedding = response.data[0].embedding

result = st.session_state.Lab4_vectorDB.query(
    query_embeddings = [query_embedding],
    n_results=3
)

for i in range(len(result['doucments'][0])):
    doc = result['doucments'][0][i]
    doc_id = result['ids'][0]
    st.write(f"The following file/syllabus might be helpful: {doc_id}")