FROM python:3.11-slim

# Evita arquivos .pyc e força logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia arquivos de dependências primeiro (boas práticas)
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do cliente
COPY . .

# Container inicia em modo interativo
CMD ["bash"]
