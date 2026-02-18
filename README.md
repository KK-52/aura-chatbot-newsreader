# Aura RAG - Serverless Real-time Web Intelligence

An AI-powered Retrieval-Augmented Generation (RAG) system that allows users to chat with live web content instantly.

## � Overview

**Aura RAG** solves the "knowledge cutoff" problem of traditional LLMs by enabling real-time ingestion of web pages. It is designed for researchers, developers, and curious users who need to ask questions about up-to-the-minute news, documentation, or articles.

**What problem does it solve?** Static LLMs don't know about events that happened today. Aura RAG scrapes the provided URL, indexes it, and lets you chat with the content immediately.

**Who is it for?** Development teams, news readers, and anyone needing an instant "chat with website" tool.

## ✨ Features

✅ **Live URL Ingestion**: Instantly scrapes, cleans, and chunks content from any public URL.

✅ **Sub-second Latency**: Powered by Groq's LPU inference engine for lightning-fast responses (<300ms).

✅ **Vector Search**: Uses ChromaDB and FastEmbed for efficient semantic search within the documents.

✅ **Serverless & Free**: Optimized to run completely free on **Google Cloud Run** (Scale-to-Zero).

✅ **Robust Scraper**: Handles modern websites with specialized headers and retry logic.

## 🛠 Tech Stack

### Frontend
- HTML5 / CSS3
- Vanilla JavaScript

### Backend
- Python
- FastAPI

### AI/ML
- **LLM**: Llama 3 70B (via Groq)
- **Embeddings**: FastEmbed (Quantized)
- **Vector DB**: ChromaDB

### Infrastructure
- Google Cloud Run
- Docker

## 📂 Project Structure

```bash
aura-rag/
│── main.py                # FastAPI entry point
│── rag_engine.py          # Vector DB & LLM logic
│── scraper.py             # Web scraping module
│── models.py              # Pydantic data models
│── deploy.ps1             # Deployment automation script
│── Dockerfile             # Container configuration
│── requirements.txt       # Python dependencies
│── .env                   # Environment variables (Excluded from git)
│── .gitignore             # Git exclusion rules
│── static/                # Frontend assets
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── README.md              # Documentation
```

## ⚙️ Installation

```bash
# Clone repo
git clone <your-repo-url>

# Go into folder
cd aura-rag

# Env Setup (Create a .env file)
echo "GROQ_API_KEY=your_key" > .env

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py
```

## ▶️ Usage

1.  **Start the Server**: Run `python main.py` or deploy to Cloud Run.
2.  **Open UI**: Navigate to `http://localhost:8080`.
3.  **Ingest Content**: Paste a URL (e.g., a news article) and click "Ingest".
4.  **Chat**: Ask questions about the article in the chat window.

## � Results

-   **Inference Speed**: Reduced from ~3s to **<300ms** using Groq.
-   **Cost**: **$0.00/month** on Google Cloud Run Free Tier.
-   **Accuracy**: High fidelity retrieval using semantic chunking.

### Live Demo
[**Click here to try the Live App**](https://url-rag-service-679178381345.us-central1.run.app)

## 🔮 Future Improvements

-   [ ] Add persistent database storage (PostgreSQL/Supabase).
-   [ ] Support PDF and file upload ingestion.
-   [ ] Multi-URL context window (chat with multiple sites at once).
-   [ ] User authentication system.
