# Base image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (build tools for some Python libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install Python deps first (better layer caching)
COPY one_last_time/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy the app
COPY . /app

# Expose Flask port
EXPOSE 5000

# Run with gunicorn so it binds to 0.0.0.0 for container networking
# App entry: module path is one_last_time.app:app
CMD ["gunicorn", "one_last_time.app:app", "-b", "0.0.0.0:5000", "--workers", "3"]


