FROM python:3.11-slim

LABEL org.opencontainers.image.title="smart-greenhouse-monitoring-service" \
      org.opencontainers.image.description="Smart greenhouse microclimate monitoring service" \
      org.opencontainers.image.authors="Копань Артем Алексеевич"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

