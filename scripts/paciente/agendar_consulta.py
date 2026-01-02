import argparse
import requests
import sys
from utils.validacoes import verificar_credenciais, eh_int

def agendar_consulta(args):
    # ---- Permissões ----
    if args.perfil_operador == "medico":
        print("ERRO: Médico não pode agendar consultas.")
        return

    # ---- Credenciais ----
    if not verificar_credenciais(args):
        return
    
    if not eh_int(args.id_consulta):
        print("ERRO: id_consulta deve ser um número inteiro.")
        return

    # ---- Perfil admin / recepcionista ----
    if args.perfil_operador in ["admin", "recepcionista"]:
        if not args.email_paciente:
            print("ERRO: email_paciente é obrigatório para admin/recepcionista.")
            return

    # ---- Perfil paciente ----
    if args.perfil_operador == "paciente":
        args.email_paciente = args.email_operador

    # ---- Forma de pagamento ----
    if args.forma_pagamento == "cartao":
        if not args.numero_cartao or not args.data_validade:
            print("ERRO: Cartão exige número e data de validade.")
            return

    elif args.forma_pagamento == "convenio":
        if not args.titular_convenio or not args.numero_convenio:
            print("ERRO: Convênio exige titular e número.")
            return

    # ---- Payload ----
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "email_paciente": args.email_paciente,
        "id_consulta": args.id_consulta,
        "forma_pagamento": args.forma_pagamento
    }

    if args.forma_pagamento == "cartao":
        payload.update({
            "numero_cartao": args.numero_cartao,
            "data_validade": args.data_validade
        })

    if args.forma_pagamento == "convenio":
        payload.update({
            "cpf_titular_convenio": args.cpf_titular_convenio,
            "data_validade_convenio": args.data_validade_convenio,
            "numero_convenio": args.numero_convenio
        })

    try:
        resp = requests.post(
            "http://localhost:5001/agendamentos/agendar",
            json=payload,
            timeout=5
        )
        print("\n>>> Resposta do servidor:")
        print(resp.json())

    except Exception as e:
        print(f"Erro de conexão: {e}")



def main():
    parser = argparse.ArgumentParser(description="Sistema de Gestao de Agendamento")
    subparsers = parser.add_subparsers(dest="comando")

    agendar = subparsers.add_parser("agendar")
    agendar.add_argument("perfil_operador", choices=["admin", "paciente", "recepcionista"])
    agendar.add_argument("email_operador")
    agendar.add_argument("senha_operador")
    agendar.add_argument("id_consulta", type=int)
    agendar.add_argument("forma_pagamento", choices=["cartao", "convenio"])

    # opcionais (validados depois)
    agendar.add_argument("--email_paciente", default=None)
    agendar.add_argument("--numero_cartao", default=None)
    agendar.add_argument("--data_validade", default=None)
    agendar.add_argument("--cpf_titular_convenio")
    agendar.add_argument("--data_validade_convenio", default=None)
    agendar.add_argument("--numero_convenio", default=None)

    agendar.set_defaults(func=agendar_consulta)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()


