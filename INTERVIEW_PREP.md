# 🎓 Aura RAG: Technical Interview Prep Guide

This document is designed to help you crush technical interviews by deep-diving into your **Aura RAG** project.

---

## 🟢 Level 1: The Basics (What & Why)

**Q: Can you explain the high-level architecture of this project?**
**Your Answer:**
"The user submits a URL. My system **scrapes** the HTML using `BeautifulSoup`, cleans it, and splits it into small semantic **chunks**. These chunks are converted into numerical vectors (embeddings) using a lightweight model and stored in **ChromaDB**. When the user asks a question, I convert their question into a vector, find the most similar chunks (semantic search), and feed those chunks as context to **Llama 3 (via Groq)** to generate the final answer."

**Q: Why did you choose FastAPI over Flask or Django?**
**Your Answer:**
-   **Performance**: It's built on `Starlette` and `Pydantic`, offering high-performance async capabilities (crucial for handling multiple scraping requests).
-   **Type Safety**: Python type hints make code robust and self-documenting.
-   **Auto-Docs**: It generates Swagger UI automatically, which speeds up testing APIs.

**Q: Why use Docker?**
**Your Answer:**
"It solves the 'it works on my machine' problem. By containerizing the app with its specific Python version (3.11-slim) and system dependencies (like `libgomp1`), I ensure it runs exactly the same on my laptop as it does on Google Cloud Run."

---

## 🟡 Level 2: Implementation Details (How)

**Q: How do you handle long articles that exceed the LLM's context window?**
**Your Answer:**
"I implemented a **Chunking Strategy** in `scraper.py`. Instead of feeding the whole text, I split it into 500-word segments. Crucially, I use a **50-word overlap** between chunks. This ensures that context isn't lost if a sentence is split in the middle. I only retrieve the top 5 most relevant chunks (`top_k=5`) to stay well within Llama 3's 8k token limit."

**Q: Explain the 'Scale-to-Zero' feature you mentioned in the README.**
**Your Answer:**
"I deployed this on **Google Cloud Run**, which is a serverless platform. It automatically spins up a container when a request comes in and spins it down to zero when idle. This means I pay **$0.00** when no one is using the app, unlike a traditional EC2 instance that costs money 24/7."

**Q: How does the vector search find relevant info?**
**Your Answer:**
"It serves as a **Semantic Search** engine. It doesn't just match keywords (like Ctrl+F). It calculates the **Cosine Similarity** between the question's vector and the document vectors. If the vectors point in the same direction in the high-dimensional space, they are semantically similar—even if they don't share the exact same words (e.g., 'dog' and 'canine')."

---

## 🔴 Level 3: Advanced System Design (Scaling & Optimization)

**Q: Your valid chunks are stored in memory. What happens if the container restarts?**
**Your Answer:**
"Currently, ChromaDB is configured to use the ephemeral file system (`/tmp` in Cloud Run), so data is lost on restart. This is intentional for a demo. To scale this for production, I would simply switch the ChromaDB client to connect to a persistent external database like **Pinecone**, **Weaviate**, or a **PostgreSQL (pgvector)** instance."

**Q: Scraping is slow. How would you handle 10,000 requests per second?**
**Your Answer:**
"I would decouple the ingestion from the user response:
1.  **Async Queue**: The `/ingest` endpoint would just push a job to a queue (like **RabbitMQ** or **Google Pub/Sub**) and return 'Processing started'.
2.  **Worker Pool**: A separate fleet of worker containers would pick up jobs, scrape, and embed in the background.
3.  **Webhooks/Polling**: The frontend would poll for status or receive a webhook when ingestion is done."

**Q: Why Groq? Why not just use OpenAI?**
**Your Answer:**
"Latency. OpenAI's GPT-4 can take 3-10 seconds for a response. Groq uses **LPUs (Language Processing Units)**, which are deterministic hardware chips designed specifically for linear algebra (matrix multiplication). This allows them to generate **300-500 tokens/second**, making the chat feel instant (real-time)."

---

## ☠️ Level 4: "Impossible" / Deep Technical Dive

**Q: Explain "Temperature" in LLMs mathematically. What technically happens when you set it to 0 vs 1?**
**Your Answer:**
"LLMs predict the next token by outputting a probability distribution (logits) for every word in the vocabulary. The final step is a **Softmax function**.
Temperature ($T$) scales these logits ($z_i$) before Softmax:
$$P_i = \frac{\exp(z_i / T)}{\sum \exp(z_j / T)}$$
-   **Low Temp ($T \to 0$)**: Makes the distribution 'sharper'. The most likely word gets nearly 100% probability. This makes the model **deterministic** and focused (good for factual Q&A).
-   **High Temp ($T \to 1$)**: Flattens the distribution. Less likely words get a higher chance of being picked during sampling. This increases **creativity** but also the risk of hallucinations."

**Q: How does `Top-P` (Nucleus Sampling) differ from Temperature?**
**Your Answer:**
"Temperature changes the *shape* of the probability curve. Top-P changes *which words are even considered*. With Top-P = 0.9, the model sorts all tokens by probability and only samples from the smallest set whose cumulative probability equals 90%. It dynamically truncates the 'long tail' or unlikey/nonsense words, preventing the model from going completely off the rails while still allowing variety."

**Q: Your embedding model outputs 384 dimensions. Why 384? What does a single dimension represent?**
**Your Answer:**
"384 is specific to the `all-MiniLM-L6-v2` architecture (a distilled BERT model). A single dimension doesn't represent a human concept like 'color' or 'size'. It's a learned feature in the hidden state of the neural network. However, the *combination* of these dimensions captures semantic meaning. The magnitude of the vector might represent concepts like 'subject' vs 'object', or 'positive' vs 'negative' sentiment, distributed across the implementation."

**Q: How does HNSW (Hierarchical Navigable Small World) index work in ChromaDB?**
**Your Answer:**
"It's a graph-based algorithm for Approximate Nearest Neighbor (ANN) search.
-   **Small World**: Most nodes can be reached from any other node in a small number of hops.
-   **Hierarchical**: It builds layers of graphs. Top layers have few 'expressway' links for long-distance jumps across the vector space. As you get closer to the target, you drop down to lower, denser layers for fine-grained search.
-   It changes search complexity from $O(N)$ (brute force scan) to $O(\log N)$, making it viable for millions of vectors."
