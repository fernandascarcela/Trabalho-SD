package br.com.clinica.convenio;

import io.grpc.Server;
import io.grpc.ServerBuilder;

public class ConvenioServer {

    public static void main(String[] args) throws Exception {
        Server server = ServerBuilder
                .forPort(50051)
                .addService(new ConvenioServiceImpl())
                .build();

        server.start();
        System.out.println(" Serviço de Convênio gRPC rodando na porta 50051");

        server.awaitTermination();
    }
}
