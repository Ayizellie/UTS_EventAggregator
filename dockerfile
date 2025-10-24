# ============================================
# Stage 1: Build stage
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Stage 2: Runtime stage
# ============================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="11221069@student.itk.ac.id"
LABEL description="UTS Event Aggregator - Idempotent Event Processing System"

WORKDIR /app

# Create non-root user untuk security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser requirements.txt .

# Create data directory untuk SQLite persistence
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Set PATH untuk user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check 
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/stats')" || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]