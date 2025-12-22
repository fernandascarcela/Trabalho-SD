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
        return {"erro": f"Erro TCP: {e}"}


def json_invalido():
    return jsonify({"erro": "JSON inválido"}), 400


# ---------- PACIENTE ----------
@app.post("/paciente/registro")
def registrar():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = [
        "nome_paciente",
        "email_paciente",
        "senha_paciente",
    ]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resposta = enviar_para_servico(
        "paciente_registrar",
        body
    )

    return jsonify(resposta), 201 if "erro" not in resposta else 400


@app.delete("/paciente/excluir")
def excluir():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = [
        "email_paciente",
        "senha_paciente",
    ]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resposta = enviar_para_servico(
        "paciente_excluir",
        body
    )

    return jsonify(resposta), 201 if "erro" not in resposta else 400



# ---------- ADMIN ----------
@app.post("/admin/medico/criar")
def admin_criar_medico():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = [
        "email_admin",
        "senha_admin",
        "nome_medico",
        "email_medico",
        "senha_medico",
        "especialidade"
    ]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resposta = enviar_para_servico(
        "admin_criar_medico",
        body
    )

    return jsonify(resposta), 201 if "erro" not in resposta else 400


@app.post("/admin/paciente/criar")
def admin_criar_paciente():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = [
        "email_admin",
        "senha_admin",
        "nome_paciente",
        "email_paciente",
        "senha_paciente"
    ]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resposta = enviar_para_servico(
        "admin_criar_paciente",
        body
    )

    return jsonify(resposta), 201 if "erro" not in resposta else 400


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
