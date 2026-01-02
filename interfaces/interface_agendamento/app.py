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

def erro(msg, status=400):
    return jsonify({"erro": msg}), status


# ------------------- CRUD de Atendimentos -------------------
@app.post("/<perfil_operador>/atendimentos/criar")
def criar_atendimento(perfil_operador):
    if perfil_operador not in ["admin", "medico"]:
        return erro("Perfil sem permissão")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json
    obrigatorios = ["email_operador", "senha_operador", "data", "horario"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        
        resposta = rpc_client.criar_atendimento(
            body["email_operador"],
            body["senha_operador"],
            body["id_consulta"],
            body["data"],
            body["horario"]
        )
        return jsonify(resposta), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.post("/atendimentos/listar")
def listar_atendimentos():
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json

    medico = body.get("medico")
    especialidade = body.get("especialidade")

    try:
        resposta = rpc_client.listar_atendimentos(
            medico,
            especialidade
        )
        return jsonify(resposta), 200

    except Exception as e:
        return erro(str(e), 500)

@app.post("/<perfil_operador>/atendimentos/excluir")
def excluir_atendimento(perfil_operador):
    if perfil_operador not in ["admin", "medico"]:
        return erro("Perfil sem permissão")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json
    obrigatorios = ["email_operador", "senha_operador", "id_atendimento"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = rpc_client.excluir_atendimento(
            body["email_operador"],
            body["senha_operador"],
            body["id_atendimento"]
        )
        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.post("/<perfil_operador>/atendimentos/editar")
def editar_atendimento(perfil_operador):
    if perfil_operador not in ["admin", "medico"]:
        return erro("Perfil sem permissão")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json
    obrigatorios = ["email_operador", "senha_operador", "id_atendimento"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = rpc_client.editar_atendimento(
            body["email_operador"],
            body["senha_operador"],
            body["id_atendimento"],
            body["data"],
            body["horario"]
        )
        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.post("/<perfil_operador>/atendimentos/status")
def atualizar_status_atendimento(perfil_operador):
    if perfil_operador not in ["admin", "medico"]:
        return erro("Perfil sem permissão")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json
    obrigatorios = ["email_operador", "senha_operador", "id_atendimento", "status"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = rpc_client.atualizar_status_atendimento(
            body["email_operador"],
            body["senha_operador"],
            body["id_atendimento"],
            body["status"]
        )
        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# --------------- Consultas marcadas -------------------
@app.post("/<perfil_operador>/consultas/agendadas")
def consultas_agendadas(perfil_operador):
    if perfil_operador not in ["admin", "medico", "paciente"]:
        return erro("Perfil sem permissão para acessar consultas marcadas")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json
    obrigatorios = ["perfil_operador", "email_operador", "senha_operador", "email_medico"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = rpc_client.consultas_agendadas(
            body["email_operador"],
            body["senha_operador"],
            body["email_medico"],
            body["data"],
            body["status"]
        )
        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
