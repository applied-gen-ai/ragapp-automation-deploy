from sentence_transformers import CrossEncoder
import os

HF_TOKEN = os.environ.get("HUGGINGFACE_API", None)
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2", use_auth_token=HF_TOKEN)

def cross_encoder_func(query, documents, k=5):
    import numpy as np
    pairs = [[query, doc.page_content] for doc in documents]
    scores = cross_encoder.predict(pairs)
    top_indices = np.argsort(scores)[::-1][:k]
    top_k_documents = [documents[idx] for idx in top_indices]
    return scores
