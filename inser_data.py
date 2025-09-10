from read_pdf import read_pdf
from chunking import chunk_texts
from insert import insert_docs, insert_kyword
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import login

import boto3
import json
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "aws-deploy"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    return str(secret['GROK_API']), str(secret['HUGGINGFACE_API'])


g_api, token = get_secret()
print(token)

if not token:
        raise ValueError("HUGGING_FACE_HUB_TOKEN not set in environment")
login(token)

embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def prep_docs(chunks):
    docs = []
    for i in chunks:
        d = Document(page_content = i.page_content, metadata={"source": "budget"},)
        docs.append(d)
    return docs

def create_data_insert():
    text = read_pdf(r"./budget_speech.pdf")
    chunks = chunk_texts(text)
    print("chunking completed.......")

    ds = prep_docs(chunks)

    print("inserting docs------")

    insert_docs(embeddings, ds)

    insert_kyword(ds)
    print("inserted......................")

create_data_insert()