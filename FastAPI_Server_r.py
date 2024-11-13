from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import transformers
import arxiv

# Initialize the FastAPI app with CORS settings
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set appropriate origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j Database Credentials
neo4j_uri = "neo4j://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Neo4j driver
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    app.state.driver = driver
    yield  # Provide access to app's lifespan context
    driver.close()  # Clean up resources on shutdown

app = FastAPI(lifespan=lifespan)

# Request models
class PaperRequest(BaseModel):
    topic: str
    year: Optional[int] = None

class QuestionRequest(BaseModel):
    paper_id: str
    question: str

class ArxivSearchRequest(BaseModel):
    keyword: str
    max_results: Optional[int] = 10

class FutureWorksRequest(BaseModel):
    content: str

# Sample endpoint to test API connection
@app.get("/")
def read_root():
    return {"message": "Welcome to the Academic Research Paper Assistant API!"}

### Paper Search Endpoint ###
@app.post("/search_papers/")
def search_papers(request: PaperRequest):
    """
    Search for papers based on topic and optional year.
    """
    topic = request.topic
    year = request.year
    # Placeholder: Replace with actual search logic (e.g., Arxiv API)
    results = [{"title": f"Sample Paper on {topic}", "year": year or 2023, "id": "paper_id_123"}]
    return {"papers": results}

### Neo4j Paper Query Endpoint ###
@app.post("/query_papers_by_topic_year/")
def query_papers_by_topic_year(request: PaperRequest):
    """
    Query stored papers by topic and year in Neo4j.
    """
    with app.state.driver.session() as session:
        query_str = "MATCH (p:Paper) WHERE 1=1 "
        params = {}

        if request.year:
            query_str += "AND p.year = $year "
            params['year'] = request.year
        if request.topic:
            query_str += "AND p.topic = $topic "
            params['topic'] = request.topic

        query_str += "RETURN p.title AS title, p.year AS year, p.topic AS topic, p.abstract AS abstract, p.authors AS authors"
        result = session.run(query_str, **params)

        papers = [{"title": record["title"], "year": record["year"], "topic": record["topic"], "abstract": record["abstract"], "authors": record["authors"]} for record in result]
        return {"papers": papers}

### Enhanced Question Answering Endpoint ###
@app.post("/enhanced_answer_question/")
def enhanced_answer_question(request: QuestionRequest):
    """
    Answer a question based on the content of a specific paper.
    """
    try:
        inputs = tokenizer(request.question, request.context, return_tensors="pt", truncation=True)
        outputs = qa_model(**inputs)

        # Extract answer span with highest score
        answer_start = outputs.start_logits.argmax()
        answer_end = outputs.end_logits.argmax()
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start: answer_end + 1])
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Store Papers in Neo4j ###
@app.post("/store_paper/")
def store_paper(paper: dict):
    """
    Store paper information in Neo4j database.
    """
    with app.state.driver.session() as session:
        try:
            session.run(
                "MERGE (p:Paper {title: $title, year: $year, id: $id})",
                title=paper['title'],
                year=paper['year'],
                id=paper['id']
            )
            return {"status": "Paper stored successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

### Paper Query by Year ###
@app.get("/query_papers/")
def query_papers(year: int):
    """
    Query papers by publication year.
    """
    with app.state.driver.session() as session:
        result = session.run("MATCH (p:Paper) WHERE p.year = $year RETURN p.title, p.id", year=year)
        papers = [{"title": record["p.title"], "id": record["p.id"]} for record in result]
        return {"papers": papers}

### Simple Question Answering Endpoint ###
@app.post("/answer_question/")
def answer_question(request: QuestionRequest):
    """
    Provide a sample answer to a question about a specific paper.
    """
    paper_id = request.paper_id
    question = request.question
    
    # Placeholder: Replace with actual LLM integration for Q&A
    answer = f"This is a sample answer to '{question}' for paper ID {paper_id}."
    return {"answer": answer}

### ArXiv Search Endpoint ###
@app.post("/arxiv_search/")
def arxiv_search(request: ArxivSearchRequest):
    """
    Search for papers on ArXiv by keyword.
    """
    try:
        search = arxiv.Search(
            query=request.keyword,
            max_results=request.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for result in search.results():
            results.append({
                "title": result.title,
                "summary": result.summary,
                "authors": [author.name for author in result.authors],
                "year": result.published.year,
                "url": result.entry_id
            })
        return {"papers": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Future Work Suggestions Endpoint ###
@app.post("/generate_future_works/")
def generate_future_works(request: FutureWorksRequest):
    """
    Generate future work suggestions based on paper content.
    """
    content = request.content
    # Placeholder for future work suggestions logic
    suggestions = [f"Explore further advancements in {content[:30]}..."]
    return {"suggestions": suggestions}
