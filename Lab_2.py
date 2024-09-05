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
st.title("📄 MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management


if not st.secrets["openai_key"]:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=st.secrets["openai_key"])
    stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say this is a test"}],
            stream=True,
        )
    
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt, .md or .pdf)", type=("txt", "md", "pdf")
    )
    
    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:

        # Process the uploaded file and question.
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension in ['txt', 'md']:
          document = uploaded_file.read().decode()
        elif file_extension == 'pdf':
          document = read_pdf(uploaded_file)
        else:
          st.error("Unsupported file type.")
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)