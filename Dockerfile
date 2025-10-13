# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed for pandas)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENV PORT=8501

ENTRYPOINT ["sh", "-c", "streamlit run app/streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
