from flask import Flask, request, jsonify
import socket
import json

app = Flask(__name__)

HOST = "localhost"               #Dockercompose: "servico_usuarios"
PORT = 5001

def enviar_socket(payload: dict):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(json.dumps(payload).encode())
    resp = json.loads(s.recv(4096).decode())
    s.close()
    return resp

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    return jsonify(enviar_socket({
        "op": "login",
        "email": data["email"],
        "senha": data["senha"]
    }))

@app.route("/criar", methods=["POST"])
def criar_usuario():
    data = request.json
    return jsonify(enviar_socket({
        "op": "criar_usuario",
        "nome": data["nome"],
        "email": data["email"],
        "senha": data["senha"],
        "tipo": data["tipo"]
    }))

@app.route("/listar", methods=["GET"])
def listar():
    return jsonify(enviar_socket({"op": "listar"}))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
