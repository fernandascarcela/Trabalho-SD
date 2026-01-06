import pika
import json
import time
import requests
import getpass

# ---------------- CONFIGURAÇÕES ----------------
RABBITMQ_HOST = "localhost"
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

            # Define um nome fixo para a fila baseada no email
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
    print("=== SISTEMA DE NOTIFICAÇÕES (PACIENTE) ===\n")

    email = input("Email: ").strip()
    
    iniciar_consumidor(email)