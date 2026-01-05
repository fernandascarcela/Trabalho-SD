
from datetime import date, datetime, time
from psycopg2.extras import RealDictRow

from database import get_user


def normalizar_data(data_str: str) -> str:
    """
    Aceita 'YYYY-MM-DD' ou 'DD/MM/YYYY' e devolve sempre 'YYYY-MM-DD'.
    """
    data_str = data_str.strip()
    try:
        # já no formato ISO
        return datetime.strptime(data_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        pass

    try:
        # formato BR
        return datetime.strptime(data_str, "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError("Data inválida. Use 'YYYY-MM-DD' ou 'DD/MM/YYYY'.")



def to_plain(obj):
    # RealDictRow -> dict
    if isinstance(obj, RealDictRow):
        obj = dict(obj)

    # list/tuple -> list
    if isinstance(obj, (list, tuple)):
        return [to_plain(x) for x in obj]

    # dict -> dict (recursivo)
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}

    # date/time/datetime -> string
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.strftime("%H:%M:%S")

    return obj


def map_status_cli_to_db(status):
    """
    CLI: confirmado, concluido, cancelado, pendente
    DB enum (do seu schema): CONFIRMADO, CONCLUÍDO, CANCELADO, PENDENTE, etc.
    """
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
    """
    Aceita 'MM/YY', 'MM/YYYY', 'MM-YY', 'MM-YYYY'
    Verifica se não está expirado.
    """
    if not data_validade:
        raise ValueError("Data de validade do cartão é obrigatória.")

    dv = data_validade.strip()
    for fmt in ("%m/%y", "%m/%Y", "%m-%y", "%m-%Y"):
        try:
            dt = datetime.strptime(dv, fmt)
            ano = dt.year
            mes = dt.month
            # considera válido até o fim do mês
            hoje = datetime.now()
            if (ano, mes) < (hoje.year, hoje.month):
                raise ValueError("Cartão expirado.")
            return True
        except ValueError:
            # tenta próximo formato
            continue

    raise ValueError("Formato inválido de data_validade (use MM/YY ou MM/YYYY).")


def auth_operador(email_operador, senha_operador, perfil_operador_esperado=None):
    user = get_user(email_operador, senha_operador)
    if not user:
        return None

    # se quiser conferir coerência entre perfil informado e user_type do banco:
    if perfil_operador_esperado:
        perfil = perfil_operador_esperado.strip().lower()
        tipo = user["user_type"]
        # mapeia perfis do CLI/HTTP -> tipos do DB
        mapa = {
            "admin": "ADMIN",
            "medico": "MEDICO",
            "paciente": "PACIENTE",
            "recepcionista": "RECEPCIONISTA",
        }
        if perfil in mapa and tipo != mapa[perfil]:
            return None

    return user
