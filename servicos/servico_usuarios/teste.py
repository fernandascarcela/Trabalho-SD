import socket
import json

HOST = "0.0.0.0"
PORT = 6001

mensagem = {
    "protocolo": "usuarios/1.0",
    "tipo": "request",
    "acao": "registrar_usuario",
    "dados": {
        "perfil_operador": "admin",
        "email_operador": "admin@gmail.com",
        "senha_operador": "admin123",
        "role": "paciente",
        "nome": "João Teste",
        "email": "joao@test.com",
        "senha": "123456",
        "cpf": "12345678900"
    }
}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(json.dumps(mensagem).encode())

resposta = s.recv(4096)
print(resposta.decode())

s.close()
