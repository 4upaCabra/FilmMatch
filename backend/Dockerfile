FROM python:3.11-slim

WORKDIR /app

# Настройка зеркал PyPI и таймаутов для корпоративных сетей
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org
ARG PIP_TIMEOUT=120

# Кэширование pip слоев
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

# Копирование остального кода
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
