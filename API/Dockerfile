FROM python:3.11.14
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=API.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD python manage.py migrate --noinput && \
    gunicorn --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    API.wsgi:application
