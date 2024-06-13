from utils import get_router_query_engine
import streamlit as st


query_engine = get_router_query_engine("resort data\Accommodation at Serenity Bay Resort.pdf")

# Streamlit UI for user input
st.title("Document Query App")
question = st.chat_input("Ask your question about the document you uploaded:")

# Process the query when the user submits a question
if question:
    response = query_engine.query(question)
    st.write(response.response)

