# Use official slim Python 3.12 image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user and switch to it
RUN addgroup --system app && adduser --system --group app \
    && chown -R app:app /app
USER app

# Expose server port
EXPOSE 8000

# Run database migrations and start Gunicorn server
CMD ["sh", "-c", "python manage.py migrate && gunicorn Agrotech.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60 --access-logfile - --error-logfile -"]
