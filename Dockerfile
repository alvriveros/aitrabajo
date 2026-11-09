FROM python:3.12-slim

# OpenCV (dependencia de Ultralytics) necesita estas bibliotecas del sistema.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# PyTorch para CPU: el de PyPI trae CUDA y pesa varios GB más. Otro índice se elige con --build-arg.
ARG TORCH_INDEX=https://download.pytorch.org/whl/cpu
COPY requirements.txt .
COPY vision/requirements.txt vision/requirements.txt
RUN pip install --no-cache-dir torch==2.15.0 torchvision==0.29.2 --index-url "$TORCH_INDEX" \
    && pip install --no-cache-dir -r requirements.txt -r vision/requirements.txt \
    && python -c "import cv2, lap, torch, ultralytics"
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

COPY api/ api/
COPY ui/ ui/
COPY vision/ vision/
COPY evaluation/ evaluation/
COPY .streamlit/config.toml .streamlit/config.toml
COPY docs/demo/ docs/demo/
# Pesos oficiales de Ultralytics, que no se versionan: hay que descargarlos antes (ver README, «Docker»).
COPY yolo11n.pt .
