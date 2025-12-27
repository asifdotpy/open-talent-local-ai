# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  OpenTalent vLLM Production Server                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

FROM nvidia/cuda:12.1-base-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set Python path
ENV PYTHONPATH=/app
WORKDIR /app

# Install vLLM and dependencies
RUN pip install --no-cache-dir \
    vllm \
    huggingface_hub \
    torch \
    transformers \
    accelerate

# Create model directory
RUN mkdir -p /models

# Copy configuration
COPY vllm-config.yaml /app/vllm-config.yaml
COPY start-vllm.sh /app/start-vllm.sh

RUN chmod +x /app/start-vllm.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["/app/start-vllm.sh"]
