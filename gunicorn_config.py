import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
# workers = multiprocessing.cpu_count() * 2 + 1
# workers = 1
# # worker_class = "gthread"  # Use threaded workers for async handling
# worker_class = "sync"  # Uses separate processes, preventing threading issues
# threads = 8  # Each worker will have 8 threads for better concurrency

# Worker processes
workers = 2  # Start with 2 workers (adjust based on your GPU capacity)
worker_class = "sync"  # Use separate processes (better for CUDA)

# Prevent CUDA threading issues
threads = 1  # Only 1 thread per worker (ensures CUDA initializes correctly)

timeout = 300  # Allow long-running requests up to 5 minutes
keepalive = 30  # Keep persistent connections open for 30 seconds

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"
loglevel = "info"

# Security
# limit_request_line = 4094  # Limit request size to prevent abuse
# preload_app = True
# Prevent master process from initializing CUDA
preload_app = False  # Ensures each worker initializes CUDA separately

# Set environment variables for CUDA stability
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Ensure only GPU 0 is used
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"  # Ensures CUDA executes synchronously
os.environ["NVIDIA_VISIBLE_DEVICES"] = "all"  # Ensure all GPUs are accessible
os.environ["NVIDIA_DRIVER_CAPABILITIES"] = "compute,utility"
