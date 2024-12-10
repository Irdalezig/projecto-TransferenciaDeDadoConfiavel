#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import sys
from Debug import PacketDebugger  # Importa o debugger

# Tamanho máximo de um pedaço de dados (em bytes)
tamanho_max_pedaco = 1000

def tratar_erro(mensagem):
    # Exibe uma mensagem de erro e encerra o programa
    print(f"Erro: {mensagem}", file=sys.stderr)
    sys.exit(-1)

def main():
    # Verifica se os argumentos necessários foram fornecidos
    if len(sys.argv) != 4:
        print("Uso: python receptor_sr.py  <arquivo_destino> <porta> <tamanho_janela>")
        sys.exit(-1)

    # Lê os argumentos fornecidos pelo usuário
    arquivo_destino = sys.argv[1]
    porta = int(sys.argv[2])
    tamanho_janela = int(sys.argv[3])

    if tamanho_janela < 1 or tamanho_janela > 32:
        tratar_erro("O tamanho da janela deve estar entre 1 e 32.")

    try:
        # Cria um socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Liga o socket ao endereço local e porta
        sock.bind(("", porta))
        print(f"Receptor ligado na porta {porta}")
    except socket.error:
        tratar_erro("Erro ao criar ou ligar o socket.")

    try:
        # Abre o arquivo para escrita em modo binário
        arquivo = open(arquivo_destino, "wb")
    except IOError:
        tratar_erro("Erro ao abrir arquivo para escrita.")

    # Inicializa o debugger
    debugger = PacketDebugger()

    # Inicializa as variáveis de controle
    base = 1  # Base da janela (número esperado mais baixo)
    janela_recebida = [None] * tamanho_janela  # Armazena pacotes recebidos fora de ordem
    janela_ack = [False] * tamanho_janela  # Rastrea quais pacotes já foram confirmados
    ultimo_num_sequencia = base + tamanho_janela - 1  # Número máximo da janela

    while True:
        try:
            # Recebe um pacote do remetente
            pacote, endereco_remetente = sock.recvfrom(1024 + 4)  # 4 bytes para o número de sequência
            if not pacote:
                # Sai do loop se não houver mais pacotes
                break

            # Extrai o número de sequência e os dados do pacote
            num_sequencia, dados = struct.unpack(f"!I{tamanho_max_pedaco}s", pacote)
            dados = dados.rstrip(b'\x00')  # Remove bytes de preenchimento

            debugger.log_packet_info(num_sequencia, len(dados), "Recebido")  # Log de pacote recebido

            if num_sequencia == 0:
                # Último pacote recebido
                print("Último pacote recebido. Enviando ACK final e encerrando.")
                ack = struct.pack("!I", 0)
                sock.sendto(ack, endereco_remetente)
                debugger.log_packet_info(0, 0, "ACK Enviado", None)  # Log do ACK final
                break

            print(f"Pacote recebido {num_sequencia} de {endereco_remetente}")

            # Verifica se o número de sequência está na janela atual
            if base <= num_sequencia <= ultimo_num_sequencia:
                # Calcula o índice do pacote na janela
                indice = (num_sequencia - base) % tamanho_janela

                # Se o pacote já não foi recebido, armazena e confirma
                if not janela_ack[indice]:
                    janela_recebida[indice] = dados
                    janela_ack[indice] = True
                    print(f"Pacote {num_sequencia} armazenado.")

                    # Envia um ACK para o remetente
                    ack = struct.pack("!I", num_sequencia)
                    sock.sendto(ack, endereco_remetente)
                    print(f"ACK enviado {num_sequencia}")

                    debugger.log_packet_info(num_sequencia, 0, "ACK Enviado")  # Log do ACK

                # Processa os pacotes em ordem crescente a partir da base
                while janela_ack[0]:
                    # Grava o pacote no arquivo e avança a janela
                    arquivo.write(janela_recebida[0])
                    janela_recebida.pop(0)
                    janela_ack.pop(0)
                    janela_recebida.append(None)
                    janela_ack.append(False)

                    base += 1
                    ultimo_num_sequencia += 1
                    print(f"Base atualizada para {base}")
            else:
                # Pacote fora da janela, envia ACK para o último pacote válido
                ack = struct.pack("!I", base - 1)
                sock.sendto(ack, endereco_remetente)
                print(f"Pacote fora da janela. ACK reenviado {base - 1}")

                debugger.log_packet_info(base - 1, 0, "ACK Reenviado")  # Log de ACK reenviado

        except KeyboardInterrupt:
            print("Encerrando o receptor.")
            break
        except socket.error as e:
            print(f"Erro na comunicação do socket: {e}", file=sys.stderr)

    # Fecha o arquivo e o socket
    arquivo.close()
    sock.close()

if __name__ == "__main__":
    main()
