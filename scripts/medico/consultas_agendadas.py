import argparse
import requests
import sys
from scripts.utils.validacoes import verificar_credenciais, data_valida, eh_int


def listar_consultas(args):
    if args.perfil_operador == "paciente" :
        print(f"\nERRO: Como {args.perfil_operador}, você nao tem permissao para listar consultas do medico.")
        return
    
    # ---- Validação de credenciais ----
    if not verificar_credenciais(args):
        return
    
    # ---- Validação de email do médico ----
    if not args.email_medico:
        print("ERRO: Email do médico é necessário.")
        return
    
    # ---- Validação de data ----
    if args.data and not data_valida(args.data):
        print("ERRO: Data inválida. Formato: DD-MM-AAAA")
        return
    
    # ---- Validação de status ----
    if args.status and args.status not in ["confirmado", "concluido", "cancelado", "pendente"]:
        print("ERRO: Status inválido.")
        return
    
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "email_medico": args.email_medico,
        "data": args.data,
        "status": args.status,
    }

    endpoint = "admin" if args.perfil_operador == "admin" else "medico"
    
    try:
        resp = requests.post(
            f"http://localhost:5002/{endpoint}/consultas/agendadas",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")
    

def atualizar_status_consulta(args):
    if args.perfil_operador != "medico" and args.perfil_operador != "admin":
        print(f"\nERRO: Como {args.perfil_operador}, você nao tem permissao para atualizar atendimentos.")
        return
    
    # ---- Validação de credenciais ----
    if not verificar_credenciais(args):
        return
    
    # ---- Validação de ID do atendimento ----
    if not eh_int(args.id_consulta):
        print("ERRO: ID do atendimento inválido.")
        return
    
    # ---- Validação de status ----
    if args.status not in ["confirmado", "concluido", "cancelado"]:
        print("ERRO: Status inválido.")
        return
    
    # ---- Preparar payload ----
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "id_consulta": args.id_consulta,  
        "status": args.status,
    }

    endpoint = "admin" if args.perfil_operador == "admin" else "medico"
    try:
        resp = requests.post(
            f"http://localhost:5002/{endpoint}/consulta/status",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestao de Consultas Medicos")
    subparsers = parser.add_subparsers(dest="comando")


    # ---- Listar Consultas ----
    listar = subparsers.add_parser("listar")
    listar.add_argument("perfil_operador", choices=["admin", "medico", "recepcionista"])
    listar.add_argument("email_operador")
    listar.add_argument("senha_operador")
    listar.add_argument("email_medico")
    listar.add_argument("data", help="Formato: DD-MM-AAAA", nargs="?", default=None)
    listar.add_argument("status", nargs="?", default=None, choices=["confirmado", "concluido", "cancelado", "pendente"])
    listar.set_defaults(func=listar_consultas)

        # ---- Atualizar Status Consulta ----
    atualizar = subparsers.add_parser("atualizar")
    atualizar.add_argument("perfil_operador", choices=["admin", "medico"])
    atualizar.add_argument("email_operador")
    atualizar.add_argument("senha_operador")
    atualizar.add_argument("id_consulta")
    atualizar.add_argument("status", choices=["confirmado", "concluido", "cancelado"])
    atualizar.set_defaults(func=atualizar_status_consulta)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()


