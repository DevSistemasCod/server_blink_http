import network
import socket
from machine import Pin
import time


led = Pin(2, Pin.OUT)
led.value(0)

REDE_SSID="WIFI_IOT_CFP601"
REDE_SENHA="iot@senai601"


def conectar_wifi(nome_rede, senha):
    # Cria uma interface de rede no modo cliente (station)
    rede = network.WLAN(network.STA_IF)
    rede.active(True)  # Ativa o Wi-Fi
    rede.connect(nome_rede, senha)  # Tenta conectar à rede com os dados fornecidos

    tentativas = 10  # Número de tentativas de conexão
    while not rede.isconnected() and tentativas > 0:
        print("Conectando ao Wi-Fi...")
        time.sleep(1)
        tentativas = tentativas - 1

    # Exibe resultado da conexão
    if rede.isconnected():
        print("Conectado ao Wi-Fi:", rede.ifconfig())
    else:
        print("Falha ao conectar ao Wi-Fi.")

# --- Função para carregar arquivos do sistema de arquivos ---
def carregar_arquivo(nome):
    try:
        with open(nome, 'r') as arquivo:
            return arquivo.read()
    except OSError as e:
        print("Erro ao carregar arquivo:", nome, "-", e)
        return None

# --- Envia resposta HTTP formatada ---
def enviar_resposta(conexao_socket, status=200, formato_conteudo='text/html', corpo=''):
    if corpo is None:
        corpo = ''
    if isinstance(corpo, str):
        corpo = corpo.encode()  # Converte string para bytes se necessário

    conexao_socket.send('HTTP/1.1 {} OK\r\n'.format(status))
    conexao_socket.send('Content-Type: {}\r\n'.format(formato_conteudo))
    conexao_socket.send('Content-Length: {}\r\n'.format(len(corpo)))
    conexao_socket.send('Connection: close\r\n\r\n')
    conexao_socket.sendall(corpo)

# --- Manipuladores de rota para o LED ---
def tratar_on(conexao_socket):
    led.value(1)  # Liga o LED
    print("LED ligado")
    enviar_resposta(conexao_socket, corpo="LED ligado")

def tratar_off(conexao_socket):
    led.value(0)  # Desliga o LED
    print("LED desligado")
    enviar_resposta(conexao_socket, corpo="LED desligado")


def tratar_css(conexao_socket):
    conteudo = carregar_arquivo('style.css')
    if conteudo is None:
        conteudo = ''
    enviar_resposta(conexao_socket, formato_conteudo='text/css', corpo=conteudo)

def tratar_js(conexao_socket):
    conteudo = carregar_arquivo('script.js')
    if conteudo is None:
        conteudo = ''
    enviar_resposta(conexao_socket, formato_conteudo='application/javascript', corpo=conteudo)

def tratar_index(conexao_socket):
    conteudo = carregar_arquivo('index.html')
    if not conteudo:
        conteudo = "<h1>Arquivo index.html não encontrado</h1>"
    enviar_resposta(conexao_socket, corpo=conteudo)


def servidor_http():
    # Cria o socket do servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', 80))  # Escuta na porta 80 em todas as interfaces
    servidor.listen(1)  # Aceita uma conexão por vez

    print("Servidor HTTP aguardando conexões...")

    while True:
        try:
            # Aguarda conexão de um cliente
            conexao_socket, endereco = servidor.accept()
            print("Cliente conectado de:", endereco)
            processar_requisicao(conexao_socket)
        except Exception as erro:
            print("Erro ao processar conexão:", erro)
        finally:
            conexao_socket.close()  # Fecha o socket da conexão após o atendimento


def processar_requisicao(conexao_socket):
    try:
        requisicao = conexao_socket.recv(1024).decode()
        print("Requisição recebida:\n", requisicao)

        if not requisicao.startswith('GET'):
            # Apenas requisições GET são aceitas
            enviar_resposta(conexao_socket, status=400, corpo="Requisição inválida.")
            return

        caminho = requisicao.split(' ')[1]  # Extrai o caminho solicitado

        # Roteia os comandos para o LED
        if caminho == '/2/on':
            tratar_on(conexao_socket)
        elif caminho == '/2/off':
            tratar_off(conexao_socket)
        else:
            # Se for a raiz, direciona para index.html
            if caminho == '/':
                caminho = '/index.html'

            nome_arquivo = caminho[1:]  # Remove a barra inicial
            conteudo = carregar_arquivo(nome_arquivo)

            if conteudo is None:
                enviar_resposta(conexao_socket, status=404, corpo="Arquivo não encontrado.")
            else:
                tipo = detectar_tipo_conteudo(nome_arquivo)
                enviar_resposta(conexao_socket, formato_conteudo=tipo, corpo=conteudo)

    except Exception as erro:
        print("Erro ao processar requisição:", erro)
        enviar_resposta(conexao_socket, status=500, corpo="Erro interno do servidor.")


def detectar_tipo_conteudo(nome_arquivo):
    if nome_arquivo.endswith('.html'):
        return 'text/html'
    elif nome_arquivo.endswith('.css'):
        return 'text/css'
    elif nome_arquivo.endswith('.js'):
        return 'application/javascript'
    else:
        return 'text/plain'  # Tipo padrão para arquivos desconhecidos


def main():
    conectar_wifi(REDE_SSID, REDE_SENHA)
    servidor_http()


main()

