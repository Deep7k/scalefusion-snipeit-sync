# Use official Python base image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY app/ app/

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app/main.py"]
