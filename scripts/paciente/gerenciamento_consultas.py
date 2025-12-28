import argparse
import requests
import sys


# -----------------------CONTA-----------------------
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


def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestão de Usuários")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- Comando Registrar ----
    criar = subparsers.add_parser("registrar")
    
    # 1. Identificação de quem está OPERANDO o comando
    criar.add_argument("perfil_operador", choices=["admin", "recepcionista"], help="Seu cargo")
    criar.add_argument("email_operador", help="Seu e-mail de login")
    criar.add_argument("senha_operador", help="Sua senha")

    # 2. Dados de quem será CRIADO
    criar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"], help="Cargo do novo usuário")
    criar.add_argument("nome")
    criar.add_argument("email")
    criar.add_argument("senha")
    criar.add_argument("--especialidade", required=False)

    criar.set_defaults(func=criar_usuario)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
