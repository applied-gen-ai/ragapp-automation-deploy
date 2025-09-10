import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
import pickle


def insert_docs(embeddings, documents):
    
    dimension = 384  # Default dimension for all-MiniLM-L6-v2
    index = faiss.IndexFlatL2(dimension)

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local("faiss_index")

def insert_kyword(documents):

    retriever = BM25Retriever.from_documents(documents)

    with open('retriever.pkl', 'wb') as f:
        pickle.dump(retriever, f)