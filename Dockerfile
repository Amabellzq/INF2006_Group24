# Step 1: Use an official Python image as the base
FROM python:3.9

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy dependency files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the Flask app into the container
COPY . .

# Step 5: Expose Flask's port
EXPOSE 8000

# Step 6: Start Gunicorn (No need for start.sh)
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "wsgi:app"]
