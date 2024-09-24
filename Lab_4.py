import streamlit as st
from openai import OpenAI
import os
import PyPDF2

__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')

import chromadb
chroma_client = chromadb.PersistentClient(path="~/embeddings")

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

pdf_texts = {}
for file_name in os.listdir('pdfs'):
    file_path = os.path.join('pdfs', file_name)
    pdf_texts[file_name] = read_pdf(file_path)
    add_coll(st.session_state.Lab4_vectorDB, pdf_texts[file_name], file_name, st.session_state.openai_client)

    
topic = st.sidebar.selectbox("Topic", ("Generative AI", "Text Mining", "Data Science Overview"))


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