# Using a lightweight Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (required by Cloud Run)
EXPOSE 8080

# Start the app using Gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8080"]
