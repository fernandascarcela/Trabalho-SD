FROM python:3.11-slim

# Evita arquivos .pyc e buffer no stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Dependências do sistema (psycopg2 precisa disso)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --no-cache-dir psycopg2-binary

# Copia o resto do código
COPY . .

# Porta TCP do serviço de usuários
EXPOSE 6001

# Comando de inicialização
CMD ["python", "main.py"]
