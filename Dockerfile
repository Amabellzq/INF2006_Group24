# Step 1: Use a lightweight Python image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy dependency files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the Flask app into the container
COPY . .

# Step 5: Create a non-root user for security
RUN groupadd -r flask && useradd -r -g flask flask
USER flask

# Step 6: Expose Flask's port
EXPOSE 8000

# Step 7: Start Gunicorn with better settings
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--timeout", "120", "--bind", "0.0.0.0:8000", "wsgi:app"]
