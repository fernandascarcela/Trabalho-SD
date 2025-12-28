import argparse
import requests
import sys


def criar_usuario(args):
    if args.perfil_operador == "recepcionista" and args.role != "paciente":
        print(f"\nERRO: Como {args.perfil_operador}, você só tem permissão para criar 'paciente'.")
        print(f"Tentativa de criar '{args.role}' negada localmente.")
        return

    payload = { 
        "perfil_operador": args.perfil_operador, 
        "email_operador": args.email_operador, 
        "senha_operador": args.senha_operador,
        "role": args.role,
        "nome": args.nome,
        "email": args.email,
        "senha": args.senha
    }

    if args.role == "medico" and args.especialidade:
        payload["especialidade"] = args.especialidade

    endpoint = "admin" if args.perfil_operador == "admin" else "recepcionista"
    try:
        resp = requests.post(f"http://localhost:5001/{endpoint}/usuarios/registrar", json=payload)
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")



def editar_usuario(args):
    if args.perfil_operador == "recepcionista" and args.role != "paciente":
        print(f"\nERRO: Como {args.perfil_operador}, você só tem permissão para editar dados de 'paciente'.")
        print(f"Tentativa de editar dados de '{args.role}' negada localmente.")
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
        resp = requests.post(f"http://localhost:5001/{endpoint}/usuarios/editar", json=payload)
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")

def excluir_usuario(args):
    if args.perfil_operador == "recepcionista" and args.role != "paciente":
        print(f"\nERRO: Como {args.perfil_operador}, você só tem permissão para excluir 'paciente'.")
        print(f"Tentativa de excluir '{args.role}' negada localmente.")
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
        resp = requests.post(f"http://localhost:5001/{endpoint}/usuarios/excluir", json=payload)
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")

def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestão de Usuários")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- Registrar ----
    criar = subparsers.add_parser("registrar")
    criar.add_argument("perfil_operador", choices=["admin", "recepcionista"], help="Seu cargo")
    criar.add_argument("email_operador", help="Seu e-mail de login")
    criar.add_argument("senha_operador", help="Sua senha")
    criar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"], help="Cargo do novo usuário")
    criar.add_argument("nome")
    criar.add_argument("email")
    criar.add_argument("senha")
    criar.add_argument("--especialidade", required=False)
    criar.set_defaults(func=criar_usuario)

    # ---- Editar ----
    editar = subparsers.add_parser("editar", help="Edita um usuário existente")
    editar.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    editar.add_argument("email_operador")
    editar.add_argument("senha_operador")
    editar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    editar.add_argument("email", help="E-mail do usuário a ser editado")
    editar.add_argument("--novo-nome", help="Novo nome do usuário")
    editar.add_argument("--nova-senha", help="Nova senha do usuário")
    editar.add_argument("--nova-especialidade", help="Nova especialidade (se médico)")
    editar.set_defaults(func=editar_usuario)

    # ---- Excluir ----
    excluir = subparsers.add_parser("excluir", help="Exclui um usuário existente")
    excluir.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    excluir.add_argument("email_operador")
    excluir.add_argument("senha_operador")
    excluir.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    excluir.add_argument("email", help="E-mail do usuário a ser excluído")
    excluir.set_defaults(func=excluir_usuario)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
