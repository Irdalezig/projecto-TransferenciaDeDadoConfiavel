# -*- coding: utf-8 -*-
import time
import logging

# Configuração de logs
logging.basicConfig(
    filename="debug_packet_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class PacketDebugger:
    def __init__(self):
        self.start_times = {}  # Armazena os tempos de início de pacotes

    def log_packet_info(self, seq_num, packet_size, status, start_time=None, address=None, event=None):
        """
        Registra informações sobre um pacote.

        :param seq_num: Número de sequência do pacote.
        :param packet_size: Tamanho do pacote em bytes.
        :param status: Status do pacote (Enviado, Recebido, Retransmitido, etc.).
        :param start_time: Tempo de início da transmissão do pacote (opcional).
        :param address: Endereço relacionado ao evento (opcional).
        :param event: Evento adicional para log (ex: Timeout, ACK fora de ordem).
        """
        end_time = time.time()
        if start_time is not None:
            elapsed_time = end_time - start_time
            elapsed_time_str = f"{elapsed_time:.4f}s"
        else:
            elapsed_time_str = "indisponivel"

        log_message = (
            f"Pacote {seq_num}: Tamanho={packet_size} bytes, "
            f"Tempo={elapsed_time_str}, Status={status}"
        )
        if address:
            log_message += f", Endereço={address}"
        if event:
            log_message += f", Evento={event}"

        logging.info(log_message)

    def start_timing(self, seq_num):
        """Inicia o temporizador para um pacote."""
        if seq_num not in self.start_times:
            self.start_times[seq_num] = time.time()
        else:
            logging.warning(f"Temporizador já iniciado para o pacote {seq_num}.")

    def end_timing_and_log(self, seq_num, packet_size, status, address=None, event=None):
        """
        Finaliza o temporizador e registra informações do pacote.

        :param seq_num: Número de sequência do pacote.
        :param packet_size: Tamanho do pacote em bytes.
        :param status: Status do pacote (ex: Sucesso, Falha).
        :param address: Endereço relacionado ao evento (opcional).
        :param event: Evento adicional para log (opcional).
        """
        start_time = self.start_times.pop(seq_num, None)
        if start_time is None:
            logging.warning(f"Tempo de início não encontrado para o pacote {seq_num}.")
        self.log_packet_info(seq_num, packet_size, status, start_time, address, event)

    def log_event(self, event_message, address=None):
        """
        Registra eventos gerais que não estão relacionados diretamente a um pacote.

        :param event_message: Descrição do evento.
        :param address: Endereço relacionado ao evento (opcional).
        """
        log_message = f"Evento: {event_message}"
        if address:
            log_message += f", Endereço={address}"
        logging.info(log_message)
