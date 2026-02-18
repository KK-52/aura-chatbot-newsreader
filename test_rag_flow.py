import scraper
import rag_engine
import os

def test_scraper():
    print("Testing Scraper...")
    url = "https://example.com"
    # We can't easily mock requests in a simple script without extra libs, 
    # so we'll test the split logic with dummy text.
    print("  Testing split_text...")
    text = "This is sentence one. This is sentence two. " * 50
    chunks = scraper.split_text(text, chunk_size=20, overlap=5)
    print(f"  Generated {len(chunks)} chunks.")
    assert len(chunks) > 0
    print("  Scraper Split Text: PASS")

def test_rag_generation():
    print("\nTesting RAG Generation...")
    context = "Python is a programming language. It is used for web development."
    query = "What is Python?"
    
    # Force no keys to test fallback first
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    
    answer = rag_engine.generate_answer_with_llm(context, query)
    print(f"  Fallback Answer: {answer}")
    assert "LLM API keys not found" in answer or "Python is a programming language" in answer
    print("  Fallback Generation: PASS")

if __name__ == "__main__":
    test_scraper()
    test_rag_generation()
    print("\nAll Tests Passed!")
