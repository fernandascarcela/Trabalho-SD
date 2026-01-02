import psycopg2
import os
from psycopg2.extras import RealDictCursor
from psycopg2 import errors

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
def editar_paciente(email_atual, nome=None, senha=None, cpf=None, novo_email=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Pega o user_id do paciente que vai editar
        cur.execute("SELECT user_id FROM users WHERE email = %s", (email_atual,))
        user = cur.fetchone()

        user_id = user[0]

        # ---- Atualiza tabela users ----
        updates = []
        valores = []

        if nome:
            updates.append("name = %s")
            valores.append(nome)

        if senha:
            updates.append("password = %s")
            valores.append(senha)

        if novo_email:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (novo_email,))
            existente = cur.fetchone()

            if existente and existente[0] != user_id:
                return {"erro": "Email já cadastrado"}
            
            updates.append("email = %s")
            valores.append(novo_email)

        if updates:
            set_clause = ", ".join(updates)
            cur.execute(f"""
                UPDATE users
                SET {set_clause}
                WHERE user_id = %s
            """, (*valores, user_id))

        if cpf:
            cur.execute("SELECT user_id FROM patient WHERE cpf = %s", (cpf,))
            existente = cur.fetchone()

            if existente and existente[0] != user_id:
                return {"erro": "CPF já cadastrado"}

            cur.execute("""
                UPDATE patient
                SET cpf = %s
                WHERE user_id = %s
            """, (cpf, user_id))

        conn.commit()
        return {"mensagem": "Paciente atualizado com sucesso"}

    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

def editar_medico(email_atual, nome=None, senha=None, crm=None, especialidade=None, novo_email=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (email_atual,))
        user = cur.fetchone()

        user_id = user[0]

        updates = []
        valores = []

        if nome:
            updates.append("name = %s")
            valores.append(nome)

        if senha:
            updates.append("password = %s")
            valores.append(senha)

        if novo_email:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (novo_email,))
            existente = cur.fetchone()

            if existente and existente[0] != user_id:
                return {"erro": "Email já cadastrado"}
            
            updates.append("email = %s")
            valores.append(novo_email)

        if updates:
            set_clause = ", ".join(updates)
            cur.execute(f"""
                UPDATE users
                SET {set_clause}
                WHERE user_id = %s
            """, (*valores, user_id))

        if crm:
            cur.execute("SELECT user_id FROM doctor WHERE crm = %s", (crm,))
            existente = cur.fetchone()

            if existente and existente[0] != user_id:
                return {"erro": "CRM já cadastrado"}
            
            cur.execute("""
                UPDATE doctor
                SET crm = %s
                WHERE user_id = %s
            """, (crm, user_id))

        if especialidade:
            cur.execute("""
                UPDATE doctor
                SET specialty = %s
                WHERE user_id = %s
            """, (especialidade.upper(), user_id))

        conn.commit()
        return {"mensagem": "Médico atualizado com sucesso"}
    
    except errors.InvalidTextRepresentation:
        conn.rollback()
        return {"erro": "Especialidade nova inválida"}
    
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

def editar_recepcionista_admin(email_atual, nome=None, senha=None, novo_email=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (email_atual,))
        user = cur.fetchone()

        user_id = user[0]

        updates = []
        valores = []

        if nome:
            updates.append("name = %s")
            valores.append(nome)

        if senha:
            updates.append("password = %s")
            valores.append(senha)

        if novo_email:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (novo_email,))
            existente = cur.fetchone()

            if existente and existente[0] != user_id:
                return {"erro": "Email já cadastrado"}
            
            updates.append("email = %s")
            valores.append(novo_email)

        if not updates:
            return {"erro": "Nenhum campo válido enviado para edição"}

        set_clause = ", ".join(updates)
        cur.execute(f"""
            UPDATE users
            SET {set_clause}
            WHERE user_id = %s
        """, (*valores, user_id))

        conn.commit()
        return {"mensagem": "Usuário atualizado com sucesso"}

    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()

#Função de exclusão de usuários
def excluir_usuarios(email):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE email = %s RETURNING user_id;", (email,))
        resultado = cur.fetchone()

        if resultado:
            conn.commit()
            return {"mensagem": f"Usuário {email} removido com sucesso!"}
        else:
            return {"erro": "Usuário não encontrado."}

    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": "Erro ao excluir usuário."}

    finally:
        cur.close()
        conn.close()

# Função de listagem de usuários
def listar_por_funcao(role):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if role.upper() not in ["PACIENTE", "MEDICO", "RECEPCIONISTA", "ADMIN"]:
            return {"erro": "Role inválida"}

        if role == "PACIENTE":
            cur.execute("""
                SELECT u.user_id, u.name, u.email, u.user_type, p.cpf
                FROM users u
                JOIN patient p ON u.user_id = p.user_id
                WHERE u.user_type = 'PACIENTE'
            """)
        elif role == "MEDICO":
            cur.execute("""
                SELECT u.user_id, u.name, u.email, u.user_type, d.crm, d.specialty
                FROM users u
                JOIN doctor d ON u.user_id = d.user_id
                WHERE u.user_type = 'MEDICO'
            """)
        else:
            cur.execute("""
                SELECT user_id, name, email, user_type
                FROM users
                WHERE user_type = %s
            """, (role.upper(),))

        usuarios = cur.fetchall()

        return {"usuarios": usuarios}

    except psycopg2.Error as e:
        return {"erro": str(e)}

    finally:
        cur.close()
        conn.close()