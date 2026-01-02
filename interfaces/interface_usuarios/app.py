from flask import Flask, request, jsonify
import socket
import json
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

SERVICO_HOST = os.getenv("SERVICO_HOST", "localhost")
SERVICO_PORT = int(os.getenv("SERVICO_PORT", 6001))
PROTOCOLO = "usuarios/1.0"

especialidades_validas = ['FISIOTERAPEUTA', 'NUTRICIONISTA', 'PISIQUIATRA', 'DERMATOLOGISTA', 'PEDIATRIA']
funcoes_validas = ['paciente', 'medico', 'recepcionista', 'admin']

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

def erro(msg, status=400):
    return jsonify({"erro": msg}), status

def operador_pode_criar(perfil_operador, role):
    if perfil_operador == "admin":
        return True
    if perfil_operador == "recepcionista" and role == "paciente":
        return True
    return False

@app.post("/<perfil_operador>/usuarios/registrar")
def registrar_usuario(perfil_operador):
    if perfil_operador not in ["admin", "recepcionista"]:
        return erro("Perfil de operador inválido")

    if not request.is_json:
        return erro("JSON inválido")

    body = request.json

    obrigatorios = [
        "email_operador",
        "senha_operador",
        "role",
        "nome",
        "email",
        "senha"
    ]

    if not all(c in body for c in obrigatorios):
        return erro("Campos obrigatórios ausentes")

    role = body["role"]

    if role not in funcoes_validas:
        return erro("Role inválida")

    if not operador_pode_criar(perfil_operador, role):
        return erro("Permissão negada")

    # ---- Validação por tipo ----
    if role == "medico":
        if "crm" not in body or "especialidade" not in body:
            return erro("CRM e especialidade são obrigatórios para médico")
        
        if body["especialidade"].upper() not in especialidades_validas:
            return erro("Especialidade inválida")

    if role == "paciente":
        if "cpf" not in body:
            return erro("CPF é obrigatório para paciente")

    # ---- Encaminha para serviço TCP ----
    resposta = enviar_para_servico(
        acao="registrar_usuario",
        dados=body
    )

    status = 201 if "erro" not in resposta else 400
    return jsonify(resposta), status

@app.post("/<perfil_operador>/usuarios/editar")
def editar_usuario(perfil_operador):
    if perfil_operador not in funcoes_validas:
        return erro("Perfil de operador inválido")
    
    if not request.is_json:
        return erro("JSON inválido")

    body = request.json

    obrigatorios = [
        "perfil_operador", 
        "email_operador", 
        "senha_operador"
    ]

    if not all(c in body for c in obrigatorios):
        return erro("Campos obrigatórios ausentes")

    auto_edicao = False

    if "email" not in body:
        auto_edicao = True
    else:
        if body["email"] == body["email_operador"]:
            auto_edicao = True

    # ---------- VALIDAÇÃO DE PERMISSÃO ----------
    if auto_edicao:
        if perfil_operador == "recepcionista":
            return erro("Recepcionista não pode editar a si mesmo")
    else:
        if perfil_operador not in ["admin", "recepcionista"]:
            return erro("Apenas admin ou recepcionista podem editar outros usuários")
        
        if "role" not in body:
            return erro("Role do usuário a ser editado é obrigatória")
            
        if perfil_operador == "recepcionista" and body["role"] not in ["paciente", "medico"]:
            return erro("Recepcionista só pode editar paciente ou médico")

    # ---------- ENCAMINHA PARA O SERVIÇO TCP ----------
    resposta = enviar_para_servico(
        acao="editar_usuario",
        dados=body
    )

    status = 200 if "erro" not in resposta else 400
    return jsonify(resposta), status

@app.post("/<perfil_operador>/usuarios/excluir")
def excluir_usuario(perfil_operador):
    if perfil_operador not in ["admin", "recepcionista"]:
        return erro("Perfil inválido")

    if not request.is_json:
        return erro("JSON inválido")

    body = request.json

    obrigatorios = [
        "email_operador",
        "senha_operador",
        "role",
        "email"
    ]

    if not all(c in body for c in obrigatorios):
        return erro("Campos obrigatórios ausentes")
    
    if body["role"] not in funcoes_validas:
        return erro("Role inválida")

    resposta = enviar_para_servico(
        acao="excluir_usuario",
        dados=body
    )

    status = 200 if "erro" not in resposta else 400
    return jsonify(resposta), status

@app.post("/<perfil_operador>/usuarios/listar")
def listar_usuarios(perfil_operador):
    if perfil_operador != "admin":
        return erro("Apenas admin pode listar usuários")

    if not request.is_json:
        return erro("JSON inválido")

    body = request.json

    obrigatorios = [
        "email_operador",
        "senha_operador",
        "role"
    ]

    if not all(c in body for c in obrigatorios):
        return erro("Campos obrigatórios ausentes")
    
    if body["role"] not in funcoes_validas:
        return erro("Role inválida")

    resposta = enviar_para_servico(
        acao="listar_usuarios",
        dados=body
    )

    status = 200 if "erro" not in resposta else 400
    return jsonify(resposta), status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
