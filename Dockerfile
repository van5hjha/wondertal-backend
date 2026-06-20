FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt gunicorn whitenoise

# Copy project
COPY . /app/

# Make the startup script executable
RUN chmod +x /app/start.sh

# Collect static files (if you are using Django's staticfiles)
RUN python manage.py collectstatic --noinput || true

# Run the application (starts both web and celery)
CMD ["/app/start.sh"]
