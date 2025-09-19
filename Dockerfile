FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and assets
COPY *.py ./
COPY *.pdf ./
COPY faiss_index/ ./faiss_index/
COPY retriever.pkl ./

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to verify the service is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 0

# Run Streamlit with file watcher disabled
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
