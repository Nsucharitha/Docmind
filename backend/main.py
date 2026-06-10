from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from services.pdf_processor import extract_text_chunks
from services.embedder import embed_chunks, embed_query
from services.vector_store import upsert_chunks, query_similar
from services.llm import generate_answer

load_dotenv()

app = FastAPI(title="DocMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

uploaded_docs = {}

class QueryRequest(BaseModel):
    question: str
    doc_id: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/")
def root():
    return {"message": "DocMind API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    contents = await file.read()
    chunks = extract_text_chunks(contents, file.filename)

    if not chunks:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    embeddings = embed_chunks([c["text"] for c in chunks])
    doc_id = file.filename.replace(" ", "_").replace(".pdf", "")
    upsert_chunks(doc_id, chunks, embeddings)
    uploaded_docs[doc_id] = {"filename": file.filename, "chunk_count": len(chunks)}

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks_indexed": len(chunks),
        "message": "Document indexed successfully!"
    }

@app.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest):
    query_embedding = embed_query(request.question)
    results = query_similar(request.doc_id, query_embedding, top_k=4)

    if not results:
        raise HTTPException(status_code=404, detail="No relevant content found.")

    context_chunks = [r["text"] for r in results]
    sources = list(set([r["source"] for r in results]))
    answer = generate_answer(request.question, context_chunks)

    return QueryResponse(answer=answer, sources=sources)

@app.get("/docs-list")
def list_documents():
    return {"documents": uploaded_docs}