FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org
ARG PIP_TIMEOUT=120

COPY requirements.txt .
RUN pip install \
    --no-cache-dir \
    --timeout=120 \
    --retries=5 \
    -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
