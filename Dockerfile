# Use CUDA 11.8 base image with cuDNN support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set the working directory
WORKDIR /LivePortrait

# Install necessary system packages and upgrade pip in a single layer to optimize caching
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git ffmpeg cmake libsm6 libxext6 libxrender-dev libglib2.0-0 libx11-dev python3-pip python3-dev libopencv-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure execution permissions for scripts
RUN chmod +x /LivePortrait/*.sh

# Default command (modify based on your application)
CMD ["python3", "app.py"]
