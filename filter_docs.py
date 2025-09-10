from sentence_transformers import CrossEncoder
import numpy as np


cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
def cross_encoder_func(query, documents, k=5):

    pairs = [[query, doc.page_content] for doc in documents]
    scores = cross_encoder.predict(pairs)
    top_indices = np.argsort(scores)[::-1][:k]

    top_k_documents = [documents[idx] for idx in top_indices]

    return scores