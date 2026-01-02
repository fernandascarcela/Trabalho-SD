import socket
import json

from handlers import tratar_acao

# Aceita conexões de qualquer container
HOST = "0.0.0.0"
PORT = 6001
# Garante que apenas mensagens com este protocolo sejam processadas
PROTOCOLO = "usuarios/1.0"


def tratar_requisicao(mensagem):
    if mensagem.get("protocolo") != PROTOCOLO:
        return {"erro": "Protocolo inválido"}

    acao = mensagem["acao"]
    dados = mensagem.get("dados")

    if not acao or not dados:
        return {"erro": "Mensagem mal formatada"}

    resposta = tratar_acao(acao, dados)

    return resposta


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()

        print(f"✅ Serviço de Usuários rodando na porta {PORT}")

        while True:
            conexao, endereco = servidor.accept()

            with conexao:
                try:
                    dados_recebidos = conexao.recv(4096)

                    if not dados_recebidos:
                        continue

                    mensagem = json.loads(dados_recebidos.decode())

                    resposta = tratar_requisicao(mensagem)

                except Exception as e:
                    resposta = {
                        "erro": f"Erro interno no serviço: {str(e)}"
                    }

                conexao.sendall(json.dumps(resposta).encode())


if __name__ == "__main__":
    main()
