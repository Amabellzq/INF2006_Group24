# Step 1: Use a lightweight Python image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*  # Clean up after installation

# Step 4: Copy dependency files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the Flask app into the container
COPY . .

# Step 7: Expose Flask's port
EXPOSE 8000

# Step 8: Start Gunicorn
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--timeout", "120", "--bind", "0.0.0.0:8000", "wsgi:app"]
