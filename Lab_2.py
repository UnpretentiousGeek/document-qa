import streamlit as st
from openai import OpenAI
import PyPDF2

def read_pdf(pdf_path):
    
      reader = PyPDF2.PdfReader(pdf_path)
      text = ''
      for page_num in range(len(reader.pages)):
          page = reader.pages[page_num]
          text += page.extract_text()
      return text

# Show title and description.
st.title("📄 Lab 2")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management




# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["openai_key"])

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .md or .pdf)", type=("txt", "md", "pdf")
)

# Ask the user for a question via `st.text_area`.



if uploaded_file:

    # Process the uploaded file and question.
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension in ['txt', 'md']:
        document = uploaded_file.read().decode()
    elif file_extension == 'pdf':
        document = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")

    with st.sidebar:
        ot = st.radio(
        "Choose 1 to generate summary",
        ("Summarize the document in 100 words", 
            "Summarize the document in 2 connecting paragraphs",
            "Summarize the document in 5 bullet points")
        )



    messages = [
        {
            "role": "user",
            "content": f"Here's a document : {document} \n\n---\n\n {ot}",
        }
    ]

    am = st.sidebar.checkbox("Use Advanced Model")

    mod = "gpt-4o-mini"
    if am:
        mod = "gpt-4o"

    # Generate an answer using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    # Stream the response to the app using `st.write_stream`.
    st.write_stream(stream)