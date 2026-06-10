from services.pdf_processor import extract_text_chunks

with open("sample.pdf", "rb") as f:
    pdf_bytes = f.read()

chunks = extract_text_chunks(pdf_bytes, "sample.pdf")
print(f"Total chunks: {len(chunks)}")
print(f"\nFirst chunk:\n{chunks[0]['text'][:300]}")
print(f"\nSource: {chunks[0]['source']}")

from services.embedder import embed_chunks, embed_query

embeddings = embed_chunks([c["text"] for c in chunks[:3]])
print(f"\nEmbedding dimension: {len(embeddings[0])}")
print(f"First 5 values: {embeddings[0][:5]}")

q_embedding = embed_query("What is this document about?")
print(f"\nQuery embedding dimension: {len(q_embedding)}")

from services.vector_store import upsert_chunks, query_similar

# Store chunks in Pinecone
upsert_chunks("sample_resume", chunks, embeddings)
print("\n✅ Chunks stored in Pinecone!")

# Query it
import time
time.sleep(2)  # wait for Pinecone to index

results = query_similar("sample_resume", q_embedding, top_k=2)
print(f"\nTop results for 'What is this document about?':")
for r in results:
    print(f"\nScore: {r['score']:.3f}")
    print(f"Source: {r['source']}")
    print(f"Text: {r['text'][:200]}")


from services.llm import generate_answer

question = "What programming languages does this person know?"
context_chunks = [r["text"] for r in results]

answer = generate_answer(question, context_chunks)
print(f"\nQ: {question}")
print(f"A: {answer}")