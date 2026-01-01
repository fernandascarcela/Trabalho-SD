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
@app.post("/validacao/cadastrar")
def cadastrar_convenio():
    if not request.is_json:
        return json_invalido()

    body = request.json
    obrigatorios = ["nome", "codigo"]

    if not all(c in body for c in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        resposta = stub.CadastrarConvenio(
            convenio_pb2.ConvenioRequest(
                nome=body["nome"],
                codigo=body["codigo"]
            )
        )
        return jsonify({
            "sucesso": resposta.sucesso,
            "mensagem": resposta.mensagem
        }), 201 if resposta.sucesso else 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.post("/convenio/validar")
def validar_convenio():
    if not request.is_json:
        return json_invalido()

    body = request.json
    if "codigo" not in body:
        return jsonify({"erro": "Código obrigatório"}), 400

    try:
        resposta = stub.ValidarConvenio(
            convenio_pb2.ValidacaoRequest(codigo=body["codigo"])
        )
        return jsonify({
            "valido": resposta.valido,
            "mensagem": resposta.mensagem
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
