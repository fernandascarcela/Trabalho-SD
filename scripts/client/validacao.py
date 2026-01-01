import argparse
import requests
import sys


def validar(args):
    perfis_permitidos = ["admin", "recepcionista"]

    if args.perfil_operador not in perfis_permitidos:
        print(
            f"\nERRO: Como {args.perfil_operador}, "
            "voce nao tem permissao para validar pagamento ou convenio."
        )
        print("Tentativa de validacao negada localmente.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "tipo_pagamento": args.tipo_pagamento
    }

    # ---------- VALIDAÇÃO POR TIPO DE PAGAMENTO ----------
    if args.tipo_pagamento == "cartao":
        obrigatorios = ["bandeira", "tipo_cartao", "ultimos_digitos", "valor"]

        for campo in obrigatorios:
            if not getattr(args, campo, None):
                print(f"\nERRO: Campo obrigatório ausente para cartão: {campo}")
                return

        payload.update({
            "bandeira": args.bandeira,
            "tipo_cartao": args.tipo_cartao,       # credito ou debito
            "ultimos_digitos": args.ultimos_digitos,
            "valor": args.valor
        })

        endpoint = "cartao"

    elif args.tipo_pagamento == "convenio":
        obrigatorios = ["codigo_convenio", "numero_carteirinha", "titular"]

        for campo in obrigatorios:
            if not getattr(args, campo, None):
                print(f"\nERRO: Campo obrigatório ausente para convênio: {campo}")
                return

        payload.update({
            "codigo_convenio": args.codigo_convenio,
            "numero_carteirinha": args.numero_carteirinha,
            "titular": args.titular
        })

        endpoint = "convenio"

    else:
        print("\nERRO: Tipo de pagamento inválido. Use 'cartao' ou 'convenio'.")
        return

    # ---------- CHAMADA AO SERVIÇO ----------
    try:
        resp = requests.post(
            f"http://localhost:5001/validar/{endpoint}",
            json=payload,
            timeout=5
        )

        print(f"\n>>> Resposta do Servidor:")
        print(resp.json())

    except Exception as e:
        print(f"\nERRO: Falha de comunicação com o serviço de validação: {e}")
   

def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Gestão de Validação de Pagamento e Convênio"
    )
    subparsers = parser.add_subparsers(dest="comando")

    # ---------- VALIDAR ----------
    validar_parser = subparsers.add_parser(
        "validar",
        help="Validar pagamento por cartão ou convênio"
    )

    # Dados do operador
    validar_parser.add_argument(
        "perfil_operador",
        choices=["admin", "recepcionista", "paciente"],
        help="Perfil do operador"
    )
    validar_parser.add_argument(
        "email_operador",
        help="E-mail do operador"
    )
    validar_parser.add_argument(
        "senha_operador",
        help="Senha do operador"
    )

    # Tipo de pagamento
    validar_parser.add_argument(
        "tipo_pagamento",
        choices=["cartao", "convenio"],
        help="Tipo de pagamento"
    )

    # ---------- CAMPOS PARA CARTÃO ----------
    validar_parser.add_argument(
        "--bandeira",
        help="Bandeira do cartão (ex: Visa, Master)"
    )
    validar_parser.add_argument(
        "--tipo_cartao",
        choices=["credito", "debito"],
        help="Tipo do cartão"
    )
    validar_parser.add_argument(
        "--ultimos_digitos",
        help="Últimos 4 dígitos do cartão"
    )
    validar_parser.add_argument(
        "--valor",
        type=float,
        help="Valor da consulta"
    )

    # ---------- CAMPOS PARA CONVÊNIO ----------
    validar_parser.add_argument(
        "--codigo_convenio",
        help="Código do convênio"
    )
    validar_parser.add_argument(
        "--numero_carteirinha",
        help="Número da carteirinha"
    )
    validar_parser.add_argument(
        "--titular",
        help="Nome do titular do convênio"
    )

    validar_parser.set_defaults(func=validar)

    # ---------- EXECUÇÃO ----------
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
