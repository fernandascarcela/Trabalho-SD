import argparse
import requests
import sys
from scripts.utils.validacoes import verificar_credenciais, data_valida, horario_valido, eh_int


def criar_atendimento(args):
    # ---- Permissões ----
    if args.perfil_operador not in ["medico", "admin"]:
        print(f"\nERRO: Como {args.perfil_operador}, você não tem permissão para criar atendimentos.")
        return
    
    # ---- Validação de credenciais ----
    if not verificar_credenciais(args):
        return

    # ---- Admin precisa informar o médico ----
    if args.perfil_operador == "admin" and not args.email_medico:
        print("ERRO: Admin deve informar o email do médico responsável pelo atendimento.")
        return

    # ---- Validação de data e horário ----
    if not data_valida(args.data):
        print("ERRO: Formato de data inválida.")
        return

    if not horario_valido(args.horario):
        print("ERRO: Formato de horário inválido.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "email_medico": args.email_medico,
        "data": args.data,
        "horario": args.horario,
        
    }

    endpoint = "admin" if args.perfil_operador == "admin" else "medico"

    try:
        resp = requests.post(
            f"http://localhost:5002/{endpoint}/atendimentos/criar",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def excluir_atendimento(args):
    if args.perfil_operador != "medico" and args.perfil_operador != "admin":
        print(f"\nERRO: Como {args.perfil_operador}, você nao tem permissao para excluir atendimentos.")
        return
    
    # ---- Validação de credenciais ----
    if not verificar_credenciais(args):
        return
    
    # ---- Validação de ID do atendimento ----
    if not eh_int(args.id_atendimento):
        print("ERRO: ID do atendimento inválido.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "id_atendimento": args.id_atendimento,  
    }

    endpoint = "admin" if args.perfil_operador == "admin" else "medico"

    try:
        resp = requests.post(
            f"http://localhost:5002/{endpoint}/atendimentos/excluir",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def listar_atendimentos(args):
    payload = {
        "medico": args.medico,
        "especialidade": args.especialidade,
    }
    if args.medico:
        payload["medico"] = args.medico
    if args.especialidade:
        payload["especialidade"] = args.especialidade
    
    try:
        resp = requests.post(
            f"http://localhost:5002/atendimentos/listar",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor (LISTA DE ATENDIMENTOS):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")


def editar_atendimento(args):
    if args.perfil_operador != "medico" and args.perfil_operador != "admin":
        print(f"\nERRO: Como {args.perfil_operador}, você nao tem permissao para editar atendimentos.")
        return
    
    # ---- Validação de credenciais ----
    if not verificar_credenciais(args):
        return
    
    # ---- Validação de ID do atendimento ----
    if not eh_int(args.id_atendimento):
        print("ERRO: ID do atendimento inválido.")
        return
    
    # ---- Validação de data e horário atendimento ----
    if args.data and not data_valida(args.data):
        print("ERRO: Formato de data inválida.")
        return

    if args.horario and not horario_valido(args.horario):
        print("ERRO: Formato de horário inválido.")
        return
        
    # ---- Preparar payload ----
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "id_atendimento": args.id_atendimento,  
    }
    if args.data:
        payload["data"] = args.data
    if args.horario:
        payload["horario"] = args.horario


    endpoint = "admin" if args.perfil_operador == "admin" else "medico"
    try:
        resp = requests.post(
            f"http://localhost:5002/{endpoint}/atendimentos/editar",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")

def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestao de Atendimentos Medicos")
    subparsers = parser.add_subparsers(dest="comando")

    # ---- Criar Atendimento ----
    criar = subparsers.add_parser("criar")
    criar.add_argument("perfil_operador", choices=["admin", "medico"])
    criar.add_argument("email_operador")
    criar.add_argument("senha_operador")
    criar.add_argument("--email_medico", required=False)
    criar.add_argument("data")
    criar.add_argument("horario")
    criar.set_defaults(func=criar_atendimento)

    # ---- Listar ----
    listar = subparsers.add_parser("listar")
    listar.add_argument("medico", nargs="?", default=None)
    listar.add_argument("especialidade", nargs="?", default=None)
    listar.set_defaults(func=listar_atendimentos)
    
    # ---- Editar ----
    editar = subparsers.add_parser("editar")
    editar.add_argument("perfil_operador", choices=["admin", "medico"])
    editar.add_argument("email_operador")
    editar.add_argument("senha_operador")
    editar.add_argument("id_atendimento")
    editar.add_argument("data", nargs="?", default=None)
    editar.add_argument("horario", nargs="?", default=None)
    editar.set_defaults(func=editar_atendimento)

    # ---- Excluir ----
    excluir = subparsers.add_parser("excluir")
    excluir.add_argument("perfil_operador", choices=["admin", "medico"])
    excluir.add_argument("email_operador")
    excluir.add_argument("senha_operador")
    excluir.add_argument("id_atendimento")
    excluir.set_defaults(func=excluir_atendimento)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
