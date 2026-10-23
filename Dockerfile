
# 1. Use Python 3.11
FROM python:3.11-slim

# 2. Configure Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 3. Set the working directory
WORKDIR /app

# 4. Copy dependencies first for better build caching
COPY requirements.txt /app/requirements.txt

# 5. Install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# 6. Copy LegalBot application, including static frontend files
COPY app/ /app/app/

# 7. Document the application port
EXPOSE 8000

# 8. Check whether the FastAPI application is healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

# 9. Start the FastAPI server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
