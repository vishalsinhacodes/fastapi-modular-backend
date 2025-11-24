# Use a lightweight Python image
FROM python:3.11-slim

# Set work directory in container
WORKDIR /app

# Install system dependencies for psycopg2 and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy requirments and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port (inside container)
EXPOSE 8000

# Use environment variable for module path if needed
ENV PYTHONPATH=/app

# Run the app with uvicorn
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]