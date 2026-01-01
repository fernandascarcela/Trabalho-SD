import argparse
import requests
import sys
from utils.validacoes import email_valido, cpf_valido, senha_valida, crm_valido


def criar_usuario(args):

    # ---- Permissões ----
    if args.perfil_operador == "recepcionista" and args.role != "paciente":
        print(f"\nERRO: Como {args.perfil_operador}, você só tem permissão para criar 'paciente'.")
        return

    # ---- Validação do operador ----
    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida (mín. 6 caracteres).")
        return

    # ---- Validação do novo usuário ----
    if not email_valido(args.email):
        print("ERRO: E-mail do novo usuário inválido.")
        return

    if not senha_valida(args.senha):
        print("ERRO: Senha do novo usuário inválida (mín. 6 caracteres).")
        return

    # ---- Montagem base do payload ----
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "role": args.role,
        "nome": args.nome,
        "email": args.email,
        "senha": args.senha,
    }

    # ---- Paciente ----
    if args.role == "paciente":
        if not args.cpf:
            print("ERRO: Paciente precisa de CPF.")
            return

        if not cpf_valido(args.cpf):
            print("ERRO: CPF inválido.")
            return

        payload["cpf"] = args.cpf

    # ---- Médico ----
    if args.role == "medico":
        if not args.crm:
            print("ERRO: Médico precisa de CRM.")
            return

        if not crm_valido(args.crm):
            print("ERRO: CRM inválido. Deve conter apenas números.")
            return

        if not args.especialidade:
            print("ERRO: Médico precisa de especialidade.")
            return

        payload["crm"] = args.crm
        payload["especialidade"] = args.especialidade

    endpoint = "admin" if args.perfil_operador == "admin" else "recepcionista"

    try:
        resp = requests.post(
            f"http://localhost:5001/{endpoint}/usuarios/registrar",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def editar_usuario(args):

    if args.perfil_operador == "recepcionista" and args.role not in ["paciente", "medico"]:
        print(f"\nERRO: Como {args.perfil_operador}, você só pode editar 'paciente' ou 'medico'.")
        return

    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida.")
        return

    if not email_valido(args.email):
        print("ERRO: E-mail do usuário a ser editado inválido.")
        return

    if args.nova_senha and not senha_valida(args.nova_senha):
        print("ERRO: Nova senha inválida (mín. 6 caracteres).")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "role": args.role,
        "email": args.email,
    }

    if args.novo_nome:
        payload["nome"] = args.novo_nome

    if args.nova_senha:
        payload["senha"] = args.nova_senha

    if args.nova_especialidade:
        payload["especialidade"] = args.nova_especialidade

    endpoint = "admin" if args.perfil_operador == "admin" else "recepcionista"

    try:
        resp = requests.post(
            f"http://localhost:5001/{endpoint}/usuarios/editar",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def excluir_usuario(args):

    if args.perfil_operador == "recepcionista" and args.role != "paciente":
        print(f"\nERRO: Como {args.perfil_operador}, você só pode excluir 'paciente'.")
        return

    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida.")
        return

    if not email_valido(args.email):
        print("ERRO: E-mail do usuário inválido.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "role": args.role,
        "email": args.email,
    }

    endpoint = "admin" if args.perfil_operador == "admin" else "recepcionista"

    try:
        resp = requests.post(
            f"http://localhost:5001/{endpoint}/usuarios/excluir",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestão de Usuários")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- Registrar ----
    criar = subparsers.add_parser("registrar")
    criar.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    criar.add_argument("email_operador")
    criar.add_argument("senha_operador")
    criar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    criar.add_argument("nome")
    criar.add_argument("email")
    criar.add_argument("senha")
    criar.add_argument("--especialidade")
    criar.add_argument("--crm")
    criar.add_argument("--cpf")
    criar.set_defaults(func=criar_usuario)

    # ---- Editar ----
    editar = subparsers.add_parser("editar")
    editar.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    editar.add_argument("email_operador")
    editar.add_argument("senha_operador")
    editar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    editar.add_argument("email")
    editar.add_argument("--novo-nome")
    editar.add_argument("--nova-senha")
    editar.add_argument("--nova-especialidade")
    editar.set_defaults(func=editar_usuario)

    # ---- Excluir ----
    excluir = subparsers.add_parser("excluir")
    excluir.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    excluir.add_argument("email_operador")
    excluir.add_argument("senha_operador")
    excluir.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    excluir.add_argument("email")
    excluir.set_defaults(func=excluir_usuario)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
