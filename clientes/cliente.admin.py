import requests

API_USUARIOS = "http://localhost:8000"
API_AGENDAMENTO = "http://localhost:8001"


class ClienteAdmin:
    def __init__(self):
        self.token = None

    def login(self):
        email = input("Email: ")
        senha = input("Senha: ")
        print("[REST] Login →", email)
        self.token = "TOKEN_FAKE_ADMIN"

    # -----------------------
    # FUNÇÕES
    # -----------------------
    def criar_usuario(self):
        nome = input("Nome: ")
        email = input("Email: ")
        senha = input("Senha: ")
        tipo = input("Tipo (paciente/medico/recepcionista/admin): ")

        payload = {"nome": nome, "email": email, "senha": senha, "tipo": tipo}
        print("\n[REST] Criando usuário →", payload)

    def desativar_usuario(self):
        user_id = input("ID do usuário: ")
        print(f"[REST] DELETE /usuarios/{user_id}")

    def listar_agendamentos(self):
        print("[REST] GET /consultas/todas")

    def ver_logs(self):
        print("[REST] GET /logs")


if __name__ == "__main__":
    cli = ClienteAdmin()
    cli.login()

    print("\n=== CLIENTE ADMINISTRADOR ===")

    while True:
        print("\n1. Criar usuário")
        print("2. Desativar usuário")
        print("3. Listar agendamentos")
        print("4. Ver logs")
        print("0. Sair")

        op = input("> ")

        if op == "1":
            cli.criar_usuario()
        elif op == "2":
            cli.desativar_usuario()
        elif op == "3":
            cli.listar_agendamentos()
        elif op == "4":
            cli.ver_logs()
        elif op == "0":
            break
