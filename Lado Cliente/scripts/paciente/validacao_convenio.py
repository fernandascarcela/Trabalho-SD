import argparse
import requests
import sys

def validar(args):
    perfis_permitidos = ["admin", "paciente", "recepcionista"]
    
    if args.perfil_operador not in perfis_permitidos:
        print(
            f"\nERRO: Como {args.perfil_operador}, "
            "Voce nao tem permissao para cadastrar convenio."
        )
        print("Tentativa de cadastro negada localmente.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "cpf_titular_convenio": args.cpf_titular_convenio,
        "numero_carteirinha": args.numero_carteirinha,
        "data_de_validade": args.data_de_validade,
    }

    try:
        resp = requests.post(
            f"http://interface_validation:5003/convenio/validacao",
            json=payload
        )
        print(f"\n>>> Resposta do Servidor: ")
        print(resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")

    except Exception as e:
        print(f"\nERRO: Falha de comunicação com o serviço de validação: {e}")
   

def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Gestão de Convênio"
    )
    subparsers = parser.add_subparsers(dest="comando")

    # ---------- VALIDAR ----------
    validar_parser = subparsers.add_parser("validar", help="Validar convenio")

    # Dados do operador
    validar_parser.add_argument("perfil_operador", choices=["admin", "recepcionista", "paciente"], help="Perfil do operador")
    validar_parser.add_argument("email_operador", help="E-mail do operador")
    validar_parser.add_argument("senha_operador", help="Senha do operador")
    validar_parser.add_argument( "cpf_titular_convenio", help="CPF do titular do convênio")
    validar_parser.add_argument( "numero_carteirinha",  help="Número da carteirinha")
    validar_parser.add_argument("data_de_validade", help="Data de validade do convênio")
    validar_parser.set_defaults(func=validar)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()