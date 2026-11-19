import json
from pathlib import Path
from dados import carregar, salvar
from entrada import escolher
from telas import aula_navegador, quiz, pix, glossario, progresso
ARQUIVO = Path(__file__).with_name("leila_dados.json")



# ---------- programa ----------

def main():
    dados = carregar()
    if not dados["nome"]:
        print(" === Bem-vindo(a) ao LEILA\n Aprenda a usar o celular com confiança! === ")
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