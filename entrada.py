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