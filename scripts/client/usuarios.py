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
    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida.")
        return
    
    auto_edicao = False

    if not args.email:
        auto_edicao = True
    else:
        if args.email == args.email_operador:
            auto_edicao = True

        usuario_email = args.email

    # ---------- REGRAS DE PERMISSÃO ----------
    if auto_edicao:
        # Quem pode autoeditar
        if args.perfil_operador in ["recepcionista"]:
            print("ERRO: Recepcionista não pode se autoeditar.")
            return
        
        if args.role:
            if args.role not in ["paciente", "medico", "recepcionista", "admin"]:
                print("ERRO: Role inválida.")
                return
        # Paciente, médico e admin podem autoeditar a si mesmos
    else:
        if args.perfil_operador == "recepcionista" and args.role not in ["paciente", "medico"]:
            print(
                f"\nERRO: Como {args.perfil_operador}, você só pode editar paciente ou médico."
            )
            return

        if args.perfil_operador in ["paciente", "medico"]:
            print(
                f"\nERRO: Você só pode se autoeditar."
            )
            return

        if not args.role:
            print("ERRO: Role do usuário a ser editado é obrigatória.")
            return

        if not args.email:
            print("ERRO: Email do usuário a ser editado é obrigatória.")
            return

        if not email_valido(usuario_email):
            print("ERRO: E-mail do usuário a ser editado inválido.")
            return

    # ---------- NOVO E-MAIL ----------
    if args.novo_email:
        if not email_valido(args.novo_email):
            print("ERRO: Novo e-mail inválido.")
            return

    # ---------- NOVA SENHA ----------
    if args.nova_senha:
        if not senha_valida(args.nova_senha):
            print("ERRO: Nova senha inválida (mín. 6 caracteres).")
            return

    # ---------- REGRAS ESPECÍFICAS PARA MÉDICO ----------
    role_final = args.role if args.role else args.perfil_operador

    if role_final == "medico":
        if args.nova_especialidade and not args.nova_especialidade.strip():
            print("ERRO: Especialidade inválida.")
            return

        if args.crm and not crm_valido(args.crm):
            print("ERRO: CRM inválido.")
            return

    # ---------- PAYLOAD ----------
    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
    }

    if not auto_edicao:
        payload["email"] = usuario_email
        payload["role"] = args.role

    if args.novo_nome:
        payload["nome"] = args.novo_nome

    if args.novo_email:
        payload["novo_email"] = args.novo_email

    if args.nova_senha:
        payload["senha"] = args.nova_senha

    if role_final == "medico":
        if args.nova_especialidade:
            payload["especialidade"] = args.nova_especialidade
        if args.crm:
            payload["crm"] = args.crm

    if role_final == "paciente" and args.cpf:
        if not cpf_valido(args.cpf):
            print("ERRO: CPF inválido.")
            return
        payload["cpf"] = args.cpf

    # ---------- ENDPOINT ----------
    endpoint = args.perfil_operador 

    # ---------- CHAMADA AO SERVIÇO ----------
    try:
        resp = requests.post(
            f"http://localhost:5001/{endpoint}/usuarios/editar",
            json=payload,
            timeout=5
        )
        print(payload)

        print(f"\n>>> Resposta do Servidor ({args.perfil_operador.upper()}):")
        print(resp.json())

    except Exception as e:
        print(f"\nERRO: Falha de conexão: {e}")

def excluir_usuario(args):

    if args.perfil_operador == "recepcionista" and args.role not in ["paciente", "medico"]:
        print(f"\nERRO: Como {args.perfil_operador}, você só pode excluir 'paciente' ou 'medico'.")
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

def listar_usuarios(args):
    if not email_valido(args.email_operador):
        print("ERRO: E-mail do operador inválido.")
        return

    if not senha_valida(args.senha_operador):
        print("ERRO: Senha do operador inválida.")
        return

    payload = {
        "perfil_operador": args.perfil_operador,
        "email_operador": args.email_operador,
        "senha_operador": args.senha_operador,
        "role": args.role,
    }

    try:
        resp = requests.post(
            f"http://localhost:5001/admin/usuarios/listar",
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
    editar.add_argument("perfil_operador", choices=["admin", "recepcionista","paciente","medico"])
    editar.add_argument("email_operador")
    editar.add_argument("senha_operador")
    editar.add_argument("role", nargs="?", choices=["paciente", "medico", "recepcionista", "admin"])
    editar.add_argument("email",nargs="?", default=None)
    
    editar.add_argument("--novo-nome")
    editar.add_argument("--novo-email")
    editar.add_argument("--nova-senha")
    editar.add_argument("--nova-especialidade")
    editar.add_argument("--crm")
    editar.add_argument("--cpf")
    editar.set_defaults(func=editar_usuario)

    # ---- Listar ----
    listar = subparsers.add_parser("listar")
    listar.add_argument("perfil_operador", choices=["admin", "recepcionista"])
    listar.add_argument("email_operador")
    listar.add_argument("senha_operador")
    listar.add_argument("role", choices=["paciente", "medico", "recepcionista", "admin"])
    listar.set_defaults(func=listar_usuarios)

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
