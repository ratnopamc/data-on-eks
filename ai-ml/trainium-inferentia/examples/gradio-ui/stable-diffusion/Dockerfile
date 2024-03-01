# Use Python base image
FROM --platform=linux/amd64 python:3.9-slim as build

ENV MODEL_ENDPOINT="/imagine"
ENV SERVICE_NAME="http://localhost:8000"

# Set working directory in the container
WORKDIR /app

# Copy requirements file
# COPY requirements.txt /app/requirements.txt

# Copy the Python script into the container
COPY gradio-app-stablediffusion.py /app/gradio-app-stablediffusion.py

RUN pip install --no-cache-dir gradio requests Pillow
# Install dependencies
# RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port
# EXPOSE 8000

# Set environment variables
# ENV MODEL_ENDPOINT="/imagine"
# ENV SERVICE_NAME="http://localhost:8000"

# Command to run the Python script
ENTRYPOINT ["python", "gradio-app-stablediffusion.py"]
