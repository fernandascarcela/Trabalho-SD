from flask import Flask, request, jsonify
import grpc
import convenio_pb2
import convenio_pb2_grpc
import os

app = Flask(__name__)

# Configurações para forçar IPv4 e evitar falha de DNS no Docker
GRPC_SERVER_ADDRESS = os.getenv('GRPC_SERVER_ADDRESS', 'localhost:50051')
OPTIONS = [
    ('grpc.dns_enable_srv_queries', 0),
    ('grpc.address_family', 'ipv4') 
]

@app.route('/convenio/validacao', methods=['POST'])
def validar_convenio():
    dados = request.json
    print(f"\n[Interface] Recebi requisição REST: {dados}")

    try:
        # ADICIONADO: options=OPTIONS aqui é o que resolve o erro de DNS!
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS, options=OPTIONS) as channel:
            stub = convenio_pb2_grpc.ConvenioServiceStub(channel)
            
            grpc_request = convenio_pb2.ValidarConvenioRequest(
                email=dados.get('email_operador'),
                senha=dados.get('senha_operador'),
                cpf=dados.get('cpf_titular_convenio'),
                numeroCarteirinha=dados.get('numero_carteirinha'),
                dataDeValidade=dados.get('data_de_validade')
            )

            print("[Interface] Enviando para o Java via gRPC...")
            grpc_response = stub.validarConvenio(grpc_request)

            resposta_json = {
                "sucesso": grpc_response.sucesso,
                "mensagem": grpc_response.mensagem
            }
            
            print(f"[Interface] Resposta do Java: {resposta_json}")
            return jsonify(resposta_json), 200

    except grpc.RpcError as e:
        erro_msg = f"Erro de comunicação gRPC: {e.details()}"
        print(erro_msg)
        return jsonify({"sucesso": False, "mensagem": erro_msg}), 500
    except Exception as e:
        erro_msg = f"Erro interno na interface: {str(e)}"
        print(erro_msg)
        return jsonify({"sucesso": False, "mensagem": erro_msg}), 500

if __name__ == '__main__':
    print(f">>> Interface conectando em: {GRPC_SERVER_ADDRESS}")
    app.run(host='0.0.0.0', port=5003, debug=True)