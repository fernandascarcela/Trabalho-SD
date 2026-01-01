from flask import Flask, request, jsonify
import xmlrpc.client
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

AGENDAMENTO_RPC_URL = os.getenv(
    "AGENDAMENTO_RPC_URL",
    "http://localhost:7001"
)

# Cliente RPC
rpc_client = xmlrpc.client.ServerProxy(
    AGENDAMENTO_RPC_URL,
    allow_none=True
)

def json_invalido():
    return jsonify({"erro": "JSON inválido"}), 400


# ---------- AGENDAMENTO ----------
@app.post("/agendamento/criar")
def criar_agendamento():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = ["email_paciente", "senha_paciente", "id_consulta"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        
        resposta = rpc_client.criar_agendamento(
            body["email_paciente"],
            body["senha_paciente"],
            body["id_consulta"],
            body["data"],
            body["horario"]
        )
        return jsonify(resposta), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.get("/agendamento/listar")
def listar_agendamentos():
    try:
        resposta = rpc_client.listar_agendamentos()
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.post("/agendamento/cancelar")
def cancelar_agendamento():
    if not request.is_json:
        return json_invalido()

    body = request.json
    if "agendamento_id" not in body:
        return jsonify({"erro": "agendamento_id obrigatório"}), 400

    try:
        resposta = rpc_client.cancelar_agendamento(body["agendamento_id"])
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
