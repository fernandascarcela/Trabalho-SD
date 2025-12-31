import pika
import json
import psycopg2
import select
import time

RABBITMQ_HOST = 'rabbitmq'
EXCHANGE_NAME = 'notifications'

DB_CONFIG = {
    'host': 'postgres',
    'database': 'clinic_management_db',
    'user': 'admin',
    'password': 'admin123'
}

def connect_rabbitmq():
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
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type='fanout',
                durable=True
            )
            return connection, channel
        except pika.exceptions.AMQPError:
            time.sleep(5)

def connect_database():
    while True:
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            connection.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
            )
            return connection
        except Exception:
            time.sleep(5)

def fetch_notification(cursor, notification_id):
    cursor.execute("""
        SELECT n.notification_id,
               n.message,
               n.appointment_id,
               u.user_id,
               u.email
        FROM notification n
        JOIN users u ON u.user_id = n.user_id
        WHERE n.notification_id = %s
    """, (notification_id,))
    return cursor.fetchone()

def publish_notification(data):
    message = {
        "notification_id": data[0],
        "message": data[1],
        "consultation_id": data[2],
        "user_id": data[3],
        "email": data[4]
    }

    try:
        connection, channel = connect_rabbitmq()
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key='',
            body=json.dumps(message)
        )
        connection.close()
    except pika.exceptions.AMQPError:
        pass

def listen_notifications():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("LISTEN new_notification;")

    while True:
        if select.select([connection], [], [], 5) == ([], [], []):
            continue

        connection.poll()

        while connection.notifies:
            notify = connection.notifies.pop(0)
            data = fetch_notification(cursor, notify.payload)
            if data:
                publish_notification(data)

if __name__ == "__main__":
    listen_notifications()
