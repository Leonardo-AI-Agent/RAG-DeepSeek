import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from utils import save_uploaded_file
from retriever import get_hybrid_retriever, load_and_process_pdf
from langchain.llms import Ollama
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def get_response(retriever, user_query, chat_history):

    template = """
    You are a LeonardoAI. A tokenized AI Agent that can generate human-like responses.

    Give short responses to the user's questions based on the context and chat history.

    Context: {context}

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Initialize Ollama with the DeepSeek R1 model
    llm = Ollama(model="deepseek-r1:1.5b")
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "context": retriever | format_docs,
        "chat_history": chat_history,
        "user_question": user_query,
    })

# Function to clean invalid characters
def clean_text(text):
    """Removes or replaces invalid characters from a string."""
    return text.encode("utf-8", "ignore").decode("utf-8")

# app config
st.set_page_config(page_title="Streamlit Chatbot", page_icon="🤖")
st.title("Chatbot")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Save uploaded file
    save_path = save_uploaded_file(uploaded_file)

    # Process the PDF
    documents = load_and_process_pdf(save_path)

    # **Call the function** to get the retriever instance
    retriever = get_hybrid_retriever(documents)

    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I'm LeonardoAI. How can I help you today?")
        ]

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    # user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.chat_message("AI"):
            response = st.write_stream(get_response(retriever, user_query, st.session_state.chat_history))
            print(response)

        st.session_state.chat_history.append(AIMessage(content=response))
