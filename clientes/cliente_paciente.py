import requests
import pika
import threading
import json

API_USUARIOS = "http://localhost:8000"
API_AGENDAMENTO = "http://localhost:8001"
RABBITMQ_HOST = "localhost"


class ClientePaciente:
    def __init__(self):
        self.token = None
        self.user_id = None

    # ----------------------
    # AUTENTICAÇÃO
    # ----------------------
    def criar_conta(self):
        nome = input("Nome: ")
        email = input("Email: ")
        senha = input("Senha: ")

        payload = {"nome": nome, "email": email, "senha": senha}

        print("\n[REST] Criando conta →", payload)
        #resp = requests.post(f"{API_USUARIOS}/criar", json=payload)


    def login(self):
        email = input("Email: ")
        senha = input("Senha: ")

        print("\n[REST] Login →", {"email": email})

        # resp = requests.post(f"{API_USUARIOS}/login", json={"email": email, "senha": senha})
        # obj = resp.json()
        # self.token = obj["token"]
        # self.user_id = obj["id"]

        self.token = "TOKEN_FAKE"
        self.user_id = 1

    # ----------------------
    # FUNÇÕES DO PACIENTE
    # ----------------------
    def listar_medicos(self):
        print("\n[REST] GET /medicos/listar")
        # requests.get(f"{API_AGENDAMENTO}/medicos")

    def agendar_consulta(self):
        medico_id = input("ID do médico: ")
        horario = input("Horário (YYYY-MM-DD HH:MM): ")

        payload = {
            "paciente_id": self.user_id,
            "medico_id": medico_id,
            "horario": horario
        }

        print("\n[REST] Agendando consulta →", payload)
        # requests.post(f"{API_AGENDAMENTO}/consultas", json=payload)

    def consultar_status(self):
        print(f"\n[REST] GET /consultas/paciente/{self.user_id}")
        # requests.get(...)

    # ----------------------
    # NOTIFICAÇÕES (RabbitMQ)
    # ----------------------
    def receber_notificacoes(self):
        def callback(ch, method, properties, body):
            msg = json.loads(body.decode())
            print(f"\n🔔 [NOTIFICAÇÃO] {msg}\n> ", end="")

        def listen():
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            channel = connection.channel()
            queue = f"notificacoes_paciente_{self.user_id}"
            channel.queue_declare(queue=queue)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            print("\n[MQ] Aguardando notificações...\n")
            channel.start_consuming()

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()


if __name__ == "__main__":
    cli = ClientePaciente()

    print("\n=== CLIENTE PACIENTE ===")
    cli.login()
    cli.receber_notificacoes()

    while True:
        print("\n1. Listar médicos")
        print("2. Agendar consulta")
        print("3. Consultar status")
        print("0. Sair")

        op = input("> ")

        if op == "1":
            cli.listar_medicos()
        elif op == "2":
            cli.agendar_consulta()
        elif op == "3":
            cli.consultar_status()
        elif op == "0":
            break