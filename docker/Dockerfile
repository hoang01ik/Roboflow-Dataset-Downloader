# Dockerfile for Linux-based GUI runtime (Requires X11 host)
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Tkinter and X11
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libx11-6 \
    libxext-6 \
    librender-dev \
    libxft2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency file and install
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code from src/
COPY src/ .

# Environment variable for display (overriden by runtime --net=host or -e DISPLAY)
ENV DISPLAY=:0

# Command to execute (inside /app, which contains main.py)
CMD ["python", "main.py"]
