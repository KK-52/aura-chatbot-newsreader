from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

# Local imports
from models import IngestRequest, QueryRequest
import rag_engine
import scraper

app = FastAPI(title="URL RAG System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def ingest_url(request: IngestRequest):
    """
    Scrapes a URL and indexes its content.
    """
    try:
        print(f"Scraping {request.url} for session {request.session_id}...")
        text = scraper.scrape_url(request.url)
        if not text:
            raise HTTPException(status_code=400, detail="No text found on page.")
            
        chunks = scraper.split_text(text)
        print(f"Extracted {len(chunks)} chunks.")
        
        rag_engine.add_documents_to_rag(request.url, chunks, request.session_id)
        
        return {"status": "success", "message": f"Successfully ingested {len(chunks)} chunks from {request.url}"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_data(request: QueryRequest):
    """
    Answers questions based on indexed URLs.
    """
    try:
        result = rag_engine.query_rag(request.query, request.top_k, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8080))
    print(f"Starting server... Access at http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
