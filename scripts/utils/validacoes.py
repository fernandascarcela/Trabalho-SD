import re

def email_valido(email):
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(padrao, email) is not None

def senha_valida(senha):
    return len(senha) >= 6


def verificar_credenciais(args):
    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return False

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida (mín. 6 caracteres).")
        return False

    return True

def cpf_valido(cpf):
    # aceita 000.000.000-00 ou 00000000000
    padrao = r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$"
    return re.match(padrao, cpf) is not None

def crm_valido(crm):
    return crm.isdigit()

def data_valida(data):
    # Formato: DD/MM/AAAA
    padrao = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
    return re.match(padrao, data) is not None

def horario_valido(horario):
    # Formato: HH:MM (24h)
    padrao = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"
    return re.match(padrao, horario) is not None


def eh_int(valor):
    try:
        int(valor)
        return True
    except (ValueError, TypeError):
        return False
