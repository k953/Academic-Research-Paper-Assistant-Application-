# streamlit_frontend.py
import streamlit as st
import requests

# Set FastAPI server URL
FASTAPI_SERVER_URL = "http://localhost:8000"

# Title of the application
st.title("Academic Research Paper Assistant")

# Sidebar - Paper Search and Storage Options
st.sidebar.header("Paper Search and Storage")

# Input for topic-based search
topic = st.sidebar.text_input("Enter research topic:")
year = st.sidebar.number_input("Publication year (optional):", min_value=1900, max_value=2100, step=1, value=2023)
search_button = st.sidebar.button("Search Papers")

# Paper search and display results
if search_button:
    search_payload = {"topic": topic, "year": int(year)}
    try:
        response = requests.post(f"{FASTAPI_SERVER_URL}/search_papers/", json=search_payload)
        papers = response.json().get("papers", [])
        st.write("### Search Results")
        if papers:
            for paper in papers:
                st.write(f"**Title:** {paper['title']}")
                st.write(f"**Year:** {paper['year']}")
                st.write(f"**ID:** {paper['id']}")
                st.button(f"Store Paper", key=f"store_{paper['id']}", on_click=lambda p=paper: store_paper(p))
        else:
            st.write("No papers found for the given topic and year.")
    except Exception as e:
        st.error(f"Error fetching papers: {e}")

# Function to store paper details in Neo4j database
def store_paper(paper):
    try:
        response = requests.post(f"{FASTAPI_SERVER_URL}/store_paper/", json=paper)
        if response.status_code == 200:
            st.success(f"Paper '{paper['title']}' stored successfully!")
        else:
            st.error("Failed to store paper in database.")
    except Exception as e:
        st.error(f"Error storing paper: {e}")

# Section for Summarization
st.header("Summarize a Research Paper")
content = st.text_area("Enter paper content:")
summarize_button = st.button("Summarize")

if summarize_button:
    try:
        summary_response = requests.post(f"{FASTAPI_SERVER_URL}/summarize/", json={"content": content})
        summary_text = summary_response.json().get("summary")
        st.write("### Summary")
        st.write(summary_text)
    except Exception as e:
        st.error(f"Error summarizing paper: {e}")

# Section for Question Answering
st.header("Ask a Question about a Research Paper")
context = st.text_area("Enter paper content (context):")
question = st.text_input("Enter your question:")
qa_button = st.button("Get Answer")

if qa_button:
    try:
        answer_response = requests.post(f"{FASTAPI_SERVER_URL}/answer_question/", json={"context": context, "question": question})
        answer_text = answer_response.json().get("answer")
        st.write("### Answer")
        st.write(answer_text)
    except Exception as e:
        st.error(f"Error retrieving answer: {e}")

# Sidebar - ArXiv Paper Search
st.sidebar.header("ArXiv Search")
arxiv_keyword = st.sidebar.text_input("Keyword for ArXiv search:")
arxiv_results_button = st.sidebar.button("Search ArXiv")

# ArXiv search functionality
if arxiv_results_button:
    arxiv_payload = {"keyword": arxiv_keyword}
    try:
        response = requests.post(f"{FASTAPI_SERVER_URL}/arxiv_search/", json=arxiv_payload)
        arxiv_papers = response.json().get("papers", [])
        st.write("### ArXiv Search Results")
        if arxiv_papers:
            for paper in arxiv_papers:
                st.write(f"**Title:** {paper['title']}")
                st.write(f"**Authors:** {', '.join(paper['authors'])}")
                st.write(f"**Year:** {paper['year']}")
                st.write(f"[Read more]({paper['url']})")
        else:
            st.write("No papers found for the given keyword.")
    except Exception as e:
        st.error(f"Error fetching ArXiv papers: {e}")

# Sidebar - Database Paper Search
st.sidebar.header("Database Search")
db_topic = st.sidebar.text_input("Topic for database search:")
db_year = st.sidebar.number_input("Year", min_value=1900, max_value=2100, step=1, value=2023)
db_search_button = st.sidebar.button("Search Database")

# Database search functionality
if db_search_button:
    db_query_payload = {"topic": db_topic, "year": int(db_year)}
    try:
        response = requests.post(f"{FASTAPI_SERVER_URL}/query_papers_by_topic_year/", json=db_query_payload)
        db_papers = response.json().get("papers", [])
        st.write("### Database Search Results")
        if db_papers:
            for paper in db_papers:
                st.write(f"**Title:** {paper['title']}")
                st.write(f"**Year:** {paper['year']}")
                st.write(f"**Topic:** {paper['topic']}")
                st.write(f"**Abstract:** {paper['abstract']}")
        else:
            st.write("No papers found.")
    except Exception as e:
        st.error(f"Error querying database: {e}")

# Enhanced Q&A Section
st.header("Enhanced Question Answering")
enhanced_context = st.text_area("Enter paper section (e.g., abstract, conclusion):")
enhanced_question = st.text_input("Ask a question:")
enhanced_qa_button = st.button("Get Enhanced Answer")

if enhanced_qa_button:
    try:
        qa_response = requests.post(f"{FASTAPI_SERVER_URL}/enhanced_answer_question/", json={"context": enhanced_context, "question": enhanced_question})
        answer = qa_response.json().get("answer")
        st.write("### Answer")
        st.write(answer)
    except Exception as e:
        st.error(f"Error retrieving enhanced answer: {e}")

# Future Work Suggestions Section
st.header("Generate Future Work Suggestions")
future_content = st.text_area("Enter paper content for future work suggestions:")
future_work_button = st.button("Generate Suggestions")

if future_work_button:
    try:
        future_response = requests.post(f"{FASTAPI_SERVER_URL}/generate_future_works/", json={"content": future_content})
        suggestions = future_response.json().get("suggestions", [])
        st.write("### Future Work Suggestions")
        for suggestion in suggestions:
            st.write(f"- {suggestion}")
    except Exception as e:
        st.error(f"Error generating future work suggestions: {e}")
