# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies needed for PostgreSQL client library (libpq-dev)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Copy Pipfiles and install dependencies
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy

# Copy the rest of the code
COPY . /app/

# Expose the port
EXPOSE 8000