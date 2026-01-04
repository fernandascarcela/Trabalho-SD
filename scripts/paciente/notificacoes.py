import pika
import json
import time
import requests
import getpass

# ---------------- CONFIGURAÇÕES ----------------
RABBITMQ_HOST = "rabbitmq"
EXCHANGE_NAME = "notifications"

USUARIOS_AUTH_URL = "http://localhost:5001/login"
# -----------------------------------------------



# ---------- AUTENTICAÇÃO ----------
def validar_credenciais(email, senha):
    try:
        resp = requests.post(
            USUARIOS_AUTH_URL,
            json={
                "email": email,
                "senha": senha
            },
            timeout=5
        )
        return resp.status_code == 200
    except Exception as e:
        print("Erro ao validar credenciais:", e)
        return False


# ---------- CONSUMIDOR ----------
def iniciar_consumidor(email_usuario):
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600
                )
            )
            channel = connection.channel()

            # Garante que o exchange existe
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="fanout",
                durable=True
            )

            # Fila exclusiva para este consumidor
            result = channel.queue_declare(
                queue="",
                exclusive=True
            )
            queue_name = result.method.queue

            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue_name
            )

            print("\nAguardando notificações...\n")

            def callback(ch, method, properties, body):
                mensagem = json.loads(body)

                # FILTRA PELO EMAIL AUTENTICADO
                if mensagem.get("email") == email_usuario:
                    print("NOVA NOTIFICAÇÃO")
                    print(f"Mensagem: {mensagem.get('message')}")
                    print(f"Consulta ID: {mensagem.get('consultation_id')}")
                    print("-" * 40)

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True
            )

            channel.start_consuming()

        except pika.exceptions.AMQPError as e:
            print("Erro no RabbitMQ, tentando reconectar...", e)
            time.sleep(5)


# ---------- MAIN ----------
if __name__ == "__main__":
    print("=== SISTEMA DE NOTIFICAÇÕES ===\n")

    email = input("Email: ").strip()
    senha = getpass.getpass("Senha: ")

    if not validar_credenciais(email, senha):
        print("\nCredenciais inválidas. Acesso negado.")
        exit(1)

    print("\nLogin realizado com sucesso.")
    iniciar_consumidor(email)
