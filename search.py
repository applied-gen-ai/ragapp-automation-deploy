from langchain_community.vectorstores import FAISS
import pickle
from huggingface_hub import login
from langchain.retrievers import EnsembleRetriever


with open('retriever.pkl', 'rb') as f:
        retriever_kw = pickle.load(f)

def similarity_search(query,embeddings,  k=5):

    new_vector_store = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    docs = new_vector_store.similarity_search(query, k=k)
    return docs



def keyword_search(query):
    docs = retriever_kw.invoke(query, k=5)
    return docs

def hybrid_search(query, embeddings, k):
    new_vector_store = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )

    faiss_retriever = new_vector_store.as_retriever(search_kwargs={"k": k})
    retriever_kw.k=k

    ensemble_retriever = EnsembleRetriever(
    retrievers=[retriever_kw, faiss_retriever], weights=[0.5, 0.5]
    )

    docs = ensemble_retriever.invoke(query)
    return docs


