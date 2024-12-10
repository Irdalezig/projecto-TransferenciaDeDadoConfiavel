# Desenho e Implementação de Protocolo de Transporte Confiável em python

## Sobre o Projeto

 Este projeto implementa protocolos RDT (Reliable Data Transfer) sobre sockets UDP em Python, garantindo o transporte confiável de ficheiros. O emissor fragmenta os ficheiros em pacotes, que são transmitidos de forma sequencial. O receptor, por sua vez, processa os pacotes recebidos, verifica sua integridade e ordem, e reagrupa-os para reconstruir o ficheiro original.

- **Funcionalidades:**
  - O remetente divide o arquivo em pacotes de 1000 bytes (exceto o último, que pode ser menor).
  - Utiliza uma janela de envio/recepção com tamanho configurável (entre 1 e 32 pacotes).
  - Permite a transmissão simultânea de múltiplos pacotes enquanto aguarda confirmações (ACKs).
  - O remetente envia pacotes numerados sequencialmente e retransmite pacotes perdidos após um timeout.
  - O receptor armazena pacotes recebidos fora de ordem e os organiza corretamente antes de gravá-los no arquivo.
  - O receptor envia ACKs para confirmar pacotes recebidos.
  - Reenvia o último ACK válido para pacotes fora da janela.
  - Identifica o último pacote (marcado com número de sequência 0) para encerrar a transmissão.

## Estrutura do Projecto

- `Debug.py`: Um arquivo Python responsável por executar tarefas de depuração e diagnóstico no projeto.
- `file-receiver.py`: Código do servidor encarregado de gerenciar a recepção de arquivos no projeto.
- `file-sender.py`: Código do cliente designado para realizar o envio de arquivos no projeto.
- `Makefile`: Script para compilar e executar o projeto.
- `log-packets.txt`: utilizado para monitorar, registrar e analisar pacotes no projeto.
- `file.txt`: Arquivo de texto utilizado para testes de integração entre os módulos de envio e recepção de arquivos.
- `vagrantfile`: Um arquivo de configuração do Vagrant, usado para configurar máquinas virtuais.
- `.vagrant/`: Diretório que contém metadados e configurações relacionadas ao Vagrant, incluindo informações sobre máquinas virtuais, sincronização de pastas e outros dados.
- `__pycache__/`: Diretório gerado automaticamente pelo Python, contendo arquivos compilados (.pyc).
- `debug_packet_log.log`: Arquivo de log utilizado para registrar informações detalhadas de depuração e análise do sistema.

## Objetivos

1. **Implementar comunicação em rede:**
   - Utilizar sockets UDP para troca de mensagens entre nós.
2. **Garantir a consistência dos dados:**
   - Desenvolver mecanismos para sincronização e manutenção da consistência.
3. **Explorar confiabilidade:**
   - Implementar estratégias para lidar com falhas de comunicação, duplicação de pacotes, perda de pacotes e pacotes fora de ordem.

## Requisitos
Os principais requisitos para a implementação incluem:

- **Ambiente de execução:**
  - **Python 3.x**: Este projecto foi implementado em Python 3 e deve ser executado nessa versão.
  - **Sistema Operacional**: Funciona em sistemas baseados em UNIX e Windows, com pequenas adaptações para cada ambiente.
  - **code run**(opcional)
  - **Atom**(opcional)
  - **Vagrant**: Uma ferramenta de automação para criar e gerenciar máquinas virtuais de forma rápida e consistente. 
  - **Virtualbox**: Um software de virtualização que hospeda as máquinas virtuais configuradas pelo Vagrant. Ele fornece o ambiente isolado para execução do projeto.
  
### Instalação

1. **Clone o repositório** para sua máquina local:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```

2. **Certifique-se de que Python 3, vagrant e o virtualbox estão instalados** e acessíveis no seu ambiente.

### Uso

#### 1. **Inicie o ambiente com Vagrant**

Dentro da pasta do projeto, execute o comando abaixo para iniciar as máquinas virtuais configuradas no `vagrantfile`:

```bash
vagrant up
```

Após a criação das máquinas virtuais, conecte-se a elas via SSH:

- Para o **File-Sender**:
  ```bash
  vagrant ssh file-sender
  ```
- Para o **File-Receiver**:
  ```bash
  vagrant ssh file-receiver
  ```

Dentro de cada máquina virtual, navegue para a pasta compartilhada configurada no Vagrant:

```bash
cd /vagrant
```

#### 2. **Iniciando o File-Receiver**

Na máquina virtual **File-Receiver**, execute o comando para iniciar o módulo de recepção. Este comando especifica o arquivo de saída (`output.txt`), a porta de escuta (`2222`) e um identificador para a janela (substitua `<numeroJanela>` por um número de por um úmero de 0-32 a sua escolha):

```bash
python3 file-receiver.py output.txt 2222 <numeroJanela>
```

#### 3. **Iniciando o File-Sender**

Na máquina virtual **File-Sender**, execute o comando para enviar o arquivo. Este comando especifica o arquivo de entrada (`file.txt`), o endereço IP do receptor (use `192.168.56.21`), a porta de destino (`2222`) e o identificador da janela (substitua `<numeroJanela>` por um úmero de 0-32 a sua escolha):

```bash
python3 file-sender.py file.txt 192.168.56.21 2222 <numeroJanela>
```

#### 4. **Visualizando o arquivo recebido**

Depois que o arquivo for completamente transferido, você pode visualizar o conteúdo na máquina **File-Receiver** utilizando o comando `cat`:

```bash
cat output.txt
```

#### 5. **Encerrando e limpando o ambiente**

Após finalizar as operações, destrua as máquinas virtuais para liberar recursos com o comando:

```bash
vagrant destroy
```
### Funcionamento Técnico

1. **File-Sender**:
   - O módulo de envio de arquivos (file-sender) é responsável por capturar os arquivos a serem transmitidos e encaminhá-los ao destinatário através de uma conexão estabelecida.
   - Ele utiliza sockets para estabelecer a conexão e transferir os dados de forma confiável.
   - Ele combina funções para capturar os arquivos do sistema local e enviá-los ao File-Receiver.
   - Inclui funcionalidades como dividir arquivos grandes em partes menores para transmissão, registrar logs das operações realizadas e validar o sucesso da transferência.

2. **File-Receiver**:
   - O módulo de recepção de arquivos (file-receiver) é projetado para monitorar a conexão em busca de dados recebidos.
   - Ele utiliza um loop contínuo para aguardar e processar os arquivos enviados.
   - Após receber os arquivos, ele pode armazená-los no diretório designado, validar a integridade dos dados (por exemplo, utilizando checksums) e notificar o remetente sobre o status da recepção.
   - Também pode retransmitir confirmações de recebimento para o File-Sender, garantindo que a comunicação seja confiável e rastreável.

## Equipa de Desenvolvimento
- Adriana Sampaio, Ângela Amaro e Raquel da Gama
- Professor: João Costa
- Curso: Engenharia Informática

## Licença
Este projecto de momento não está licenciado.

