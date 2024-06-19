from utils import get_doc_tools
import streamlit as st
import os
import shutil
from pathlib import Path

from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner
from llama_index.llms.openai import OpenAI

from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex


# Set up the directory for saving uploaded files
UPLOAD_DIR = 'uploaded_files'
file_paths = []
# Function to clear the upload directory without deleting it
def clear_upload_dir():
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# Check if this is the first run in this session
if 'initialized' not in st.session_state:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    else:
        clear_upload_dir()
    st.session_state['initialized'] = True
    
# Function to save uploaded file to a specified directory
def save_uploaded_file(uploaded_file, save_dir):
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    return file_path


os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = st.file_uploader("Choose files", type=['docx', 'pdf'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
        file_paths.append(file_path)
        

# Streamlit UI for user input
st.title("Document Query App")
question = st.chat_input("Ask your question about the document you uploaded:")

file_to_tools_dict = {}
      
for file in file_paths:
    print(file)
    vector_tool, summary_tool = get_doc_tools(file, Path(file).stem)
    file_to_tools_dict[file] = [vector_tool, summary_tool]
    
print(file_to_tools_dict) 
all_tools = [t for file in file_paths for t in file_to_tools_dict[file]]
obj_index = ObjectIndex.from_objects(
    all_tools,
    index_cls=VectorStoreIndex,
)



obj_retriever = obj_index.as_retriever(similarity_top_k=3)
if question:
    tools = obj_retriever.retrieve(
        question
    )

    for i in range(0, len(tools)):
        print(tools[i].metadata)

llm = OpenAI(model="gpt-4o", temperature=0)

agent_worker = FunctionCallingAgentWorker.from_tools(
    tool_retriever=obj_retriever,
    llm=llm, 
    system_prompt=""" \
You are an agent designed to answer queries over a set of given documents.
Please always use the tools provided to answer a question. Do not rely on prior knowledge.\

""",
    verbose=True
)
agent = AgentRunner(agent_worker)


# Process the query when the user submits a question
if question:
    response = agent.chat(question)
    st.write(response.response)

