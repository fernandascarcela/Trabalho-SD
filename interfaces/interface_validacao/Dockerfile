FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. convenio.proto
EXPOSE 5003
ENV GRPC_DNS_RESOLVER=native
CMD ["python", "interface_convenio.py"]