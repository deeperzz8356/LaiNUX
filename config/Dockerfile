# ============================================================
# LAINUX AGENTIC AI OS - PRODUCTION DOCKERFILE
# Multi-Stage Build for Speed & Minimal Image Size
# ============================================================

# --- Stage 1: Builder (Install all heavy deps) ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY agentic_os/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Runtime Image (Lean & Fast) ---
FROM python:3.11-slim AS runtime

# Bring in installed packages from builder
COPY --from=builder /install /usr/local

# System deps for headless operation (Vision Tools use Xvfb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd -m lainux
USER lainux

WORKDIR /app

# Copy source code
COPY --chown=lainux:lainux . .

# Create persistent directories
RUN mkdir -p /app/logs /app/sandbox /app/knowledge_base /app/tests

# Expose Neural Dashboard
EXPOSE 8000

# Health check to monitor if the OS is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default: Run in autonomous evolution mode with headless display
CMD ["sh", "-c", "Xvfb :99 -screen 0 1280x720x16 & DISPLAY=:99 python -m agentic_os.main --auto"]
