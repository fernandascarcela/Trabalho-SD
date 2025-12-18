import sys
import requests

if len(sys.argv) != 3:
    print("Uso: python login.py <email> <senha>")
    sys.exit(1)

email = sys.argv[1]
senha = sys.argv[2]

payload = {
    "email": email,
    "senha": senha
}

try:
    resp = requests.post("http://localhost:5001/usuarios/login", json=payload)
    print("Resposta do servidor:", resp.json())

except Exception as e:
    print("Erro ao conectar ao servidor:", e)
