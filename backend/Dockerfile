# Backend Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend codebase into the container
COPY . .

# Expose port 5000
EXPOSE 5000

# Modify the Flask run command to bind to all interfaces
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]