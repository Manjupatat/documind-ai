
# Use Python 3.13
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Python configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependency for ONNX Runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source, frontend and other project files
COPY . .

# Create non-root user
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Default application port
EXPOSE 8000

# Start FastAPI application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
