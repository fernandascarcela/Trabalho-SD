package br.com.clinica.convenio;

import io.grpc.stub.StreamObserver;

// Imports das classes geradas pelo gRPC
// Certifique-se de que o pacote aqui bate com o "option java_package" do seu .proto
import br.com.clinica.convenio.ConvenioServiceGrpc;
import br.com.clinica.convenio.ValidarConvenioRequest;
import br.com.clinica.convenio.ValidarConvenioResponse;

@SuppressWarnings("unused")
public class ConvenioServiceImpl extends ConvenioServiceGrpc.ConvenioServiceImplBase {

    @Override
    public void validarConvenio(ValidarConvenioRequest request, StreamObserver<ValidarConvenioResponse> responseObserver) {

        System.out.println(">>> Recebendo requisição gRPC");
        System.out.println("Email: " + request.getEmail());
        System.out.println("Carteirinha: " + request.getNumeroCarteirinha());

        // AQUI ESTÁ O SEGREDO:
        // Chamamos a classe VerificacaoConvenio que tem toda a lógica de SQL e Regras
        String resultado = VerificacaoConvenio.realizarCadastroCompleto(
                request.getEmail(),            // Vem do .proto
                request.getSenha(),            // Vem do .proto
                request.getCpf(),              // Vem do .proto
                request.getNumeroCarteirinha(),// Vem do .proto
                request.getDataDeValidade()    // Vem do .proto
        );

        // Se a string de retorno começar com "Sucesso", então boolean = true
        boolean sucesso = resultado.startsWith("Sucesso");

        // Monta a resposta para devolver ao Python
        ValidarConvenioResponse response = ValidarConvenioResponse.newBuilder()
                .setSucesso(sucesso)
                .setMensagem(resultado)
                .build();

        // Envia
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}