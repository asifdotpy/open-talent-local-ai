# Production Voice Service - Multi-stage build for optimization
FROM python:3.11-slim as base

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    espeak-ng \
    libgomp1 \
    libglib2.0-0 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Build stage
FROM base as builder

WORKDIR /build

# Install build dependencies for WebRTC compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies to a specific location
COPY requirements.txt .
COPY requirements-webrtc.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt && \
    pip install --prefix=/install --no-cache-dir -r requirements-webrtc.txt

# Download Piper TTS binary
RUN mkdir -p piper && \
    cd piper && \
    wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz && \
    tar -xzf piper_amd64.tar.gz --strip-components=1 && \
    rm piper_amd64.tar.gz && \
    chmod +x piper

# Production stage
FROM base as production

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY main.py .
COPY services/ ./services/
COPY webrtc_worker.py .
COPY webrtc_signaling_server.py .

# Copy Piper binary
COPY --from=builder /build/piper ./piper

# Create directories for models and temp files
RUN mkdir -p models logs temp && \
    chmod -R 755 models logs temp

# Create non-root user
RUN adduser --system --group --no-create-home appuser && \
    chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health').raise_for_status()"

# Switch to non-root user
USER appuser

# Expose service port
EXPOSE 8002

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15 \
    PIPER_MODEL_PATH=models/en_US-lessac-medium.onnx \
    PIPER_CONFIG_PATH=models/en_US-lessac-medium.onnx.json \
    PIPER_BINARY=./piper/piper \
    SILERO_MODEL_PATH=models/silero_vad.onnx \
    USE_MOCK_SERVICES=false \
    ENABLE_WEBRTC=true

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--log-level", "info"]
