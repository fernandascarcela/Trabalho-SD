import pika
import json
import time
import requests
import argparse
import sys

# ---------------- CONFIGURAÇÕES ----------------
RABBITMQ_HOST = "rabbitmq"
EXCHANGE_NAME = "notifications"

USUARIOS_AUTH_URL = "http://interface_usuarios:5001/login"
# -----------------------------------------------

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

        if resp.status_code == 200:
            return True

        print("Falha no login:", resp.json())
        return False

    except requests.exceptions.RequestException as e:
        print("Erro ao conectar na interface de usuários:", e)
        return False


# ---------- CONSUMIDOR ----------
def iniciar_consumidor(email_usuario):
    print(f"[*] Conectando ao RabbitMQ em {RABBITMQ_HOST}...")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            channel = connection.channel()

            # Garante que o exchange existe
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="fanout",
                durable=True
            )

            # Nome fixo da fila baseado no email
            queue_name = f"fila_{email_usuario}"

            channel.queue_declare(
                queue=queue_name,
                durable=True,
                exclusive=False,
                auto_delete=False
            )

            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue_name
            )

            print("\nAguardando notificações...\n")

            def callback(ch, method, properties, body):
                try:
                    mensagem = json.loads(body)

                    # Filtra mensagens apenas para este usuário
                    if mensagem.get("email") == email_usuario:
                        print("NOVA NOTIFICAÇÃO")
                        print(f"Mensagem: {mensagem.get('message')}")
                        print(f"Consulta ID: {mensagem.get('consultation_id')}")
                        print("-" * 40)

                except Exception as e:
                    print(f"Erro ao ler mensagem: {e}")

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True
            )

            channel.start_consuming()

        except pika.exceptions.AMQPError as e:
            print(f"Erro de conexão: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nEncerrando consumidor...")
            break


# ---------- MAIN ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sistema de Notificações (Paciente)"
    )
    parser.add_argument("email", help="Email do paciente")
    parser.add_argument("senha", help="Senha do paciente")

    args = parser.parse_args()

    email = args.email
    senha = args.senha
    

    print("=== SISTEMA DE NOTIFICAÇÕES (PACIENTE) ===\n")

    if not validar_credenciais(email, senha ):
        print("Credenciais inválidas. Acesso negado.")
        sys.exit(1)

    print("Login realizado com sucesso.")
    iniciar_consumidor(email)