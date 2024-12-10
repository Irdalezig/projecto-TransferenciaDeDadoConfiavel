#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import sys
from Debug import PacketDebugger  # Importa o debugger

# Constantes
# Tamanho máximo de um pedaço de dados a ser enviado (em bytes)
tamanho_max_pedaco = 1000
# Tempo limite para aguardar por um ACK (em segundos)
tempo_limite_segundos = 1
# Número máximo de timeouts consecutivos antes de abortar a transmissão
max_tentativas_timeout = 3

def tratar_erro(mensagem):
    # Exibe uma mensagem de erro e encerra o programa
    print(f"Erro: {mensagem}", file=sys.stderr)
    sys.exit(-1)

def main():
    # Verifica se os argumentos necessários foram fornecidos
    if len(sys.argv) != 5:
        print("Uso: python remetente.py <arquivo> <servidor_host> <servidor_porta> <tamanho_janela>")
        sys.exit(-1)

    # Lê os argumentos fornecidos pelo usuário
    nome_arquivo = sys.argv[1]
    servidor_host = sys.argv[2]
    servidor_porta = int(sys.argv[3])
    tamanho_janela = int(sys.argv[4])

    # Valida o tamanho da janela
    if tamanho_janela < 1 or tamanho_janela > 32:
        tratar_erro("O tamanho da janela deve estar entre 1 e 32.")

    try:
        # Cria um socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        tratar_erro("Erro ao criar socket.")

    # Configura o endereço do servidor
    endereco_servidor = (servidor_host, servidor_porta)

    try:
        # Abre o arquivo para leitura em modo binário
        arquivo = open(nome_arquivo, "rb")
    except IOError:
        tratar_erro("Erro ao abrir arquivo.")

    # Inicializa o debugger
    debugger = PacketDebugger()

    # Inicializa as variáveis de controle
    base = 1  # Número da base da janela de envio
    proximo_num_sequencia = 1  # Próximo número de sequência a ser enviado
    pedacos_em_transito = 0  # Quantidade de pedaços na janela
    tentativas_timeout = 0  # Contador de timeouts consecutivos
    envio_concluido = False  # Indica se o último pacote foi enviado

    while not envio_concluido or pedacos_em_transito > 0:
        # Envia pedaços de dados enquanto houver espaço na janela
        while not envio_concluido and pedacos_em_transito < tamanho_janela:
            dados = arquivo.read(tamanho_max_pedaco)
            if not dados:
                # Marca o último pacote com número de sequência 0
                pacote = struct.pack(f"!I{tamanho_max_pedaco}s", 0, b'')
                try:
                    sock.sendto(pacote, endereco_servidor)
                    print("Último pacote enviado.")
                    debugger.log_packet_info(0, 0, "Enviado", None)  # Log do último pacote
                except socket.error:
                    tratar_erro("Erro ao enviar último pacote.")

                envio_concluido = True
                break

            # Cria o pacote com número de sequência e dados
            pacote = struct.pack(f"!I{tamanho_max_pedaco}s", proximo_num_sequencia, dados.ljust(tamanho_max_pedaco, b'\x00'))
            try:
                # Inicia o temporizador para o pacote
                debugger.start_timing(proximo_num_sequencia)

                # Envia o pacote para o servidor
                sock.sendto(pacote, endereco_servidor)
                print(f"Pacote enviado {proximo_num_sequencia}")

                # Log do envio do pacote
                debugger.log_packet_info(proximo_num_sequencia, len(dados), "Enviado")
            except socket.error:
                tratar_erro("Erro ao enviar pacote.")

            # Atualiza as variáveis de controle
            proximo_num_sequencia += 1
            pedacos_em_transito += 1

        # Configura o tempo limite para o socket
        sock.settimeout(tempo_limite_segundos)

        try:
            # Aguarda por ACKs
            while True:
                ack, _ = sock.recvfrom(8)
                # Extrai o número de sequência do ACK recebido
                num_ack = struct.unpack("!I", ack[:4])[0]
                print(f"ACK recebido {num_ack}")

                # Log de ACK recebido
                debugger.log_packet_info(num_ack, 0, "ACK Recebido")

                if num_ack == 0:
                    # ACK final recebido, encerra a transmissão
                    print("ACK do último pacote recebido. Encerrando transmissão...")
                    envio_concluido = True
                    break

                if num_ack >= base:
                    # Atualiza a base e reduz o número de pedaços em trânsito
                    pedacos_em_transito -= (num_ack - base + 1)
                    base = num_ack + 1
                    tentativas_timeout = 0

                if pedacos_em_transito == 0:
                    # Sai do loop se todos os pedaços forem confirmados
                    break

        except socket.timeout:
            # Incrementa o contador de timeouts
            tentativas_timeout += 1
            if tentativas_timeout >= max_tentativas_timeout:
                # Encerra a transmissão após atingir o limite de timeouts
                print("Limite de timeouts alcançado. Encerrando...", file=sys.stderr)
                arquivo.close()
                sock.close()
                sys.exit(-1)

            # Retransmite a janela após o timeout
            print("Timeout ocorrido. Retransmitindo janela.")
            arquivo.seek((base - 1) * tamanho_max_pedaco)
            proximo_num_sequencia = base
            pedacos_em_transito = 0

    # Fecha o arquivo e o socket
    arquivo.close()
    sock.close()

if __name__ == "__main__":
    main()

#fim do ficheiro