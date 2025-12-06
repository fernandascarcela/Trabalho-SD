import requests
import pika
import threading
import json

API_USUARIOS = "http://localhost:8000"
API_AGENDAMENTO = "http://localhost:8001"
RABBITMQ_HOST = "localhost"

class ClienteRecepcionista:
    def __init__(self):
        self.token = None
        self.user_id = None

    def login(self):
        email = input("Email: ")
        senha = input("Senha: ")
        print("[REST] Login →", email)
        self.token = "TOKEN_FAKE"
        self.user_id = 10

    # -----------------------
    # FUNÇÕES
    # -----------------------
    def agendar_para_paciente(self):
        paciente = input("ID do paciente: ")
        medico = input("ID do médico: ")
        horario = input("Horário (YYYY-MM-DD HH:MM): ")

        payload = {
            "paciente_id": paciente,
            "medico_id": medico,
            "horario": horario
        }

        print("\n[REST] Agendar para paciente →", payload)

    def editar_consulta(self):
        consulta_id = input("ID da consulta: ")
        horario = input("Novo horário: ")
        print(f"[REST] Editando consulta {consulta_id} → {horario}")

    def cancelar_consulta(self):
        consulta_id = input("ID da consulta: ")
        print(f"[REST] Cancelando consulta {consulta_id}")

    def ver_agenda_medico(self):
        medico_id = input("ID do médico: ")
        print(f"[REST] GET /agenda/medico/{medico_id}")

    # -----------------------
    # NOTIFICAÇÕES
    # -----------------------
    def receber_notificacoes(self):
        def callback(ch, method, props, body):
            print("\n🔔 [NOTIFICAÇÃO] ", json.loads(body.decode()), "\n> ", end="")

        def listen():
            conn = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            ch = conn.channel()
            queue = "notificacoes_recepcionista"
            ch.queue_declare(queue=queue)
            ch.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            print("\n[MQ] Aguardando notificações...\n")
            ch.start_consuming()

        threading.Thread(target=listen, daemon=True).start()


if __name__ == "__main__":
    cli = ClienteRecepcionista()
    cli.login()
    cli.receber_notificacoes()

    print("\n=== CLIENTE RECEPCIONISTA ===")

    while True:
        print("\n1. Agendar para paciente")
        print("2. Editar consulta")
        print("3. Cancelar consulta")
        print("4. Ver agenda do médico")
        print("0. Sair")

        op = input("> ")

        if op == "1":
            cli.agendar_para_paciente()
        elif op == "2":
            cli.editar_consulta()
        elif op == "3":
            cli.cancelar_consulta()
        elif op == "4":
            cli.ver_agenda_medico()
        elif op == "0":
            break
