import requests
import pika
import threading
import json

API_AGENDAMENTO = "http://localhost:8001"
RABBITMQ_HOST = "localhost"


class ClienteMedico:
    def __init__(self):
        self.token = None
        self.medico_id = None

    def login(self):
        email = input("Email: ")
        senha = input("Senha: ")
        print("[REST] Login →", email)
        self.token = "TOKEN_FAKE"
        self.medico_id = 5

    # -----------------------
    # FUNÇÕES
    # -----------------------
    def ver_agenda(self):
        print(f"[REST] GET /agenda/medico/{self.medico_id}")

    def concluir_consulta(self):
        consulta_id = input("ID da consulta: ")
        print(f"[REST] Consulta {consulta_id} → concluída")

    def confirmar_consulta(self):
        consulta_id = input("ID da consulta: ")
        print(f"[REST] Consulta {consulta_id} → confirmada manualmente")

    # -----------------------
    # NOTIFICAÇÕES
    # -----------------------
    def receber_notificacoes(self):
        def callback(ch, method, props, body):
            print("\n🔔 [NOTIFICAÇÃO] ", json.loads(body.decode()), "\n> ", end="")

        def listen():
            conn = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            ch = conn.channel()
            queue = f"notificacoes_medico_{self.medico_id}"
            ch.queue_declare(queue=queue)
            ch.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            print("\n[MQ] Aguardando notificações...\n")
            ch.start_consuming()

        threading.Thread(target=listen, daemon=True).start()


if __name__ == "__main__":
    cli = ClienteMedico()
    cli.login()
    cli.receber_notificacoes()

    print("\n=== CLIENTE MÉDICO ===")

    while True:
        print("\n1. Ver agenda")
        print("2. Concluir consulta")
        print("3. Confirmar consulta")
        print("0. Sair")

        op = input("> ")

        if op == "1":
            cli.ver_agenda()
        elif op == "2":
            cli.concluir_consulta()
        elif op == "3":
            cli.confirmar_consulta()
        elif op == "0":
            break
