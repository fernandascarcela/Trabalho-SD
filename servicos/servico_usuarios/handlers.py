from werkzeug.security import check_password_hash

from database import (
    # Criar usuarios
    buscar_usuario_por_email,
    criar_paciente,
    criar_recepcionista,
    criar_medico,
    criar_admin,
    
    # Editar usuarios
)


def tratar_acao(acao, dados):
    """
    Recebe a ação enviada pelo main.py e decide
    qual função de negócio deve ser executada.
    
    """

    if acao == "registrar_usuario":
        return criar_usuario(dados)
    elif acao == "editar_usuario":
        return editar_usuario(dados)
    else:
        return {
            "erro": "Ação desconhecida"
        }

def validar_operador(email, senha, perfil):
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return False, "Usuário não existe"

    if usuario["password"] != senha:
        return False, "Senha inválida"

    if usuario["user_type"] != perfil.upper():
        return False, "Perfil não confere"

    return True, "Operador autenticado"

def criar_usuario(dados):
    '''
        Administrador pode criar qualquer usuário
        Recepcionista só pode criar pacientes e médicos
        Paciente não pode criar usuários
        Médico não pode criar usuários
    '''

    perfil = dados["perfil_operador"]
    usuario = dados["role"]

    valido, mensagem = validar_operador(
        dados["email_operador"],
        dados["senha_operador"],
        perfil
    )

    if not valido:
        return {"erro": mensagem}

    if usuario == "paciente":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar paciente"}

        return criar_paciente(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            cpf=dados["cpf"]
        )


    elif usuario == "medico":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar médico"}

        return criar_medico(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            crm=dados["crm"],
            especialidade=dados["especialidade"].upper()
        )


    elif usuario == "recepcionista":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar recepcionista"}

        criar_recepcionista(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )

        return {"sucesso": "Recepcionista criado com sucesso"}

    elif usuario == "admin":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar outro admin"}

        criar_admin(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )
        return {"sucesso": "Admin criado com sucesso"}

    else:
        return {"erro": "Ação inválida"}

def editar_usuario(dados):
    perfil = dados["perfil_operador"]
    usuario = dados["role"]

    valido, mensagem = validar_operador(
        dados["email_operador"],
        dados["senha_operador"],
        perfil
    )

    if not valido:
        return {"erro": mensagem}

    if usuario == "paciente":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar paciente"}

        return criar_paciente(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            cpf=dados["cpf"]
        )


    elif usuario == "medico":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar médico"}

        return criar_medico(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            crm=dados["crm"],
            especialidade=dados["especialidade"].upper()
        )


    elif usuario == "recepcionista":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar recepcionista"}

        criar_recepcionista(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )

        return {"sucesso": "Recepcionista criado com sucesso"}

    elif usuario == "admin":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar outro admin"}

        criar_admin(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )
        return {"sucesso": "Admin criado com sucesso"}

    else:
        return {"erro": "Ação inválida"}


    perfil = dados["perfil_operador"]
    usuario = dados["role"]

    valido, mensagem = validar_operador(
        dados["email_operador"],
        dados["senha_operador"],
        perfil
    )

    if not valido:
        return {"erro": mensagem}

    if usuario == "paciente":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar paciente"}

        return criar_paciente(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            cpf=dados["cpf"]
        )


    elif usuario == "medico":
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para criar médico"}

        return criar_medico(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            crm=dados["crm"],
            especialidade=dados["especialidade"].upper()
        )


    elif usuario == "recepcionista":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar recepcionista"}

        criar_recepcionista(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )

        return {"sucesso": "Recepcionista criado com sucesso"}

    elif usuario == "admin":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar outro admin"}

        criar_admin(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )
        return {"sucesso": "Admin criado com sucesso"}

    else:
        return {"erro": "Ação inválida"}