# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    pkg-config \
    make \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy the entire project for building
COPY . .

# Configure poetry to not create a virtual environment inside container
RUN poetry config virtualenvs.create false

# Install dependencies and build the package
RUN pip install cython && \
    python setup.py build_ext --inplace && \
    poetry install --only main --no-interaction --no-ansi

# Create charts directory with proper permissions
RUN mkdir -p charts && chmod 777 charts

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 