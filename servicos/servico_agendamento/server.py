from xmlrpc.server import SimpleXMLRPCServer

from database import (
    admin_create_schedule,
    check_conflit_schedule,
    get_appointment_with_schedule,
    get_doctor_id_by_email,
    get_patient_id_by_user_id,
    insert_appointment,
    list_appointments_by_doctor,
    set_schedule_available,
    update_appointment_status,
    delete_schedule_by_id,
    doctor_create_schedule,
    edit_schedule,
    get_doctor_by_name,
    get_doctor_by_user_id,
    get_insurance_by_patient_id,
    get_list_of_schedules,
    get_patient_id_by_email,
    get_schedule_by_id,
    get_user,
    insert_schedule,
)
from utils.utils import (
    auth_operador, 
    map_status_cli_to_db,
    normalizar_data, 
    to_plain, 
    validar_cartao_data_validade
)


def ok(**k):
    return {"ok": True, **k}


def fail(msg, code=400):
    # XML-RPC não trabalha com status HTTP; devolvemos code no payload
    return {"ok": False, "erro": msg, "code": code}


# ------------------ RPC METHODS ------------------

def criar_atendimento(email_operador, senha_operador, email_medico, data, horario):
    # 1) autenticar operador
    operador = get_user(email_operador, senha_operador)
    if not operador:
        return fail("Credenciais inválidas", 401)

    if operador["user_type"] not in ("ADMIN", "MEDICO"):
        return fail("Perfil sem permissão (precisa ser ADMIN ou MEDICO)", 403)

    try:
        data = normalizar_data(data)
    except ValueError as e:
        return fail(str(e), 400)

    # 2) descobrir doctor_id e specialty
    if operador["user_type"] == "MEDICO":
        # médico cria para si mesmo
        doc = doctor_create_schedule(operador)
        if not doc:
            return fail(
                "Operador é MEDICO, mas não existe registro na tabela doctor",
                404,
            )
    else:
        # admin cria para outro médico via email_medico
        if not email_medico:
            return fail("ADMIN precisa informar email_medico", 400)

        doc = admin_create_schedule(email_medico)
        if not doc:
            return fail("Médico não encontrado para o email informado", 404)

    doctor_id = doc["doctor_id"]
    specialty = doc["specialty"]

    # 3) impedir duplicar horário (mesmo médico, mesma data e hora)
    if check_conflit_schedule(doctor_id, data, horario):
        return fail(
            "Já existe um atendimento cadastrado para esse médico nessa data e horário",
            409,
        )

    # 4) criar schedule
    novo = insert_schedule(doctor_id, data, horario, specialty)
    return to_plain(
        ok(
            mensagem="Horário de atendimento criado com sucesso",
            schedule=novo,
            code=201,
        )
    )


def listar_atendimentos(medico=None, especialidade=None):
    doc = None
    doctor_id = None

    # Se algum filtro de médico foi informado, tenta resolver doctor_id
    if medico or especialidade:
        doc = get_doctor_by_name(medico, especialidade)
        if not doc:
            return fail("Atendimentos não encontrados", 404)
        doctor_id = doc["doctor_id"]

    list_of_schedules = get_list_of_schedules(doctor_id, especialidade)

    if not list_of_schedules:
        return to_plain(
            ok(
                mensagem="Nenhum horário de atendimento encontrado",
                schedules=[],
                code=200,
            )
        )

    return to_plain(
        ok(
            mensagem="Lista de horários encontrada com sucesso",
            schedules=list_of_schedules,
            code=200,
        )
    )

def excluir_atendimento(email_operador, senha_operador, id_atendimento):
    operador = get_user(email_operador, senha_operador)
    if not operador:
        return fail("Credenciais inválidas", 401)

    if operador["user_type"] not in ("ADMIN", "MEDICO"):
        return fail("Perfil sem permissão (precisa ser ADMIN ou MEDICO)", 403)

    schedule = get_schedule_by_id(id_atendimento)
    if not schedule:
        return fail("Atendimento não encontrado.", 404)

    # Se MEDICO, só pode excluir horários dele
    if operador["user_type"] == "MEDICO":
        doctor = get_doctor_by_user_id(operador["user_id"])

        if doctor["doctor_id"] != schedule["doctor_id"]:
            return fail("O médico não tem permissão para excluir este horário.", 403)

    # Só pode excluir se ainda estiver disponível
    if not schedule["is_available"]:
        return fail(
            "O atendimento já foi agendado. Cancele o agendamento para poder excluí-lo.",
            409,
        )

    deleted = delete_schedule_by_id(id_atendimento)

    if not deleted:
        return fail("Horário não encontrado", 404)

    # deleted deve retornar algo como {"schedule_id": ...}
    deleted_id = deleted.get("schedule_id") if isinstance(deleted, dict) else deleted

    return ok(
        mensagem=f"Horário de atendimento de id {deleted_id} deletado com sucesso!",
        code=200,
    )

