import os
import json
import requests
import numpy as np
import faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter
from brain import ask_llm
from analytics.chart_generator import generate_revenue_chart
from rank_bm25 import BM25Okapi
import time

BASE_VECTOR_PATH = "vectorstore"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str):
    """Single embedding — reuses batch function for consistency."""
    return get_embeddings_batch([text])[0]


def get_embeddings_batch(texts: list[str]):
    """Batch embedding for all chunks — 1 HTTP call instead of N."""
    print("Sending batch embedding request...")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBED_MODEL,
            "input": texts
        },
        timeout=600
    )

    print("OLLAMA STATUS:", response.status_code)
    print("OLLAMA RAW:", response.text[:500])

    response.raise_for_status()

    data = response.json()

    if "data" in data:
        vectors = [item["embedding"] for item in data["data"]]
    elif "embedding" in data:
        vectors = [data["embedding"]]
    else:
        raise Exception(f"Unexpected Ollama response format: {data}")

    return np.array(vectors, dtype="float32")


# ---------------- TEXT PROCESSING ----------------
def process_text(text: str, doc_id: str):

    start = time.time()

    print("===== PROCESS START =====")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)[:200]

    print(f"Chunks: {len(chunks)}")

    doc_path = os.path.join(BASE_VECTOR_PATH, doc_id)
    os.makedirs(doc_path, exist_ok=True)

    processing_flag = f"{doc_path}/processing"

    with open(processing_flag, "w") as f:
        f.write("building")

    try:
        vectors = get_embeddings_batch(chunks)

        dimension = vectors.shape[1]

        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)

        faiss.write_index(index, f"{doc_path}/index.faiss")

        with open(f"{doc_path}/chunks.json", "w") as f:
            json.dump(chunks, f)

        print("Embedding + index done")

    except Exception as e:
        print("PROCESS FAILED:", str(e))

    finally:
        if os.path.exists(processing_flag):
            os.remove(processing_flag)

        print("Processing flag removed")
        print("TOTAL TIME:", time.time() - start)


# ---------------- SINGLE DOCUMENT QUERY ----------------
def query_rag(question: str, doc_id: str, history: list[dict]):

    doc_path = os.path.join(BASE_VECTOR_PATH, doc_id)
    financial_file = os.path.join(BASE_VECTOR_PATH, doc_id, "financial.json")

    if os.path.exists(financial_file) and "revenue" in question.lower():

        with open(financial_file) as f:
            data = json.load(f)

        if data.get("revenue_mentions"):

            chart = generate_revenue_chart(
                data["revenue_mentions"],
                doc_id
            )

            return f"""
Revenue mentions found:
{data['revenue_mentions']}

Revenue chart generated at:
{chart}
"""

    if not os.path.exists(doc_path):
        return "Document is still processing. Please wait a few seconds and try again."

    if os.path.exists(os.path.join(doc_path, "processing")):
        return "Document is still being processed. Please wait."

    try:
        index = faiss.read_index(f"{doc_path}/index.faiss")

        with open(f"{doc_path}/chunks.json") as f:
            chunks = json.load(f)

        query_vector = get_embedding(question).reshape(1, -1)

        distances, indices = index.search(query_vector, 6)

        docs = [chunks[i] for i in indices[0]]

    except Exception:
        return "Document embeddings are still building. Try again in a few seconds."

    if not docs:
        return "No relevant information found."

    tokenized_docs = [t.split() for t in docs]
    bm25 = BM25Okapi(tokenized_docs)

    tokenized_query = question.split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_texts = [t[0] for t in ranked[:3]]

    context = "\n\n".join(
        f"[Source {i+1}] {t}"
        for i, t in enumerate(top_texts)
    )

    return ask_llm(
        context=context,
        question=question,
        history=history
    )


# ---------------- MULTI DOCUMENT QUERY ----------------
def query_multi_doc(question: str, doc_ids: list, history: list[dict]):

    contexts = []

    for doc_id in doc_ids:

        doc_path = os.path.join(BASE_VECTOR_PATH, doc_id)

        if not os.path.exists(doc_path):
            continue

        try:
            index = faiss.read_index(f"{doc_path}/index.faiss")

            with open(f"{doc_path}/chunks.json") as f:
                chunks = json.load(f)

            query_vector = get_embedding(question).reshape(1, -1)

            distances, indices = index.search(query_vector, 3)

            docs = [chunks[i] for i in indices[0]]

        except Exception:
            continue

        contexts.append("\n".join(docs))

    combined_context = "\n\n".join(contexts)

    return ask_llm(
        context=combined_context,
        question=question,
        history=history
    )