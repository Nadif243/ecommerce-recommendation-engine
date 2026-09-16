# Use a lightweight official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files and force stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first (Docker caches this step to speed up future builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application code
COPY src/ ./src/
COPY main.py .

# Expose the API port
EXPOSE 8000

# Start the master orchestrator
CMD ["python", "main.py"]
