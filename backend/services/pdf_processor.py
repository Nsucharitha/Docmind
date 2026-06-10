from pypdf import PdfReader
import io

def extract_text_chunks(pdf_bytes, filename, chunk_size=500, chunk_overlap=50):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    chunks = []
    chunk_index = 0

    for page_num, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        text = " ".join(raw.split())  # clean up whitespace

        if not text:
            continue

        words = text.split()
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])
            chunks.append({
                "text": chunk_text,
                "source": f"{filename} — page {page_num}",
                "page": page_num,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
            if end >= len(words):
                break
            start += chunk_size - chunk_overlap

    return chunks