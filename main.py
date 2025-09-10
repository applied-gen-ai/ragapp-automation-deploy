from read_pdf import read_pdf
from chunking import chunk_texts
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from huggingface_hub import login
from langchain_huggingface import HuggingFaceEmbeddings
from search import keyword_search, similarity_search, hybrid_search

import os
import numpy as np
os.environ["PYTHONASYNCIOSYNCHRO"] = "1"

import boto3
import time
import json
from botocore.exceptions import ClientError

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableMap, RunnableLambda
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from sentence_transformers import CrossEncoder
import streamlit as st
from filter_docs import cross_encoder_func

import torch

def normalize_logit(logit):
    """Converts a raw logit from a Cross-Encoder into a 0-1 relevance score."""
    return torch.sigmoid(torch.tensor(logit)).item()

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

if not token:
    raise ValueError("HUGGINGFACE_API not set in Secrets Manager")

login(token=token) 

embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )





def format_docs(input):
    return '\n'.join([doc.page_content for doc in input])
     

def filter_retrieved_docs(query, docs):
     final_docs = []
     final_scores = []
     scores = cross_encoder_func(query, docs)
     for i in range(len(scores)):
          logit = normalize_logit(scores[i])
          final_scores.append(logit)
          if logit>0.2:
               final_docs.append(docs[i])
     return final_docs, final_scores
              

def model_predict(query):
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    ALTERNATE_MODEL = "mixtral-8x7b-32768"

    def get_groq_model():
        try:
            return ChatGroq(temperature=0, model_name=DEFAULT_MODEL, api_key=g_api)
        except Exception as e:
            print(f"Model {DEFAULT_MODEL} failed with error: {e}. Falling back to {ALTERNATE_MODEL}.")
            return ChatGroq(temperature=0, model_name=ALTERNATE_MODEL, api_key=g_api)

    model = get_groq_model()

    prompt_str = '''
You are a helpful AI assistant that assists humans on indian economy.
Just provide answer only without additional text. Give detailed ansswer

Base your response primarily on the provided knowledge base, combined with your general knowledge.

Get the knowledge from below knowledge base:
'''

    template = ChatPromptTemplate.from_messages([
        ("system", f"{prompt_str}\n{'{context}'}"),
        ("human", "{question}")
    ])

    retrieved_docs = similarity_search(query, embeddings, k=5)

    final_ret_docs, final_scores = filter_retrieved_docs(query, retrieved_docs)

    retrieved_docs_out = [i.page_content for i in retrieved_docs]

    final_ret_docs_out = [i.page_content for i in final_ret_docs]

    if len(final_ret_docs)>0:
        formatted_docs = format_docs(final_ret_docs)
    else:
         formatted_docs = ''

    chain = (
        RunnableMap({
            "context": lambda x: formatted_docs,  # Use retrieved context
            "question": lambda x: x["question"]
        })
        | template 
        | model 
        | StrOutputParser()
    )

    llm_response = chain.invoke({"question": query})

    # Return both the retrieved documents & LLM output
    return {
        "prompt": prompt_str, 
        "retrieved_docs": retrieved_docs_out,  # Raw retrieved documents
        "scores":final_scores, 
        "final_ret_docs": final_ret_docs_out,
        "formatted_context": formatted_docs,  # Processed text from retrieved docs
        "llm_response": llm_response  # Generated answer,
    }



user_input = st.text_area("Enter Text To Answer")
button = st.button("Generate_Answer")
if user_input and button:
    summary = model_predict(user_input)
    st.write("Generated_Answer : ", summary['llm_response'])


cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def publish_metrics(user_id, question, answer, request_time_ms):
    cloudwatch.put_metric_data(
        Namespace='CustomApp',
        MetricData=[
            {
                'MetricName': 'UsersAskingQuestions',
                'Dimensions': [{'Name': 'Service', 'Value': 'your-service-name'}],
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'QuestionsAsked',
                'Dimensions': [{'Name': 'Service', 'Value': 'your-service-name'}],
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'AverageQuestionLength',
                'Dimensions': [{'Name': 'Service', 'Value': 'your-service-name'}],
                'Value': len(question),
                'Unit': 'Count'
            },
            {
                'MetricName': 'AverageAnswerLength',
                'Dimensions': [{'Name': 'Service', 'Value': 'your-service-name'}],
                'Value': len(answer),
                'Unit': 'Count'
            },
            {
                'MetricName': 'AverageRequestTime',
                'Dimensions': [{'Name': 'Service', 'Value': 'your-service-name'}],
                'Value': request_time_ms,
                'Unit': 'Milliseconds'
            }
        ]
    )