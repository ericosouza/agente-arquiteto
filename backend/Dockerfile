# ==========================================================
# Agente Arquiteto de Software - Backend (FastAPI + Python 3.12)
# ==========================================================
FROM python:3.12-slim

WORKDIR /app

# Instala ferramentas essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app/ ./app/
COPY .env.example .env

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
