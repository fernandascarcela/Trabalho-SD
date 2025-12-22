import argparse
import requests
import sys

BASE_URL = "http://localhost:5001/paciente/consultas"

# -----------------------CONSULTAS-----------------------
def agendar_consulta(args):
    payload = {
        "email_paciente": args.email,
        "senha_paciente": args.senha,
        "ID_consulta": args.ID_consulta
    }
    resp = requests.post(f"{BASE_URL}/agendar", json=payload)
    print(resp.json())

def cancelar_consulta(args):
    payload = {
        "email_paciente": args.email,
        "senha_paciente": args.senha,
        "ID_consulta": args.ID_consulta
    }
    resp = requests.post(f"{BASE_URL}/cancelar", json=payload)
    print(resp.json())

def listar_consultas(args):
    payload = {
        "email_paciente": args.email,
        "senha_paciente": args.senha
    }

    if args.medico:
        payload["medico"] = args.medico

    if args.dia:
        payload["dia"] = args.dia

    if args.status:
        payload["status"] = args.status

    resp = requests.get(f"{BASE_URL}/listar", json=payload)
    print(resp.json())



def main():
    parser = argparse.ArgumentParser(description="Gerenciamento de pacientes")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- agendar ----
    agendar = subparsers.add_parser("agendar", help="Agendar consulta")
    agendar.add_argument("email")
    agendar.add_argument("senha")
    agendar.add_argument("ID_consulta")
    agendar.set_defaults(func=agendar_consulta)

    # ---- cancelar ----
    cancelar = subparsers.add_parser("cancelar", help="Cancelar consulta")
    cancelar.add_argument("email")
    cancelar.add_argument("senha")
    cancelar.add_argument("ID_consulta")
    cancelar.set_defaults(func=cancelar_consulta)

    # ---- listar ----
    listar = subparsers.add_parser("listar", help="Listar consultas")
    listar.add_argument("email")
    listar.add_argument("senha")
    listar.add_argument("--medico", required=False, help="Filtrar por médico")
    listar.add_argument("--dia", required=False, help="Filtrar por dia (YYYY-MM-DD)")
    listar.add_argument("--status", required=False, help="Filtrar por status")
    listar.set_defaults(func=listar_consultas)


    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
