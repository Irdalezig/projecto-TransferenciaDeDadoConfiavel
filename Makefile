# Definição de variáveis
PYTHON = python
PYTHON3 = python3
VAGRANT = vagrant
EMISSOR = file-sender.py
RECEPTOR = file-receiver.py

# Argumentos de execução local
PORTA_RECEIVER = 1234
ARQUIVO_RECEIVER = output.txt
JANELA_RECEIVER = 1

PORTA_SENDER = 1234
ARQUIVO_SENDER = file.txt
HOST_SENDER = localhost
JANELA_SENDER = 1

# Argumentos de execução virtual
PORTA = 2222
ARQUIVO_R = output.txt
JANELA_RECEIVER = 1

PORTA = 2222
ARQUIVO_SENDER = file.txt
HOST = 192.168.56.21
JANELA = 1



# Alvos padrão
all: help

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make local-receiver"
	@echo "      - Executa o receptor localmente com argumentos predefinidos."
	@echo "  make local-sender"
	@echo "      - Executa o emissor localmente com argumentos predefinidos."
	@echo "  make vagrant-up"
	@echo "      - Inicia as máquinas virtuais com o Vagrant."
	@echo "  make file-receiver  ARQUIVO=<arquivo_destino> PORTA=<porta> JANELA=<tamanho_janela>"
	@echo "      - Executa o receptor na máquina virtual."
	@echo "  make file-sender ARQUIVO=<arquivo_origem> HOST=<host> PORTA=<porta> JANELA=<tamanho_janela>"
	@echo "      - Executa o emissor na máquina virtual."
	@echo "  make vagrant-destroy"
	@echo "      - Destrói as máquinas virtuais."

# Execução local
local-receiver:
	@echo "Iniciando o receptor localmente..."
	$(PYTHON) $(RECEPTOR)  $(ARQUIVO_RECEIVER) $(PORTA_RECEIVER) $(JANELA_RECEIVER)

local-sender:
	@echo "Iniciando o emissor localmente..."
	$(PYTHON) $(EMISSOR) $(ARQUIVO_SENDER) $(HOST_SENDER) $(PORTA_SENDER) $(JANELA_SENDER)

# Vagrant comandos
vagrant-up:
	@echo "Iniciando as maquinas virtuais..."
	$(VAGRANT) up

file-receiver:
	@echo "Iniciando o receptor na maquina virtual..."
	$(VAGRANT) ssh file-receiver -c "$(PYTHON3) /vagrant/$(RECEPTOR)  $(ARQUIVO_R) $(PORTA) $(JANELA)"

file-sender:
	@echo "Iniciando o emissor na maquina virtual..."
	$(VAGRANT) ssh file-sender -c "$(PYTHON3) /vagrant/$(EMISSOR) /vagrant/$(ARQUIVO_SENDER) $(HOST) $(PORTA) $(JANELA)"

vagrant-destroy:
	@echo "Destruindo as maquinas virtuais..."
	$(VAGRANT) destroy -f
