import pika
import json

RABBITMQ_HOST = "localhost"   # no Docker depois vira o nome do serviço
QUEUE_NAME = "notificacoes_paciente"


def callback(ch, method, properties, body):
    mensagem = json.loads(body)
    print("\n📢 NOVA NOTIFICAÇÃO RECEBIDA")
    print(f"Consulta ID: {mensagem['consulta_id']}")
    print(f"Status: {mensagem['status']}")
    print(f"Mensagem: {mensagem['mensagem']}")
    print("-" * 40)


def main():
    print("🔔 Aguardando notificações... (CTRL+C para sair)")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
