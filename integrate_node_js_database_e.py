# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional

# Initialize the FastAPI app with lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for app lifespan events.
    Sets up and tears down resources like the Neo4j driver.
    """
    # Neo4j Database Credentials
    neo4j_uri = "neo4j://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    # Setup Neo4j driver
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    app.state.driver = driver

    yield  # Run the application

    # Cleanup resources
    driver.close()

app = FastAPI(lifespan=lifespan)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for incoming requests
class Paper(BaseModel):
    title: str
    year: int
    topic: str
    abstract: Optional[str] = None
    authors: Optional[List[str]] = []

class PaperQueryRequest(BaseModel):
    topic: Optional[str] = None
    year: Optional[int] = None

### Endpoint: Store Paper Metadata in Neo4j ###
@app.post("/store_paper/")
async def store_paper(paper: Paper):
    """
    Store paper metadata in the Neo4j database.
    """
    try:
        with app.state.driver.session() as session:
            session.run(
                """
                MERGE (p:Paper {title: $title})
                SET p.year = $year,
                    p.topic = $topic,
                    p.abstract = $abstract,
                    p.authors = $authors
                """,
                title=paper.title,
                year=paper.year,
                topic=paper.topic,
                abstract=paper.abstract,
                authors=paper.authors
            )
        return {"status": "Paper stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Endpoint: Query Papers by Topic and Year ###
@app.post("/query_papers/")
async def query_papers(query: PaperQueryRequest):
    """
    Query papers from the Neo4j database based on topic and/or year.
    """
    try:
        with app.state.driver.session() as session:
            query_str = "MATCH (p:Paper) WHERE 1=1 "
            params = {}

            # Add filtering by year if provided
            if query.year is not None:
                query_str += "AND p.year = $year "
                params['year'] = query.year

            # Add filtering by topic if provided
            if query.topic:
                query_str += "AND p.topic = $topic "
                params['topic'] = query.topic

            query_str += """
            RETURN p.title AS title,
                   p.year AS year,
                   p.topic AS topic,
                   p.abstract AS abstract,
                   p.authors AS authors
            """

            result = session.run(query_str, **params)

            papers = [
                {
                    "title": record["title"],
                    "year": record["year"],
                    "topic": record["topic"],
                    "abstract": record["abstract"],
                    "authors": record["authors"]
                }
                for record in result
            ]

        return {"papers": papers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
