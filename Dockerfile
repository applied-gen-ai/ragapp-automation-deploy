FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# ✅ Pre-download the Hugging Face model so it's inside the image
#    This creates a cached copy under /root/.cache/huggingface/…
#    No token needed if the model is public.
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')"

# Copy application code and assets
COPY *.py ./
COPY *.pdf ./
COPY faiss_index/ ./faiss_index/
COPY retriever.pkl ./

# Expose the Streamlit port
EXPOSE 8501

# Healthcheck to verify the service is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 0

# Run Streamlit with the file watcher disabled
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
