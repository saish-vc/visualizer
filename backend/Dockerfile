FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends g++ gdb && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 10001 codetrace
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY spike.py .
COPY tests ./tests
USER codetrace
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
