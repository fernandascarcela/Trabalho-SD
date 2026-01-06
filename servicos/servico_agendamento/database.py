import os
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "clinic_management_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def get_user(email, senha):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT user_id, name, email, user_type FROM users WHERE email=%s AND password=%s",
                (email, senha)
            )
            return cur.fetchone()
        
def get_doctor_by_user_id(user_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM doctor WHERE user_id = %s",
                (user_id,)
            )
            return cur.fetchone()

def get_schedule_by_id(schedule_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM schedule WHERE schedule_id = %s",
                (schedule_id,)
            )
            return cur.fetchone()

def check_conflit_schedule(doctor_id, date, start_time):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT schedule_id
                FROM schedule
                WHERE doctor_id = %s
                    AND schedule_date = %s::date
                    AND start_time = %s::time
                """,
                (doctor_id, date, start_time)
            )

            return cur.fetchone() is not None
        

def get_patient_id_by_user_id(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT patient_id FROM patient WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None


def get_doctor_id_by_email(email_medico):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.doctor_id
                FROM users u
                JOIN doctor d ON d.user_id = u.user_id
                WHERE u.email=%s AND u.user_type='MEDICO'
                """,
                (email_medico,),
            )
            row = cur.fetchone()
            return row[0] if row else None
        
def get_patient_id_by_email(email_paciente):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.patient_id
                FROM users u
                JOIN patient p ON p.user_id = u.user_id
                WHERE u.email=%s AND u.user_type='PACIENTE'
                """,
                (email_paciente,),
            )
            row = cur.fetchone()
            return row[0] if row else None

# Funcoes auxiliares de criacao de horários de atendimento

def doctor_create_schedule(operador):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT doctor_id, specialty
                FROM doctor
                WHERE user_id = %s
                """,
                (operador["user_id"],)
            )
            return cur.fetchone()


def admin_create_schedule(email_medico):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                    SELECT d.doctor_id, d.specialty
                    FROM users u
                    JOIN doctor d ON d.user_id = u.user_id
                    WHERE u.email = %s AND u.user_type = 'MEDICO'
                    """,
                    (email_medico,)
                )
            return cur.fetchone()


def insert_schedule(doctor_id, date, start_time, specialty):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO schedule (doctor_id, schedule_date, start_time, specialty, is_available)
                VALUES (%s, %s::date, %s::time, %s::specialty_enum, TRUE)
                RETURNING schedule_id, doctor_id, schedule_date, start_time, specialty, is_available
            """, (doctor_id, date, start_time, specialty))

            return cur.fetchone(), None

# Funcoes auxiliares de listagem de horários de atendimento por médico

def get_doctor_by_name(doctor_name=None, specialty=None):
    query = """
        SELECT d.doctor_id, u.name, d.specialty
        FROM doctor d
        JOIN users u ON u.user_id = d.user_id
        WHERE u.user_type = 'MEDICO'
    """
    params = []

    if doctor_name:
        query += " AND u.name ILIKE %s"
        params.append(f"%{doctor_name}%")

    if specialty:
        query += " AND d.specialty = %s"
        params.append(specialty)

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            return cur.fetchone()

def get_list_of_schedules(doctor_id=None, specialty=None):
    query = """
        SELECT *
        FROM schedule
        WHERE 1=1
    """
    params = []

    if doctor_id is not None:
        query += " AND doctor_id = %s"
        params.append(doctor_id)

    if specialty:
        query += " AND specialty = %s"
        params.append(specialty)

    query += " ORDER BY schedule_date, start_time"

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()

# Funcoes auxiliares de exclusão de horários de atendimento
def delete_schedule_by_id(schedule_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                DELETE FROM schedule WHERE schedule_id = %s
                RETURNING schedule_id
            """, (schedule_id,))

            return cur.fetchone()
        

# Funcoes auxiliares de editar horários de atendimento
def edit_schedule(shecule_id, date, start_time):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE schedule
                SET schedule_date = %s, start_time = %s
                WHERE schedule_id = %s
                RETURNING *
            """, (date, start_time, shecule_id))

            return cur.fetchone()
        
# Agendamento

def set_schedule_available(schedule_id, is_available: bool):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE schedule SET is_available=%s WHERE schedule_id=%s",
                (is_available, schedule_id),
            )


def insert_appointment(patient_id, schedule_id, status="AGENDADO", insurance_id=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO appointment (patient_id, insurance_id, schedule_id, status)
                VALUES (%s, %s, %s, %s::appointment_status_enum)
                RETURNING appointment_id, patient_id, insurance_id, schedule_id, status
                """,
                (patient_id, insurance_id, schedule_id, status),
            )
            return cur.fetchone()


def list_appointments_by_doctor(doctor_id, date=None, status_db=None):
    query = """
        SELECT
            a.appointment_id,
            a.status,
            s.schedule_date AS data,
            s.start_time AS horario,
            u_p.name AS paciente,
            u_d.name AS medico,
            d.specialty AS especialidade,
            s.schedule_id
        FROM appointment a
        JOIN schedule s ON s.schedule_id = a.schedule_id
        JOIN doctor d ON d.doctor_id = s.doctor_id
        JOIN users u_d ON u_d.user_id = d.user_id
        JOIN patient p ON p.patient_id = a.patient_id
        JOIN users u_p ON u_p.user_id = p.user_id
        WHERE d.doctor_id = %s
    """
    params = [doctor_id]

    if date:
        query += " AND s.schedule_date = %s::date"
        params.append(date)

    if status_db:
        query += " AND a.status = %s::appointment_status_enum"
        params.append(status_db)

    query += " ORDER BY s.schedule_date DESC, s.start_time DESC"

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()
        
def get_insurance_by_patient_id(patient_id: int):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    i.insurance_id,
                    i.patient_id,
                    i.card_number,
                    i.expiration_date,
                    i.status,
                    COALESCE(
                        ARRAY_AGG(ispec.specialty)
                        FILTER (WHERE ispec.specialty IS NOT NULL),
                        '{}'
                    ) AS specialties
                FROM insurance i
                LEFT JOIN insurance_specialty ispec
                    ON ispec.insurance_id = i.insurance_id
                WHERE i.patient_id = %s
                  AND i.status = 'VALIDO'
                GROUP BY i.insurance_id
                ORDER BY i.expiration_date DESC
                LIMIT 1
                """,
                (patient_id,)
            )
            row = cur.fetchone()

    return dict(row) if row else None


def get_appointment_with_schedule(appointment_id: int):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    a.appointment_id,
                    a.patient_id,
                    a.insurance_id,
                    a.schedule_id,
                    a.status,
                    s.doctor_id,
                    s.is_available
                FROM appointment a
                JOIN schedule s ON s.schedule_id = a.schedule_id
                WHERE a.appointment_id = %s
                """,
                (appointment_id,)
            )
            row = cur.fetchone()
    return dict(row) if row else None


def update_appointment_status(appointment_id: int, new_status: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE appointment
                SET status = %s::appointment_status_enum
                WHERE appointment_id = %s
                RETURNING appointment_id, patient_id, insurance_id, schedule_id, status
                """,
                (new_status, appointment_id)
            )
            row = cur.fetchone()
    return dict(row) if row else None