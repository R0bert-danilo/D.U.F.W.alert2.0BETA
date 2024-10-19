import asyncio
import json
import os
from datetime import datetime
import discord
import nltk
import pyfiglet
import requests
from colorama import Fore, Style, init

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

init()

CONFIG_FILE = "config.json"

total_usuarios = 0
total_bots = 0
total_admins = 0

def carregar_configuracoes():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_configuracoes(bot_token, chat_id, discord_token, config_nome):
    configurations = {
        "telegram_bot_token": bot_token,
        "telegram_chat_id": chat_id,
        "discord_token": discord_token,
        "nome_config": config_nome
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(configurations, f, indent=4)

def excluir_configuracoes():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("Configurações excluídas com sucesso!")
    else:
        print("Nenhuma configuração encontrada para excluir.")

configuracoes = carregar_configuracoes()
telegram_bot_token = configuracoes.get("telegram_bot_token", '')
telegram_chat_id = configuracoes.get("telegram_chat_id", '')
global_token = configuracoes.get("discord_token", '')
global_nome_configuracao = configuracoes.get("nome_config", '')

def enviar_mensagem_telegram(mensagem):
    mensagem = mensagem.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        'chat_id': telegram_chat_id,
        'text': mensagem,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Falha ao enviar mensagem para o Telegram: {response.status_code} - {response.text}")

def configurar_bot():
    global telegram_bot_token, telegram_chat_id, global_token, global_nome_configuracao
    print("\n--- Configuração do Bot ---")
    telegram_bot_token = input("Digite o Token do Bot do Telegram: ")
    telegram_chat_id = input("Digite o ID do Chat do Telegram: ")
    global_token = input("Digite o Token do Bot do Discord: ")
    global_nome_configuracao = input("Digite um nome para salvar as configurações: ")
    salvar_configuracoes(telegram_bot_token, telegram_chat_id, global_token, global_nome_configuracao)
    print("\nConfigurações salvas com sucesso!\n")
    clear_screen()

def ver_configuracoes():
    global telegram_bot_token, telegram_chat_id, global_token, global_nome_configuracao
    if not telegram_bot_token or not telegram_chat_id or not global_token:
        print("Nenhuma configuração salva.")
    else:
        print("\n--- Configurações Salvas ---")
        print(f"Nome da Configuração: {global_nome_configuracao}")
        print(f"Token do Bot do Telegram: {telegram_bot_token}")
        print(f"ID do Chat do Telegram: {telegram_chat_id}")
        print(f"Token do Bot do Discord: {global_token}\n")
        excluir = input("Deseja excluir as configurações? (s/n): ").strip().lower()
        if excluir == 's':
            excluir_configuracoes()
            telegram_bot_token = ''
            telegram_chat_id = ''
            global_token = ''
            global_nome_configuracao = ''
    clear_screen()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def apresentacao():
    letras = ['D . U . F . W . alert']
    cores = [Fore.RED]
    for i, letra in enumerate(letras):
        result = pyfiglet.figlet_format(letra)
        print(cores[i] + result + Style.RESET_ALL)
        await asyncio.sleep(2)
        clear_screen()
    print(Fore.MAGENTA + "Bem-vindo ao bot de monitoramento!" + Style.RESET_ALL)
    await asyncio.sleep(2)
    clear_screen()

async def exibir_menu():
    while True:
        print("\n=== Menu Principal ===")
        print("1. Configurar Bot (Tokens e ID)")
        print("2. Ver Configurações Salvas")
        print("3. Excluir Configurações")
        print("4. Criar Relatório")
        print("5. Iniciar Monitoramento")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")
        if opcao == '1':
            configurar_bot()
        elif opcao == '2':
            ver_configuracoes()
        elif opcao == '3':
            excluir_configuracoes()
            clear_screen()
        elif opcao == '4':
            await criar_relatorio()
            clear_screen()
        elif opcao == '5':
            await iniciar_monitoramento()
            clear_screen()
        elif opcao == '6':
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")

async def criar_relatorio():
    global global_token, total_usuarios, total_bots, total_admins
    if not global_token:
        print("Você precisa configurar o bot antes de criar o relatório!")
        return
    print("\n--- Criando Relatório ---")
    data_hora_atual = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        global total_usuarios, total_bots, total_admins
        tasks = [processar_guild(guild) for guild in client.guilds]
        await asyncio.gather(*tasks)
        texto_relatorio = (
            f"Relatório gerado em: {data_hora_atual}\n"
            f"Nome da Configuração: {global_nome_configuracao}\n"
            f"Total de Usuários: {total_usuarios}\n"
            f"Total de Bots: {total_bots}\n"
            f"Total de Administradores: {total_admins}\n"
        )
        nome_arquivo = f"relatorio_{data_hora_atual}.txt"
        with open(nome_arquivo, "w") as arquivo:
            arquivo.write(texto_relatorio)
        print(f"Relatório salvo como {nome_arquivo}!")
        await client.close()

    await client.start(global_token)

async def processar_guild(guild):
    global total_usuarios, total_bots, total_admins
    total_usuarios += len([membro for membro in guild.members if not membro.bot])
    total_bots += len([membro for membro in guild.members if membro.bot])
    total_admins += len([membro for membro in guild.members if membro.guild_permissions.administrator])

async def iniciar_monitoramento():
    global global_token
    if not global_token:
        print("Você precisa configurar o bot antes de iniciar o monitoramento!")
        return
    print("Iniciando o monitoramento...")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Bot conectado como {client.user}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        palavras_proibidas = ["merda", "caralho", "porra", "cacete", "puta", "bosta", "filho da puta", "desgraçado",
                              "idiota", "babaca", "otário", "maluco", "imbecil", "cretino", "fdp", "arrombado",
                              "desgraça", "pau no cu", "cocô", "saco de merda", "bater", "espancar", "matar",
                              "destruir", "quebrar", "acabar com", "ferrar", "acabar com a sua raça", "saco de pancada",
                              "cabeça de melão", "safado", "corno", "porcaria", "merda de", "caralho de", "porra de",
                              "cacete de", "putaria", "bostinha", "bagulho", "putanheiro", "piranha", "pedaço de lixo",
                              "pedaço de merda"]
        for palavra in palavras_proibidas:
            if palavra in message.content.lower():
                classe = "Palavra Proibida"
                mensagem_formatada = (
                    f"*Data e Hora:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"*Usuário:* {message.author.name}\n"
                    f"*Classe:* {classe}\n"
                    f"*Mensagem:* {message.content}\n"
                    f"*Link do Usuário:* {message.author.mention}"
                )
                print(mensagem_formatada)
                enviar_mensagem_telegram(mensagem_formatada)

    await client.start(global_token)

async def main():
    await apresentacao()
    await exibir_menu()

if __name__ == "__main__":
    asyncio.run(main())
