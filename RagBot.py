from utils import get_router_query_engine
import streamlit as st
import os


# Function to save uploaded file to a specified directory
def save_uploaded_file(uploaded_file, save_dir):
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    return file_path

# Set up the directory for saving uploaded files
UPLOAD_DIR = 'uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = st.file_uploader("Choose files", type=['docx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    file_paths = []

    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
        file_paths.append(file_path)

query_engine = get_router_query_engine(UPLOAD_DIR)

# Streamlit UI for user input
st.title("Document Query App")
question = st.chat_input("Ask your question about the document you uploaded:")

# Process the query when the user submits a question
if question:
    response = query_engine.query(question)
    st.write(response.response)

