import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import os

# Use sentence-transformers (free, local)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection(
    name="financial_docs",
    embedding_function=embed_fn
)

def ingest_pdf(filepath: str, doc_id: str):
    """Ingest an annual report or financial document."""
    reader = PdfReader(filepath)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and len(text) > 100:
            chunks.append({
                "id": f"{doc_id}_page_{i}",
                "text": text[:2000],   # chunk size
                "metadata": {"source": filepath, "page": i}
            })
    
    collection.add(
        documents=[c["text"] for c in chunks],
        ids=[c["id"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks]
    )
    print(f"Ingested {len(chunks)} chunks from {filepath}")

def retrieve(query: str, n_results: int = 5) -> list[str]:
    """Semantic search over ingested documents."""
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0] if results["documents"] else []