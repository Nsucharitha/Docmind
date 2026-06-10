import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def generate_answer(question, context_chunks):
    client = _get_client()

    context = "\n\n---\n\n".join(context_chunks)

    system_prompt = """You are DocMind, an intelligent document assistant.
Answer the user's question using ONLY the context provided.
Be concise and accurate.
If the answer is not in the context, say: 'I couldn't find that in the document.'"""

    user_prompt = f"""Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()