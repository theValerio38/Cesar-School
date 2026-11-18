#!/usr/bin/env python3
"""LEILA — versão simples para o terminal.

Rode com:  python leila_simples.py
O nome e o progresso ficam salvos em leila_dados.json (na mesma pasta).
"""

import json
from pathlib import Path

ARQUIVO = Path(__file__).with_name("leila_dados.json")

# ---------- conteúdo ----------

ATIVIDADES = {
    "navegador": "Aula: usar o navegador",
    "anexar": "Quiz: anexar uma foto",
    "golpe": "Simulação: golpe do prêmio",
    "pix": "Aula: como fazer um Pix",
}

PIX = [
    ("Abra a área Pix", "No app do seu banco, toque em “Pix” e depois em “Transferir”."),
    ("Informe a chave", "Digite a chave de quem vai receber: telefone, e-mail, CPF ou aleatória."),
    ("Digite o valor", "Informe quanto quer enviar. Ex.: R$ 25,00."),
    ("Confira e confirme", "Veja nome, banco e valor. Só então confirme com sua senha."),
]

TERMOS = {
    "Aplicativo": ("Um programa que você usa no celular.", "WhatsApp e câmera."),
    "Wi-Fi": ("Internet sem fio.", "Procure a rede de casa e digite a senha."),
    "Link": ("Texto ou botão que leva a outra página.", "Só toque se confiar em quem enviou."),
    "Senha": ("Código secreto que protege sua conta.", "Não conte para ninguém."),
    "Pix": ("Enviar e receber dinheiro pelo banco.", "Confira nome e valor antes de confirmar."),
    "QR Code": ("Quadrado que a câmera consegue ler.", "Pode abrir um site ou um pagamento."),
    "Navegador": ("App para visitar sites.", "Chrome, Safari e Firefox."),
    "Golpe digital": ("Tentativa de enganar alguém online.", "Desconfie de prêmios e pressa."),
}

# ---------- dados salvos ----------

def carregar():
    try:
        dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        dados = {}
    if not isinstance(dados, dict):
        dados = {}
    return {"nome": dados.get("nome", ""), "concluidas": dados.get("concluidas", [])}


def salvar(dados):
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def concluir(dados, chave):
    if chave not in dados["concluidas"]:
        dados["concluidas"].append(chave)
        salvar(dados)

# ---------- entrada ----------

def escolher(opcoes, voltar="Voltar"):
    """Mostra as opções numeradas e devolve o número escolhido (0 = voltar)."""
    print()
    for i, texto in enumerate(opcoes, 1):
        print(f"  {i}) {texto}")
    print(f"  0) {voltar}")
    while True:
        r = input("Sua escolha: ").strip()
        if r.isascii() and r.isdigit() and int(r) <= len(opcoes):
            return int(r)
        print("Digite só o número de uma das opções.")

# ---------- telas ----------

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
    input("\nAperte Enter para voltar. ")

# ---------- programa ----------

def main():
    dados = carregar()
    if not dados["nome"]:
        print("Bem-vindo(a) ao LEILA — aprenda a usar o celular com confiança!")
        dados["nome"] = input("Qual é o seu nome? ").strip() or "amigo(a)"
        salvar(dados)

    menu = [
        ("Usar o navegador (aula)", lambda: aula_navegador(dados)),
        ("Qual botão anexa uma foto? (quiz)", lambda: quiz(
            dados, "anexar", "Anexar uma foto",
            "Qual botão você tocaria para anexar uma foto numa mensagem?",
            ["Botão de carinha", "Clipe de papel", "Botão de câmera"], 2)),
        ("Evitar golpes (simulação)", lambda: quiz(
            dados, "golpe", "Você recebeu esta mensagem",
            "“Parabéns! Você ganhou um prêmio. Clique no link e informe sua senha.”\n"
            "O que você faria?",
            ["Clicaria no link para não perder o prêmio.",
             "Não clicaria. Verificaria no canal oficial.",
             "Encaminharia para outras pessoas."], 2)),
        ("Como fazer um Pix (aula)", lambda: pix(dados)),
        ("Glossário digital", glossario),
        ("Meu progresso", lambda: progresso(dados)),
    ]

    while True:
        print(f"\n===== LEILA · Olá, {dados['nome']}! =====")
        r = escolher([texto for texto, _ in menu], "Sair")
        if r == 0:
            break
        menu[r - 1][1]()
    print("Até logo! Seu progresso está salvo.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nAté logo!")