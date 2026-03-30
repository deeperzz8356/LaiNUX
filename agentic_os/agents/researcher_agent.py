"""
Enhanced Researcher Agent with Document Reference Feeds.
This agent continuously scans high-quality AI/OS development resources
to feed the Brain with structured knowledge for self-improvement.
"""
import asyncio
import json
import os
import time
from pathlib import Path
import httpx
import aiohttp
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from ..utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KB_PATH = os.getenv("LAINUX_KNOWLEDGE_BASE", str(PROJECT_ROOT / "knowledge_base"))

# ============================================================
# KNOWLEDGE FEED SOURCES
# Premium references that LaiNUX should learn from
# ============================================================
REFERENCE_FEEDS = [
    # Agentic AI / LangGraph
    "https://python.langchain.com/docs/",
    "https://langchain-ai.github.io/langgraph/",
    # Python Best Practices
    "https://docs.python.org/3/library/",
    # FastAPI (for dashboard)
    "https://fastapi.tiangolo.com/",
    # Docker
    "https://docs.docker.com/engine/reference/builder/",
]

# Dynamic search topics to keep the OS updated
RESEARCH_TOPICS = [
    "autonomous agentic AI architecture 2024",
    "python file system security best practices",
    "langgraph multi-agent orchestration patterns",
    "FastAPI WebSocket real-time streaming",
    "docker multi-stage build optimization python",
    "AI self-improvement loop design patterns",
    "vector database RAG retrieval optimization",
    "python subprocess security sandboxing",
]


async def fetch_url_summary(url: str, timeout=8) -> str:
    """Fetches a URL and returns a text summary for the knowledge base."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Truncate to avoid massive blobs
                    return text[:3000]
    except Exception as e:
        return f"[FETCH ERROR for {url}: {str(e)}]"


def run_duckduckgo_research(topic: str, max_results=5) -> list:
    """Searches DuckDuckGo for a topic and returns cleaned results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=max_results))
        return [
            {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
            for r in results
        ]
    except Exception as e:
        logger.error(f"DuckDuckGo research failed for '{topic}': {e}")
        return []


def save_to_knowledge_base(topic: str, content: str, kb_path=DEFAULT_KB_PATH):
    """Saves research output to the shared knowledge base volume."""
    if not os.path.exists(kb_path):
        os.makedirs(kb_path)
    
    filename = topic.replace(" ", "_").replace("/", "-")[:50] + ".json"
    filepath = os.path.join(kb_path, filename)
    
    entry = {
        "topic": topic,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "content": content,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)
    
    logger.info(f"Knowledge Base: Saved research for '{topic}' -> {filepath}")


def load_knowledge_context(query: str, kb_path=DEFAULT_KB_PATH, max_docs=3) -> str:
    """Loads the most relevant knowledge base entries using Vector RAG (Semantic Search)."""
    if not os.path.exists(kb_path):
        return "No knowledge base entries yet."
    
    docs = []
    # 1. Load all documents from the volume
    for filename in os.listdir(kb_path):
        if filename.endswith(".json"):
            filepath = os.path.join(kb_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("content"):
                        docs.append(data)
            except Exception:
                pass
    
    if not docs:
        return "No relevant knowledge base entries found."
        
    # 2. RAG Semantic Search Engine
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        # Load the lightweight embedder
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Embed the contents (topic + body)
        texts = [f"{d['topic']}: {d['content'][:500]}" for d in docs]
        doc_embeddings = embedder.encode(texts).astype('float32')
        
        # Build FAISS Index
        d = doc_embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(doc_embeddings)
        
        # Search against the query
        query_embedding = embedder.encode([query]).astype('float32')
        distances, indices = index.search(query_embedding, min(max_docs, len(docs)))
        
        # Extract top results
        top_docs = [docs[i] for i in indices[0] if i != -1]
        
    except Exception as e:
        logger.warning(f"RAG Knowledge Engine missing deps, falling back to keyword: {e}")
        # Fallback to simple keyword logic if FAISS fails
        top_docs = [d for d in docs if any(kw.lower() in query.lower() for kw in d.get("topic", "").split())][:max_docs]
        if not top_docs:
            top_docs = docs[:max_docs] # Just return the latest if totally failed
    
    # Format for the LLM context limits
    return "\n\n---\n\n".join([
        f"[KB Entry: {d['topic']}]\n{d['content'][:800]}"
        for d in top_docs
    ])


def run_research_loop(duration_hours=1):
    """
    Background process: Continuously researches topics
    and populates the knowledge base with premium intelligence.
    """
    import random
    from datetime import datetime, timedelta
    
    end_time = datetime.now() + timedelta(hours=duration_hours)
    logger.info("Researcher Agent: Starting continuous knowledge acquisition...")
    
    while datetime.now() < end_time:
        topic = random.choice(RESEARCH_TOPICS)
        logger.info(f"Researcher Agent: Researching -> '{topic}'")
        
        results = run_duckduckgo_research(topic)
        if results:
            content = "\n\n".join([
                f"Title: {r['title']}\nSnippet: {r['snippet']}\nURL: {r['url']}"
                for r in results
            ])
            save_to_knowledge_base(topic, content)
        
        # Cooldown between research cycles to avoid rate limiting
        time.sleep(45)


if __name__ == "__main__":
    run_research_loop()
