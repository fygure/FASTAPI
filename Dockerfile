# Dockerfile
FROM python:3.9

WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt
# Copy the source code to the working directory
COPY ./src /app/src

# Copy .env file to the working directory
COPY .env /app/

# Set environment variables for OpenTelemetry and Python path
ENV PYTHONPATH=/app/src
ENV $(cat .env | xargs)

# Command to run the FastAPI application
CMD ["opentelemetry-instrument", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
