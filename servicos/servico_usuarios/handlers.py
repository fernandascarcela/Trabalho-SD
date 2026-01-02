from database import (
    # Criar usuarios
    buscar_usuario_por_email,
    criar_paciente,
    criar_recepcionista,
    criar_medico,
    criar_admin,
    
    # Editar usuarios
    editar_paciente,
    editar_medico,
    editar_recepcionista_admin,

    #Excluir usuarios
    excluir_usuarios,

    # Listar usuarios
    listar_por_funcao
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
    elif acao == "listar_usuarios":
        return listar_usuarios(dados)
    elif acao == "excluir_usuario":
        return excluir_usuario(dados)
    else:
        return {"erro": "Ação desconhecida"}

# É basicamente o login do operador que está tentando fazer a ação
def validar_operador(email, senha, perfil):
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return False, "Usuário não existe"

    if usuario["password"] != senha:
        return False, "Senha inválida"

    if usuario["user_type"] != perfil.upper():
        return False, "Perfil não confere"

    return True, "Operador autenticado"

# É a validação do usuário alvo da ação, se ele existe e se a role bate
def validar_usuario(email, role):
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return False, "Usuário não existe"

    if usuario["user_type"] != role.upper():
        return False, "Perfil não confere"

    return True, "Role válida"

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

        return criar_recepcionista(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )

    elif usuario == "admin":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar outro admin"}

        return criar_admin(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"]
        )

    else:
        return {"erro": "Ação inválida"}

def editar_usuario(dados):
    perfil_operador = dados["perfil_operador"]
    email_operador = dados["email_operador"]
    senha_operador = dados["senha_operador"]

    valido, mensagem = validar_operador(email_operador, senha_operador, perfil_operador)
    if not valido:
        return {"erro": mensagem}

    usuario_alvo_email = dados.get("email", email_operador)
    auto_edicao = (usuario_alvo_email == email_operador)
    
    usuario_role_alvo = dados.get("role", perfil_operador) if auto_edicao else dados.get("role")

    # 3. Validação de Existência do Alvo (apenas se não for autoedição)
    if not auto_edicao:
        if not usuario_role_alvo:
            return {"erro": "A 'role' do usuário alvo é obrigatória para edição de terceiros"}
        valido, mensagem = validar_usuario(usuario_alvo_email, usuario_role_alvo)
        if not valido:
            return {"erro": mensagem}

    # 4. Verificação de Permissões (Regras de Negócio)
    if perfil_operador in ["paciente", "medico"] and not auto_edicao:
        return {"erro": "Você só pode editar a si mesmo"}

    if perfil_operador == "recepcionista":
        if auto_edicao:
            return {"erro": "Recepcionista não pode se autoeditar"}
        if usuario_role_alvo not in ["paciente", "medico"]:
            return {"erro": "Recepcionista só pode editar pacientes ou médicos"}

    # 5. Mapeamento de Funções e Campos
    # Criamos um dicionário para evitar repetição de IFs gigantes
    mapeamento = {
        "paciente":{
                "func": editar_paciente,
                "campos": ["nome", "senha", "cpf", "novo_email"]
            },
        "medico":{ 
                "func": editar_medico, 
                "campos": ["nome", "senha", "crm", "especialidade", "novo_email"]
            },
        "recepcionista": {
                "func": editar_recepcionista_admin, 
                "campos": ["nome", "senha", "novo_email"]
            },
        "admin": { 
                "func": editar_recepcionista_admin, 
                "campos": ["nome", "senha", "novo_email"]
            }
    }

    config = mapeamento.get(usuario_role_alvo)
    if not config:
        return {"erro": f"Role '{usuario_role_alvo}' inválida para edição"}

    # Extrai apenas os campos que existem nos dados e que são permitidos para aquela role
    payload_banco = {k: dados[k] for k in config["campos"] if k in dados}
    
    # Executa a função do banco de dados correspondente
    return config["func"](usuario_alvo_email, **payload_banco)

def listar_usuarios(dados):
    '''
        Lista todos os usuários do sistema
        Apenas admin pode listar usuários
    '''
    perfil = dados["perfil_operador"]

    valido, mensagem = validar_operador(
        dados["email_operador"],
        dados["senha_operador"],
        perfil
    )

    if not valido:
        return {"erro": mensagem}

    if perfil == "admin":
        return listar_por_funcao(
            role=dados["role"]
        )
    else:
        return {"erro": "Apenas admin pode listar usuários"}

def excluir_usuario(dados):
    '''
        Administrador pode excluir qualquer usuário
        Recepcionista só pode excluir pacientes e médicos
        Paciente não pode excluir usuários
        Médico não pode excluir usuários
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
    
    valido, mensagem =  validar_usuario(
        dados["email"],
        role=usuario
    )

    if not valido:
        return {"erro": mensagem}

    if usuario in ["paciente","medico"]:
        if perfil not in ["admin", "recepcionista"]:
            return {"erro": "Sem permissão para excluir este usuário"}

        return excluir_usuarios(
            email=dados["email"],
        )

    elif usuario == "recepcionista":
        if perfil != "admin":
            return {"erro": "Sem permissão para excluir este usuário"}

        return excluir_usuarios(
            email=dados["email"],
        )

    elif usuario == "admin":
        if perfil != "admin":
            return {"erro": "Apenas admin pode criar outro admin"}

        return excluir_usuarios(
            email=dados["email"],
        )

    else:
        return {"erro": "Ação inválida"}