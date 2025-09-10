from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json


def chunk_texts(text):

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50,
    )

    chunks = text_splitter.create_documents([text])

    return chunks