def editar_atendimento(email_operador, senha_operador, id_atendimento, data, horario):
    # 1) autenticar operador
    operador = get_user(email_operador, senha_operador)
    if not operador:
        return fail("Credenciais inválidas", 401)

    if operador["user_type"] not in ("ADMIN", "MEDICO"):
        return fail("Perfil sem permissão (precisa ser ADMIN ou MEDICO)", 403)

    try:
        data = normalizar_data(data)
    except ValueError as e:
        return fail(str(e), 400)

    schedule = get_schedule_by_id(id_atendimento)
    if not schedule:
        return fail("Atendimento não encontrado.", 404)

    # Se MEDICO, só pode editar horários dele
    if operador["user_type"] == "MEDICO":
        doctor = get_doctor_by_user_id(operador["user_id"])
        if not doctor:
            return fail("Registro de médico não encontrado.", 404)

        if doctor["doctor_id"] != schedule["doctor_id"]:
            return fail("O médico não tem permissão para editar este horário.", 403)

    # Só pode editar se ainda estiver disponível
    if not schedule["is_available"]:
        return fail(
            "O atendimento já foi agendado. Cancele o agendamento para poder editá-lo.",
            409,
        )


    if check_conflit_schedule(schedule["doctor_id"], data, horario):
        return fail(
            "Já existe um horário cadastrado para esse médico nessa data e horário",
            409,
        )

    edited_schedule = edit_schedule(id_atendimento, data, horario)
    return to_plain(
        ok(
            mensagem="Horário de atendimento editado com sucesso.",
            schedule=edited_schedule,
            code=200,
        )
    )




# ------------------ CASO 1: LISTAR CONSULTAS AGENDADAS ------------------

def consultas_agendadas(email_operador, senha_operador, email_medico, data=None, status=None):
    # autenticar (qualquer user válido pode acessar, mas você pode restringir aqui)
    u = auth_operador(email_operador, senha_operador)
    if not u:
        return fail("Credenciais inválidas", 401)

    doctor_id = get_doctor_id_by_email(email_medico)
    if not doctor_id:
        return fail("Médico não encontrado", 404)

    try:
        data = normalizar_data(data) if data else None
        status_db = map_status_cli_to_db(status) if status else None
    except ValueError as e:
        return fail(str(e), 400)

    consultas = list_appointments_by_doctor(doctor_id, date=data, status_db=status_db)

    if not consultas:
        return to_plain(ok(mensagem="Nenhuma consulta encontrada", code=200))

    return to_plain(ok(mensagem="Consultas encontradas", consultas=consultas, code=200))


# ------------------ CASO 2: AGENDAR CONSULTA (criar appointment) ------------------

def agendar_consulta(
    perfil_operador,
    email_operador,
    senha_operador,
    id_atendimento,
    forma_pagamento,
    email_paciente=None,
    numero_cartao=None,
    data_validade=None,
):
    # autenticar operador e checar perfil
    u = auth_operador(email_operador, senha_operador, perfil_operador_esperado=perfil_operador)
    if not u:
        return fail("Credenciais inválidas ou perfil não confere", 401)

    perfil = perfil_operador.strip().lower()
    if perfil not in ("admin", "paciente", "recepcionista"):
        return fail("Perfil sem permissão para agendar", 403)
    
    # validar schedule (id_consulta) e disponibilidade
    schedule = get_schedule_by_id(id_atendimento)
    if not schedule:
        return fail("Consulta não encontrada", 404)


    # determinar qual paciente será usado
    if perfil == "paciente":
        # paciente agenda para si mesmo
        patient_id = get_patient_id_by_user_id(u["user_id"])
        if not patient_id:
            return fail("Paciente não encontrado", 404)
    else:
        # admin/recepcionista agenda para um paciente informado
        if not email_paciente:
            return fail("Admin/Recepcionista deve informar email_paciente", 400)

        patient_id = get_patient_id_by_email(email_paciente)
        if not patient_id:
            return fail("Paciente não encontrado", 404)

    # validar forma de pagamento
    fp = forma_pagamento.strip().lower()
    insurance_id = None

    if fp == "cartao":
        if not numero_cartao:
            return fail("Número do cartão é obrigatório", 400)
        try:
            validar_cartao_data_validade(data_validade)
        except ValueError as e:
            return fail(str(e), 400)

    elif fp == "convenio":
        insurance = get_insurance_by_patient_id(patient_id)

        if not insurance:
            return fail("Paciente não possui convênio válido", 422)

        if schedule["specialty"] not in insurance["specialties"]:
            return fail("Convênio não cobre a especialidade desta consulta", 422)

        insurance_id = insurance["insurance_id"]
    else:
        return fail("forma_pagamento inválida (use cartao|convenio)", 400)


    if not schedule["is_available"]:
        return fail("Horário indisponível", 409)

    # criar appointment e marcar schedule como indisponível
    appt = insert_appointment(
        patient_id=patient_id,
        schedule_id=id_atendimento,
        status="AGENDADO",
        insurance_id=insurance_id,
    )
    set_schedule_available(id_atendimento, False)

    return to_plain(ok(mensagem="Consulta agendada com sucesso", agendamento=appt, code=201))


