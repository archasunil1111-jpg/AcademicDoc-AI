import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Convert text chunks into numerical vectors.
    """
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings.astype("float32")


def create_faiss_index(embeddings):
    """
    Create a FAISS index from embeddings.
    """
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def search_faiss(index, chunks, query, top_k=3):
    """
    Search FAISS for the most relevant chunks.
    """

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    # Don't request more results than available chunks
    top_k = min(top_k, len(chunks))

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for i in indices[0]:

        if i != -1:
            results.append(chunks[i])

    return results