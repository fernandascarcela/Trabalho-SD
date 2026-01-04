from flask import Flask, request, jsonify
import grpc
import convenio_pb2
import convenio_pb2_grpc


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

channel = grpc.insecure_channel("localhost:8001")
stub = convenio_pb2_grpc.ConvenioServiceStub(channel)

def json_invalido():
    return jsonify({"erro": "JSON inválido"}), 400


# ---------- CONVÊNIO ----------
@app.post("/convenio/validacao")
def cadastrar_convenio():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = ["perfil_operador", "email_operador", "senha_operador", "cpf_titular_convenio", "numero_carteirinha", "data_validade"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = stub.CadastrarConvenio(
            convenio_pb2.ConvenioRequest(
                perfil_operador=body["perfil_operador"],
                email_operador=body["email_operador"],
                senha_operador=body["senha_operador"],
                cpf_titular_convenio=body["cpf_titular_convenio"],
                numero_carteirinha=body["numero_carteirinha"],
                data_validade=body["data_validade"]
            )
        )
        return jsonify({
            "sucesso": resposta.sucesso,
            "mensagem": resposta.mensagem
        }), 201 if resposta.sucesso else 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
