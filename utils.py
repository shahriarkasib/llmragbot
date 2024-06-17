import openai
from collections import deque
import nest_asyncio
import streamlit as st

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import SummaryIndex, VectorStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool


nest_asyncio.apply()

openai.api_key = st.secrets.openai_api_key   # Replace with your OpenAI API key

def get_doc_tools(uploaded_files):
    try:
        documents = SimpleDirectoryReader(uploaded_files).load_data()

        splitter = SentenceSplitter(chunk_size=1024)
        nodes = splitter.get_nodes_from_documents(documents)

        Settings.llm = OpenAI(model = "gpt-3.5-turbo")
        Settings.embed_model = OpenAIEmbedding(model = "text-embedding-ada-002")

        summary_index = SummaryIndex(nodes)
        vector_index = VectorStoreIndex(nodes)

        summary_query_engine = summary_index.as_query_engine(response_mode = "tree_summarize", use_asynch = True)
        vector_query_engine = vector_index.as_query_engine()

        summary_tool = QueryEngineTool.from_defaults(
                    query_engine = summary_query_engine, 
                    description="Useful for retrieving summary of the documents"
                    )
        vector_tool = QueryEngineTool.from_defaults(
                    query_engine = vector_query_engine, 
                    description="Useful for retrieving specific context from the documents"
                    )
        
        return vector_tool, summary_tool
    except:
        pass
        