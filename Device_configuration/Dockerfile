FROM python:3.11-slim

# App lives here
WORKDIR /app

# Optional: build tools for packages that may need compilation on some systems
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy deps first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app ./app

EXPOSE 8000

# Bind to 0.0.0.0 so the app is reachable via `docker run -p ...`
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
