import json
from pathlib import Path
from dados import carregar, salvar, concluir
from entrada import escolher
from conteudo import ATIVIDADES, PIX, TERMOS

#Funções

def aula_navegador(dados):
    print("\n=== Usar o navegador ===")
    print("O navegador é o app que abre sites (Chrome, Safari...).")
    print("1. Toque na barra de pesquisa.")
    print("2. Digite o que você procura e toque em buscar.")
    if escolher(["Concluir aula"]) == 1:
        concluir(dados, "navegador")


def quiz(dados, chave, titulo, pergunta, opcoes, certa):
    print(f"\n=== {titulo} ===\n{pergunta}")
    while True:
        r = escolher(opcoes)
        if r == 0:
            return
        if r == certa:
            print("\nMuito bem! Resposta certa.")
            concluir(dados, chave)
            return
        print("\nQuase! Tente de novo.")


def pix(dados):
    for n, (titulo, texto) in enumerate(PIX, 1):
        print(f"\n=== Pix · passo {n} de {len(PIX)}: {titulo} ===")
        print(texto)
        ultimo = n == len(PIX)
        if escolher(["Concluir aula" if ultimo else "Próximo passo"], "Sair") == 0:
            return
    print("\nAntes de confirmar um Pix, confira sempre o nome de quem recebe.")
    concluir(dados, "pix")


def glossario():
    busca = input("\nDigite uma palavra (Enter mostra todas): ").strip().lower()
    achou = False
    for termo, (significado, exemplo) in TERMOS.items():
        if busca in termo.lower() or busca in significado.lower():
            print(f"\n{termo}: {significado}\n  Exemplo: {exemplo}")
            achou = True
    if not achou:
        print("Palavra não encontrada.")
    input("\nAperte Enter para voltar. ")


def progresso(dados):
    feitas = dados["concluidas"]
    total = len(ATIVIDADES)
    print(f"\n=== Meu progresso: {len(feitas)} de {total} atividades ===")
    for chave, nome in ATIVIDADES.items():
        print(f"  [{'x' if chave in feitas else ' '}] {nome}")
    choice = escolher(["Resetar o progresso. "])
    if choice == 1:
        certeza = input("Você tem certeza? Isso apagará todo o seu progresso. (s/n) ")
        if certeza.lower() == "s":
            dados["concluidas"] = []
            salvar(dados)


def alterar_nome(dados):
    
    if dados["nome"] == "amigo(a)":
        nome = input(f"\nDigite o seu nome: ").strip()
        if nome:
            dados["nome"] = nome
            salvar(dados)
            print(f"Nome alterado para {nome}.")
    else:
        novo_nome = input("Digite seu novo nome: ").strip()
        if novo_nome:
            dados["nome"] = novo_nome
            salvar(dados)
            print(f"Nome alterado para {novo_nome}.")
        else:
            print("Nome não alterado.")