import psycopg2
import os
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
from werkzeug.security import generate_password_hash

# =============================
# Configuração do banco
# =============================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "clinica")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

# Login do usuário
def buscar_usuario_por_email(email):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT user_id, email, password, user_type
        FROM users
        WHERE email = %s
    """, (email,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return usuario


# Funções de criação de usuários
def criar_paciente(nome, email, senha, cpf):
    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO users (name, email, password, user_type)
            VALUES (%s, %s, %s, 'PACIENTE')
            RETURNING user_id
        """, (nome, email, senha))

        user_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO patient (user_id, cpf)
            VALUES (%s, %s)
        """, (user_id, cpf))

        conn.commit()
        return {"mensagem": "Paciente criado com sucesso"}

    except errors.UniqueViolation:
        conn.rollback()
        return {"erro": "Email ou CPF já cadastrado"}
    
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

def criar_recepcionista(nome, email, senha):
    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO users (name, email, password, user_type)
            VALUES (%s, %s, %s, 'RECEPCIONISTA')
        """, (nome, email, senha))

        conn.commit()
        return {"mensagem": "Recepcionista criado com sucesso"}

    except errors.UniqueViolation:
        conn.rollback()
        return {"erro": "Email já cadastrado"}
    
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

def criar_admin(nome, email, senha):
    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO users (name, email, password, user_type)
            VALUES (%s, %s, %s, 'ADMIN')
        """, (nome, email, senha))

        conn.commit()
        return {"mensagem": "Admin criado com sucesso"}

    except errors.UniqueViolation:
        conn.rollback()
        return {"erro": "Email já cadastrado"}
    
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

def criar_medico(nome, email, senha, crm, especialidade):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (name, email, password, user_type)
            VALUES (%s, %s, %s, 'MEDICO')
            RETURNING user_id
        """, (nome, email, senha))

        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO doctor (user_id, crm, specialty)
            VALUES (%s, %s, %s)
        """, (user_id, crm, especialidade))

        conn.commit()
        return {"mensagem": "Médico criado com sucesso"}
    
    except errors.InvalidTextRepresentation:
        conn.rollback()
        return {"erro": "Especialidade inválida"}

    except errors.UniqueViolation:
        conn.rollback()
        return {"erro": "Email ou CRM já cadastrado"}

    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cursor.close()
        conn.close()

# Funções de edição de usuários
