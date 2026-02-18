import chromadb
from chromadb.utils import embedding_functions
import os
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChromaDB - Use global variables for lazy loading
chroma_client = None
collection = None
embedding_func = None

def get_rag_components():
    global chroma_client, collection, embedding_func
    if collection is not None:
        return collection
    
    try:
        logger.info("Initializing ChromaDB...")
        # Use /tmp for Cloud Run as the root filesystem is read-only
        # For local, we can use a persistent directory
        db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        
        # Ensure directory exists
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 1. Try FastEmbed
        try:
            from chromadb.utils.embedding_functions import FastEmbedEmbeddingFunction
            logger.info("Loading FastEmbed model...")
            embedding_func = FastEmbedEmbeddingFunction()
        except Exception as e:
            logger.warning(f"FastEmbed failed ({e}). Using fallback.")
            class MockEmbeddingFunction(embedding_functions.EmbeddingFunction):
                def __call__(self, input: list) -> list:
                    return [[0.0] * 384 for _ in input]
            embedding_func = MockEmbeddingFunction()

        collection_name = "url_knowledge_base"
        try:
            collection = chroma_client.get_collection(name=collection_name, embedding_function=embedding_func)
        except:
            collection = chroma_client.create_collection(name=collection_name, embedding_function=embedding_func)
        
        return collection
    except Exception as e:
        logger.error(f"Failed to initialize RAG components: {e}")
        raise e

def add_documents_to_rag(url: str, chunks: list[str], session_id: str):
    """
    Adds text chunks from a URL to the vector database.
    """
    coll = get_rag_components()
    try:
        if not chunks:
            return
            
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"url": url, "chunk_index": i, "session_id": session_id} for i in range(len(chunks))]
        
        coll.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB.")
    except Exception as e:
        logger.error(f"ChromaDB Error: {e}")
        raise e

def query_rag(query_text: str, n_results: int = 5, session_id: str = None):
    """
    Queries the vector database for relevant content and generates an answer.
    """
    coll = get_rag_components()
    
    # Filter by session_id if provided
    where_filter = {"session_id": session_id} if session_id else None
    
    results = coll.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_filter
    )
    
    documents = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    
    # Context construction
    context_text = "\n\n".join([f"Source ({m.get('url', 'unknown')}): {d}" for d, m in zip(documents, metadatas)])
    
    summary = generate_answer_with_llm(context_text, query_text)
    
    return {
        "context": documents, 
        "metadatas": metadatas,
        "answer": summary
    }

def get_urls(session_id: str) -> list[str]:
    """
    Returns a list of unique URLs ingested by the session_id.
    """
    coll = get_rag_components()
    try:
        results = coll.get(
            where={"session_id": session_id},
            include=["metadatas"]
        )
        
        urls = set()
        if results['metadatas']:
            for meta in results['metadatas']:
                if meta and "url" in meta:
                    urls.add(meta["url"])
        
        return list(urls)
    except Exception as e:
        logger.error(f"Error fetching URLs: {e}")
        return []

def generate_answer_with_llm(context: str, query: str) -> str:
    """
    Generates an answer using a real LLM if available, otherwise falls back.
    """
    if not context:
        return "I couldn't find any relevant information in the provided URLs to answer your question."

    system_prompt = (
        "You are an intelligent assistant. Use the provided context to answer the user's question. "
        "If the answer is not contained in the context, explicitly say that you cannot find the answer in the source material. "
        "Do not make up information. Citation of sources is encouraged if possible."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    # 1. Try Groq (Fastest)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq Error: {e}")

    # 2. Try Google Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    # 3. Try OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")

    # 4. Fallback to basic extraction
    logger.warning("No LLM API keys found or API calls failed. Using fallback extraction.")
    top_result = context.split('\n\n')[0]
    return f"**Note: LLM API keys not found. Showing top search result:**\n\n{top_result}..."
