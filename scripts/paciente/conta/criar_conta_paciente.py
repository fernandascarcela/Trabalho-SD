import sys
import requests

if len(sys.argv) != 4:
    print("Uso: python criar_conta_paciente.py <nome> <email> <senha>")
    sys.exit(1)

nome = sys.argv[1]
email = sys.argv[2]
senha = sys.argv[3]

payload = {
    "nome": nome,
    "email": email,
    "senha": senha
}

try:
    resp = requests.post("http://localhost:5001/usuarios/criar", json=payload)
    print("Resposta do servidor:", resp.json())

except Exception as e:
    print("Erro ao conectar ao servidor:", e)
