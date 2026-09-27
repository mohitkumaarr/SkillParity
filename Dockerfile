# Use lightweight official Python image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend and frontend source code
COPY backend /app/backend
COPY frontend /app/frontend

WORKDIR /app/backend

# Expose container port
EXPOSE 8000

# Run FastAPI app using Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
