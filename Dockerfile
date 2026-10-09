FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install uv


COPY requirements.txt .


RUN uv pip install --system -r requirements.txt


COPY . .


EXPOSE 8000
