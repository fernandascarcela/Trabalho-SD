
from datetime import date, datetime, time
from psycopg2.extras import RealDictRow

from database import get_user


def normalizar_data(data_str: str) -> str:
    data_str = data_str.strip()
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        pass

    try:
        return datetime.strptime(data_str, "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError("Data inválida. Use 'YYYY-MM-DD' ou 'DD/MM/YYYY'.")



def to_plain(obj):
    if isinstance(obj, RealDictRow):
        obj = dict(obj)

    if isinstance(obj, (list, tuple)):
        return [to_plain(x) for x in obj]

    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}


    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.strftime("%H:%M:%S")

    return obj


def map_status_cli_to_db(status):
    if status is None:
        return None
    s = status.strip().lower()
    mapping = {
        "confirmado": "CONFIRMADO",
        "concluido": "CONCLUÍDO",
        "cancelado": "CANCELADO",
        "pendente": "PENDENTE",
    }
    if s not in mapping:
        raise ValueError("Status inválido (use confirmado|concluido|cancelado|pendente).")
    return mapping[s]


def validar_cartao_data_validade(data_validade):

    if not data_validade:
        raise ValueError("Data de validade do cartão é obrigatória.")

    dv = data_validade.strip()
    for fmt in ("%m/%y", "%m/%Y", "%m-%y", "%m-%Y"):
        try:
            dt = datetime.strptime(dv, fmt)
            ano = dt.year
            mes = dt.month

            hoje = datetime.now()
            if (ano, mes) < (hoje.year, hoje.month):
                raise ValueError("Cartão expirado.")
            return True
        except ValueError:

            continue

    raise ValueError("Formato inválido de data_validade (use MM/YY ou MM/YYYY).")


def auth_operador(email_operador, senha_operador, perfil_operador_esperado=None):
    user = get_user(email_operador, senha_operador)
    if not user:
        return None


    if perfil_operador_esperado:
        perfil = perfil_operador_esperado.strip().lower()
        tipo = user["user_type"]
        mapa = {
            "admin": "ADMIN",
            "medico": "MEDICO",
            "paciente": "PACIENTE",
            "recepcionista": "RECEPCIONISTA",
        }
        if perfil in mapa and tipo != mapa[perfil]:
            return None

    return user
