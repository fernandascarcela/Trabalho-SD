package br.com.clinica.convenio;

import java.sql.*;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class VerificacaoConvenio {

    private static final String URL = System.getenv("DB_URL");
    private static final String USER = System.getenv("DB_USER");
    private static final String PASSWORD = System.getenv("DB_PASSWORD");

    /**
     * Método Principal: Orquestra todo o fluxo de validação e cadastro.
     * Retorna uma String indicando sucesso ou a mensagem de erro.
     */
    public static String realizarCadastroCompleto(String email, String senha, String cpf, 
                                                  String numeroCarteirinha, String dataValidade) {
        
        Connection conn = null;

        try {
            // 1. Validar Login (Email e Senha)
            if (!validarCredenciais(email, senha)) {
                return "Erro: Credenciais de operador inválidas.";
            }

            // 2. Validar Formato da Carteirinha
            if (!validarFormatoCarteirinha(numeroCarteirinha)) {
                return "Erro: Formato da carteirinha inválido (use XX-XXXX-XXXXX).";
            }

            // 3. Validar Data de Validade
            if (!validarDataValidade(dataValidade)) {
                return "Erro: Carteirinha vencida ou data inválida.";
            }

            // --- INÍCIO DA OPERAÇÃO DE BANCO DE DADOS ---
            conn = DriverManager.getConnection(URL, USER, PASSWORD);
            
            // Desliga o commit automático para iniciar uma transação segura
            conn.setAutoCommit(false); 

            // 4. Buscar ID do Paciente pelo CPF
            Integer patientId = buscarPatientId(conn, cpf);
            if (patientId == null) {
                conn.rollback(); // Cancela qualquer coisa pendente
                return "Erro: Paciente não encontrado com o CPF informado.";
            }

            // 5. Salvar o Convênio (Tabela insurance)
            Integer insuranceId = salvarConvenio(conn, patientId, numeroCarteirinha, dataValidade);

            // 6. Definir e Salvar Especialidades (Baseado no último dígito)
            salvarEspecialidades(conn, insuranceId, numeroCarteirinha);

            // Se chegou até aqui sem erro, confirma tudo no banco
            conn.commit(); 
            return "Sucesso: Convênio cadastrado e especialidades vinculadas!";

        } catch (SQLException e) {
            // Se der erro de SQL (ex: carteirinha duplicada), faz rollback
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            }
            // Verifica se é erro de duplicidade
            if (e.getMessage().contains("insurance_card_number_key") || e.getSQLState().equals("23505")) {
                return "Erro: Esse número de carteirinha já está cadastrado.";
            }
            e.printStackTrace();
            return "Erro Interno de Banco de Dados: " + e.getMessage();
        } catch (Exception e) {
            return "Erro inesperado: " + e.getMessage();
        } finally {
            // Fecha a conexão
            if (conn != null) {
                try { conn.close(); } catch (SQLException e) { e.printStackTrace(); }
            }
        }
    }

    // ==========================================
    // MÉTODOS AUXILIARES DE VALIDAÇÃO E BANCO
    // ==========================================

    // PASSO 1: Verifica Email e Senha (abre uma conexão rápida só para leitura)
    private static boolean validarCredenciais(String email, String senha) {
        String sql = "SELECT user_id FROM users WHERE email = ? AND password = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setString(1, email);
            stmt.setString(2, senha);
            
            try (ResultSet rs = stmt.executeQuery()) {
                return rs.next(); // Retorna true se achou o usuário
            }
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    // PASSO 2: Regex
    private static boolean validarFormatoCarteirinha(String carteirinha) {
        return carteirinha != null && carteirinha.matches("\\d{2}-\\d{4}-\\d{5}");
    }

    // PASSO 3: Data Futura
    private static boolean validarDataValidade(String validade) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/yyyy");
            YearMonth dataValidadeYm = YearMonth.parse(validade, formatter);
            YearMonth hoje = YearMonth.now();
            return !dataValidadeYm.isBefore(hoje);
        } catch (Exception e) {
            return false; // Data em formato errado
        }
    }

    // PASSO 4: Busca Paciente (usa a conexão da transação)
    private static Integer buscarPatientId(Connection conn, String cpf) throws SQLException {
        String sql = "SELECT patient_id FROM patient WHERE cpf = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, cpf);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("patient_id");
                }
            }
        }
        return null;
    }

    // PASSO 5: Insert Insurance
    private static Integer salvarConvenio(Connection conn, int patientId, String carteirinha, String dataValidadeStr) throws SQLException {
        String sql = "INSERT INTO insurance (patient_id, card_number, expiration_date, status) VALUES (?, ?, ?, 'VALIDO') RETURNING insurance_id";
        
        // Converte string "MM/yyyy" para Data SQL (dia 1 do mês ou último dia)
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM/yyyy");
        YearMonth ym = YearMonth.parse(dataValidadeStr, formatter);
        LocalDate dataCompleta = ym.atEndOfMonth(); // Define validade para o último dia do mês
        Date sqlDate = Date.valueOf(dataCompleta);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, patientId);
            stmt.setString(2, carteirinha);
            stmt.setDate(3, sqlDate);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("insurance_id");
                }
            }
        }
        throw new SQLException("Falha ao inserir convênio, nenhum ID obtido.");
    }

    // PASSO 6: Insert Especialidades
    private static void salvarEspecialidades(Connection conn, int insuranceId, String carteirinha) throws SQLException {
        // Lógica do último dígito
        char ultimoChar = carteirinha.charAt(carteirinha.length() - 1);
        int ultimoDigito = Character.getNumericValue(ultimoChar);
        
        List<String> especialidades = new ArrayList<>();

        // IMPORTANTE: Os nomes aqui DEVEM ser idênticos aos do ENUM no banco (Case Sensitive e Typos inclusos)
        // SQL fornecido: ENUM ('FISIOTERAPEUTA', 'NUTRICIONISTA', 'PISIQUIATRA', 'DERMATOLOGISTA', 'PEDIATRIA')
        
        if (ultimoDigito >= 0 && ultimoDigito <= 5) {
            especialidades.add("FISIOTERAPEUTA");
            especialidades.add("NUTRICIONISTA");
            especialidades.add("PEDIATRIA"); // No SQL está PEDIATRIA, não PEDIATRA
        } else {
            // Digitos 6 a 9
            especialidades.add("DERMATOLOGISTA");
            especialidades.add("PISIQUIATRA"); // Mantendo o erro de digitação do seu SQL (PISIQUIATRA) para não dar erro
        }

        String sql = "INSERT INTO insurance_specialty (insurance_id, specialty) VALUES (?, ?::specialty_enum)";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            for (String esp : especialidades) {
                stmt.setInt(1, insuranceId);
                stmt.setString(2, esp);
                stmt.executeUpdate();
            }
        }
    }
}