def atualizar_status_consulta(perfil_operador, email_operador, senha_operador, id_consulta, status):
    # --- 0) validar status recebido ---
    status_db = map_status_cli_to_db(status)
    if not status_db:
        return fail("Status inválido. Use: confirmado, concluido, cancelado.", 400)

    # --- 1) autenticar usuário ---
    operador = get_user(email_operador, senha_operador)
    if not operador:
        return fail("Credenciais inválidas", 401)

    # --- 2) validar perfil informado vs perfil real ---
    perfil_req = (perfil_operador or "").strip().upper()
    perfil_real = operador["user_type"]  # vem do enum do banco: ADMIN, MEDICO, PACIENTE, RECEPCIONISTA

    if perfil_req != perfil_real:
        return fail(
            f"Perfil informado ({perfil_req}) não corresponde ao perfil do usuário ({perfil_real}).",
            403
        )

    # --- 3) regras de permissão por perfil ---
    if perfil_real == "RECEPCIONISTA":
        if status_db != "CANCELADO":
            return fail("Recepcionista só pode alterar o status para 'cancelado'.", 403)

    elif perfil_real == "MEDICO":
        if status_db not in ("CONCLUÍDO", "CANCELADO"):
            return fail("Médico só pode alterar o status para 'concluido' ou 'cancelado'.", 403)

    elif perfil_real == "PACIENTE":
        return fail("Paciente não tem permissão para alterar o status da consulta.", 403)

    elif perfil_real == "ADMIN":
        # admin pode todos os 3 que você definiu
        if status_db not in ("CONFIRMADO", "CONCLUÍDO", "CANCELADO"):
            return fail("Status inválido.", 400)

    else:
        return fail("Perfil inválido.", 400)

    # --- 4) carregar consulta (appointment) + schedule ---
    try:
        appointment_id = int(id_consulta)
    except (TypeError, ValueError):
        return fail("id_consulta inválido (precisa ser inteiro).", 400)

    appt = get_appointment_with_schedule(appointment_id)
    if not appt:
        return fail("Consulta não encontrada.", 404)

    # --- 5) regra extra: médico só mexe nas próprias consultas ---
    if perfil_real == "MEDICO":
        doctor_id = get_doctor_by_user_id(operador["user_id"])["doctor_id"]
        if not doctor_id:
            return fail("Registro de médico não encontrado.", 404)
        if doctor_id != appt["doctor_id"]:
            return fail("Médico não pode alterar consultas de outro médico.", 403)

    # --- 6) evitar mudanças inválidas ---
    # Ex: não permitir "confirmar" consulta já concluída/cancelada
    status_atual = appt["status"]
    if status_atual in ("CONCLUÍDO", "CANCELADO"):
        return fail(f"Não é possível alterar status: consulta está {status_atual}.", 409)

    # --- 7) atualizar status ---
    updated = update_appointment_status(appointment_id, status_db)
    if not updated:
        return fail("Falha ao atualizar status.", 500)

    # --- 8) efeitos colaterais ---
    # Se cancelar, libera o schedule para novo agendamento
    if status_db == "CANCELADO":
        set_schedule_available(appt["schedule_id"], True)

    return ok(mensagem="Status atualizado com sucesso.", consulta=updated, code=200)





# ------------------ BOOT ------------------

def main():
    server = SimpleXMLRPCServer(("0.0.0.0", 7001), allow_none=True, logRequests=True)
    server.register_introspection_functions()

    # Registrar com os nomes exatos que seu client chama
    server.register_function(criar_atendimento, "criar_atendimento")
    server.register_function(listar_atendimentos, "listar_atendimentos")
    server.register_function(excluir_atendimento, "excluir_atendimento")
    server.register_function(editar_atendimento, "editar_atendimento")
    server.register_function(atualizar_status_consulta, "atualizar_status_consulta")
    server.register_function(agendar_consulta, "agendar_consulta")
    server.register_function(consultas_agendadas, "consultas_agendadas")

    print("RPC Server rodando em http://0.0.0.0:7001")
    server.serve_forever()


if __name__ == "__main__":
    main()
