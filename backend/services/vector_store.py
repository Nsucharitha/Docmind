import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

_index = None
INDEX_NAME = "docmind-index"
EMBEDDING_DIM = 384

def _get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        existing = [i.name for i in pc.list_indexes()]
        if INDEX_NAME not in existing:
            pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        _index = pc.Index(INDEX_NAME)
    return _index

def upsert_chunks(doc_id, chunks, embeddings):
    index = _get_index()
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{doc_id}__chunk_{i}",
            "values": embedding,
            "metadata": {
                "doc_id": doc_id,
                "text": chunk["text"],
                "source": chunk["source"],
                "page": chunk["page"],
            },
        })
    index.upsert(vectors=vectors)

def query_similar(doc_id, query_embedding, top_k=4):
    index = _get_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"doc_id": {"$eq": doc_id}},
        include_metadata=True,
    )
    matches = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        matches.append({
            "text": meta.get("text", ""),
            "source": meta.get("source", ""),
            "score": match.get("score", 0),
        })
    return matches