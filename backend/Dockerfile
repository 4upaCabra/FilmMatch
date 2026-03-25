FROM python:3.11-slim

WORKDIR /app

# Настройка зеркал PyPI для российских сетей
# Используем несколько зеркал для надёжности
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ARG PIP_TIMEOUT=120

# Кэширование pip слоев
COPY requirements.txt .
RUN pip install \
    --no-cache-dir \
    --timeout=120 \
    --retries=5 \
    -r requirements.txt

# Копирование остального кода
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
