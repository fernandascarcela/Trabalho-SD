import sys
import requests

if len(sys.argv) != 6:
    print("Uso: python editar_conta_paciente.py <email> <senha> <novo_nome|- > <novo_email|- > <nova_senha|- >")
    sys.exit(1)

email = sys.argv[1]
senha = sys.argv[2]
novo_nome = sys.argv[3]
novo_email = sys.argv[4]
nova_senha = sys.argv[5]

payload = {
    "email": email,
    "senha": senha
}

if novo_nome != "-":
    payload["novo_nome"] = novo_nome

if novo_email != "-":
    payload["novo_email"] = novo_email

if nova_senha != "-":
    payload["nova_senha"] = nova_senha

resp = requests.patch("http://localhost:5001/usuarios/editar", json=payload)
print("Resposta do servidor:", resp.json())
