FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY ui/ ui/
COPY .streamlit/config.toml .streamlit/config.toml
COPY docs/demo/ docs/demo/
