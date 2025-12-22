import argparse
import requests
import sys

BASE_URL = "http://localhost:5001/paciente"


# -----------------------CONTA-----------------------
def criar_paciente(args):
    payload = {
        "nome_paciente": args.nome,
        "email_paciente": args.email,
        "senha_paciente": args.senha
    }

    resp = requests.post(f"{BASE_URL}/registrar", json=payload)
    print(resp.json())


def editar_paciente(args):
    payload = {
        "email_paciente": args.email,
        "senha_paciente": args.senha
    }

    if args.novo_nome:
        payload["novo_nome"] = args.novo_nome

    if args.novo_email:
        payload["novo_email"] = args.novo_email

    if args.nova_senha:
        payload["nova_senha"] = args.nova_senha

    resp = requests.put(f"{BASE_URL}/editar/{args.id}", json=payload)
    print(resp.json())


def excluir_paciente(args):
    payload = {
        "email_paciente": args.email,
        "senha_paciente": args.senha
    }
    resp = requests.delete(f"{BASE_URL}/excluir/{args.id}", json=payload)
    print(resp.json())

def main():
    parser = argparse.ArgumentParser(description="Gerenciamento de pacientes")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- criar ----
    criar = subparsers.add_parser("registrar", help="Criar conta paciente")
    criar.add_argument("nome")
    criar.add_argument("email")
    criar.add_argument("senha")
    criar.set_defaults(func=criar_paciente)

    # ---- editar ----
    editar = subparsers.add_parser("editar", help="Editar dados paciente")
    editar.add_argument("id")
    editar.add_argument("email")
    editar.add_argument("senha")
    editar.add_argument("--novo-nome", required=False)
    editar.add_argument("--novo-email", required=False)
    editar.add_argument("--nova-senha", required=False)
    editar.set_defaults(func=editar_paciente)


    # ---- excluir ----
    excluir = subparsers.add_parser("excluir", help="Excluir conta paciente")
    excluir.add_argument("id")
    excluir.set_defaults(func=excluir_paciente)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
