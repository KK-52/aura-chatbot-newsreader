from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Local imports
from models import IngestRequest, QueryRequest, User, UserInDB, Token
import rag_engine
import scraper
import auth

app = FastAPI(title="URL RAG System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication ---
# Simple in-memory user storage for demo purposes
# In production, use a database
USERS_DB = {}
USERS_FILE = "users.json"

def load_users():
    global USERS_DB
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                # Convert back to UserInDB objects if needed, but dict is fine for lookup
                USERS_DB = data
        except:
            USERS_DB = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(USERS_DB, f)

load_users()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = USERS_DB.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserInDB(**user_dict)
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=Token)
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(form_data.password)
    user_in_db = UserInDB(username=form_data.username, hashed_password=hashed_password)
    
    USERS_DB[form_data.username] = user_in_db.dict()
    save_users()
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: str = Depends(auth.get_current_user)):
    user_dict = USERS_DB.get(current_user)
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_dict)

# --- Application Routes ---

@app.post("/ingest")
async def ingest_url(request: IngestRequest, current_user: str = Depends(auth.get_current_user)):
    """
    Scrapes a URL and indexes its content. Protected by Auth.
    """
    try:
        # Use authenticated username as session_id
        session_id = current_user
        print(f"Scraping {request.url} for user {session_id}...")
        
        text = scraper.scrape_url(request.url)
        if not text:
            raise HTTPException(status_code=400, detail="No text found on page.")
            
        chunks = scraper.split_text(text)
        print(f"Extracted {len(chunks)} chunks.")
        
        rag_engine.add_documents_to_rag(request.url, chunks, session_id)
        
        return {"status": "success", "message": f"Successfully ingested {len(chunks)} chunks from {request.url}"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_data(request: QueryRequest, current_user: str = Depends(auth.get_current_user)):
    """
    Answers questions based on indexed URLs. Protected by Auth.
    """
    try:
        # Use authenticated username as session_id
        session_id = current_user 
        result = rag_engine.query_rag(request.query, request.top_k, session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/urls")
async def get_session_urls(current_user: str = Depends(auth.get_current_user)):
    """
    Returns a list of URLs ingested by the current user.
    """
    try:
        # We need to implement get_urls in rag_engine
        urls = rag_engine.get_urls(current_user)
        return {"urls": urls}
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
