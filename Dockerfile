# Use Python 3.9
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install system dependencies required for OpenCV and DeepFace
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a writable directory for DeepFace weights and temporary files
RUN mkdir -p /app/.deepface && chmod -R 777 /app/.deepface
ENV DEEPFACE_HOME=/app/.deepface

# Create a writable directory for file uploads/temp generation
RUN chmod -R 777 /app

# Expose the port Hugging Face expects
EXPOSE 7860

# Command to run the application using Gunicorn (Production server)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]