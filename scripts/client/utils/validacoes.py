import re

def email_valido(email):
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(padrao, email) is not None


def cpf_valido(cpf):
    # aceita 000.000.000-00 ou 00000000000
    padrao = r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$"
    return re.match(padrao, cpf) is not None


def senha_valida(senha):
    return len(senha) >= 6

def crm_valido(crm):
    return crm.isdigit()

