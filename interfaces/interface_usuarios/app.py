from flask import Flask, request, jsonify
import socket
import json
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

SERVICO_HOST = os.getenv("SERVICO_HOST", "localhost")
SERVICO_PORT = int(os.getenv("SERVICO_PORT", 6001))
PROTOCOLO = "usuarios/1.0"


# ---------- Comunicação TCP ----------
def enviar_para_servico(acao, dados):
    mensagem = {
        "protocolo": PROTOCOLO,
        "tipo": "request",
        "acao": acao,
        "dados": dados
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVICO_HOST, SERVICO_PORT))
            s.sendall(json.dumps(mensagem).encode())
            resposta = s.recv(4096)

        return json.loads(resposta.decode())

    except Exception as e:
        raise RuntimeError(f"Erro ao comunicar com serviço TCP: {e}")


# ---------- Util ----------
def json_invalido():
    return jsonify({"erro": "JSON inválido"}), 400


# ---------- Endpoints ----------
@app.post("/usuarios")
def criar_usuario():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = ["nome", "email", "senha"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios: nome, email, senha"}), 400

    try:
        resposta = enviar_para_servico("criar_usuario", body)
        return jsonify(resposta), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.post("/usuarios/login")
def login():
    if not request.is_json:
        return json_invalido()

    body = request.json
    if "email" not in body or "senha" not in body:
        return jsonify({"erro": "Campos obrigatórios: email, senha"}), 400

    try:
        resposta = enviar_para_servico("login", body)
        return jsonify(resposta)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.patch("/usuarios")
def editar_usuario():
    if not request.is_json:
        return json_invalido()

    body = request.json
    if "email" not in body or "senha" not in body:
        return jsonify({"erro": "Campos obrigatórios: email, senha"}), 400

    try:
        resposta = enviar_para_servico("editar_usuario", body)
        return jsonify(resposta)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.delete("/usuarios/")
def excluir_usuario():
    if not request.is_json:
        return json_invalido()

    body = request.json
    if "email" not in body or "senha" not in body:
        return jsonify({"erro": "Campos obrigatórios: email, senha"}), 400

    try:
        resposta = enviar_para_servico("excluir_usuario", body)
        return jsonify(resposta)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
