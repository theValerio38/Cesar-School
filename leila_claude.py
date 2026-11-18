#!/usr/bin/env python3
"""LEILA — Letramento e Cidadania (versão de terminal)

Versão em texto do protótipo navegável do Figma. Usa só a biblioteca
padrão do Python. Os dados (nome, ajustes, trilhas e progresso) ficam
salvos em "leila_dados.json", na mesma pasta deste arquivo.

Como usar:
    python leila.py            abre o programa
    python leila.py --reset    apaga os dados salvos e recomeça do zero

Dentro do programa, digite o número da opção e aperte Enter.
Atalhos: M = menu principal, A = falar com a LEILA, S = sair.
"""

import json
import os
import sys
import textwrap
import unicodedata
from pathlib import Path

ARQUIVO_DADOS = Path(__file__).resolve().with_name("leila_dados.json")
LARGURA = 66

# ---------------------------------------------------------------------------
# Conteúdo (vem do protótipo do Figma)
# ---------------------------------------------------------------------------

TRILHAS = [
    {"id": "basics", "titulo": "Usar o celular", "curta": "Celular e internet",
     "descricao": "Aprenda a navegar na internet e usar aplicativos.",
     "tela": "aula_navegador"},
    {"id": "messages", "titulo": "Mensagens e fotos", "curta": "Conversar e compartilhar",
     "descricao": "Aprenda a conversar, enviar fotos e arquivos.",
     "tela": "aula_navegador"},
    {"id": "services", "titulo": "Serviços na internet", "curta": "Resolver tarefas online",
     "descricao": "Aprenda a acessar serviços e preencher informações.",
     "tela": "aula_navegador"},
    {"id": "security", "titulo": "Segurança digital", "curta": "Evitar golpes",
     "descricao": "Aprenda a proteger suas contas e reconhecer golpes.",
     "tela": "seguranca"},
    {"id": "work", "titulo": "Ferramentas de trabalho", "curta": "Documentos e planilhas",
     "descricao": "Aprenda a escrever documentos, criar planilhas e compartilhar arquivos.",
     "tela": "trilha_trabalho"},
]
IDS_TRILHAS = {t["id"] for t in TRILHAS}

# Atividades que contam para o progresso (as que têm conteúdo no protótipo).
ATIVIDADES = {
    "navegador": "Usar o navegador",
    "anexar_quiz": "Quiz: anexar uma foto",
    "desafio_mensagem": "Desafio: enviar uma mensagem",
    "golpes": "Simulação: golpes e fraudes",
    "pix": "Como fazer um Pix",
    "documento": "Criar um documento",
}

# (título, descrição, tela). Tela None = ainda sem conteúdo no protótipo.
AULAS_TRABALHO = [
    ("Criar um documento", "Aprenda a abrir, escrever e salvar", "aula_documento"),
    ("Corrigir e organizar um texto", "Título, parágrafo e correção", None),
    ("Criar uma planilha simples", "Linhas, colunas e informações", None),
    ("Organizar uma lista de gastos", "Valores e contas simples", None),
    ("Compartilhar um arquivo", "Envie seu trabalho com segurança", None),
]

# No protótipo qualquer resposta avança. Aqui há uma resposta certa em cada
# pergunta (número da opção, começando em 0). Troque aqui se precisar.
QUIZ_OPCOES = ["Botão de carinha", "Clipe de papel", "Botão de câmera"]
QUIZ_CERTA = 1
DESAFIO_OPCOES = ["O primeiro ícone (📎)", "O segundo ícone (▣)"]
DESAFIO_CERTA = 0
GOLPE_OPCOES = [
    ("Clicaria no link para não perder o prêmio.",
     "Cuidado! Links assim servem para roubar sua senha. Pense de novo."),
    ("Não clicaria. Iria verificar a oferta no canal oficial.", None),
    ("Encaminharia para outras pessoas.",
     "Encaminhar espalha o golpe e coloca outras pessoas em risco. Pense de novo."),
]
GOLPE_CERTA = 1

PIX_PASSOS = [
    ("Abra a área Pix",
     "No aplicativo oficial do seu banco, procure a opção “Pix” e toque em “Transferir”.",
     "Pix → Transferir"),
    ("Informe a chave",
     "Digite a chave Pix de quem vai receber: telefone, e-mail, CPF ou chave aleatória.",
     "Chave: (11) 99999-0000"),
    ("Digite o valor",
     "Informe quanto deseja enviar. Você pode adicionar uma descrição para lembrar do pagamento.",
     "Valor: R$ 25,00"),
    ("Confira e confirme",
     "Verifique o nome, o banco e o valor. Só então confirme usando sua senha ou biometria.",
     "Ana Silva · R$ 25,00"),
]

TERMOS = [
    {"termo": "Aplicativo", "simples": "Um programa que você usa no celular.",
     "exemplo": "WhatsApp, banco e câmera são exemplos de aplicativos."},
    {"termo": "Wi-Fi", "simples": "Uma conexão com a internet sem usar fios.",
     "exemplo": "Em casa, procure o nome da sua rede Wi-Fi e digite a senha."},
    {"termo": "Link", "simples": "Um texto ou botão que leva você para outra página.",
     "exemplo": "Toque em links apenas quando confiar em quem enviou."},
    {"termo": "Senha", "simples": "Um código secreto que protege sua conta.",
     "exemplo": "Use uma senha diferente para cada conta e não conte para ninguém."},
    {"termo": "Pix", "simples": "Uma forma de enviar e receber dinheiro pelo banco.",
     "exemplo": "Antes de confirmar, confira sempre o nome e o valor."},
    {"termo": "QR Code", "simples": "Um quadrado com desenho que a câmera do celular consegue ler.",
     "exemplo": "Ele pode abrir um site, um cardápio ou um pagamento."},
    {"termo": "Navegador", "simples": "O aplicativo usado para visitar sites na internet.",
     "exemplo": "Google Chrome, Safari e Firefox são navegadores."},
    {"termo": "Golpe digital", "simples": "Uma tentativa de enganar alguém pela internet ou celular.",
     "exemplo": "Desconfie de prêmios, ameaças e pedidos com muita pressa."},
]

RESPOSTA_INICIAL = "Posso explicar uma aula, ajudar na navegação ou dar dicas de segurança."
PERGUNTAS_LEILA = [
    ("Como usar a plataforma?",
     "Use o menu (tecle M) para escolher entre aulas, segurança e seu progresso. "
     "Posso acompanhar você em cada passo."),
    ("Quero uma dica de segurança",
     "Nunca compartilhe senhas e desconfie de mensagens que pedem urgência ou prometem prêmios."),
    ("Não entendi uma atividade",
     "Sem problema! Leia novamente com calma e procure as partes destacadas. "
     "Você também pode tentar outra vez."),
]


# ---------------------------------------------------------------------------
# Dados salvos
# ---------------------------------------------------------------------------

def dados_iniciais() -> dict:
    return {
        "versao": 1,
        "nome": "",
        "onboarding_concluido": False,
        "letras_grandes": False,
        "ouvir_instrucoes": True,
        "trilhas": [],
        "concluidas": [],
    }


def carregar() -> dict:
    dados = dados_iniciais()
    if not ARQUIVO_DADOS.exists():
        return dados
    try:
        lidos = json.loads(ARQUIVO_DADOS.read_text(encoding="utf-8"))
        if not isinstance(lidos, dict):
            raise ValueError("formato inesperado")
    except (OSError, ValueError):
        copia = ARQUIVO_DADOS.with_suffix(".json.bak")
        try:
            ARQUIVO_DADOS.replace(copia)
            print(f"Os dados salvos estavam com problema. Guardei uma cópia em {copia.name}.")
        except OSError:
            pass
        return dados
    for chave, padrao in dados.items():
        if chave in lidos and type(lidos[chave]) is type(padrao):
            dados[chave] = lidos[chave]
    dados["trilhas"] = list(dict.fromkeys(t for t in dados["trilhas"] if t in IDS_TRILHAS))
    dados["concluidas"] = list(dict.fromkeys(a for a in dados["concluidas"] if a in ATIVIDADES))
    return dados


def salvar(dados: dict) -> None:
    temporario = ARQUIVO_DADOS.with_suffix(".tmp")
    try:
        temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(ARQUIVO_DADOS)
    except OSError as erro:
        print(f"Não consegui salvar seus dados: {erro}")


def sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in base if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Programa
# ---------------------------------------------------------------------------

class Sair(Exception):
    """O usuário pediu para sair."""


class IrPara(Exception):
    """Troca de tela imediatamente (usado pelo atalho M)."""

    def __init__(self, tela: str):
        super().__init__(tela)
        self.tela = tela


class App:
    def __init__(self) -> None:
        self.dados = carregar()
        self.ultima: str | None = None
        self.pix_passo = 0
        self.telas = {
            "boas_vindas": self.tela_boas_vindas,
            "acessibilidade": self.tela_acessibilidade,
            "nome": self.tela_nome,
            "trilhas": self.tela_trilhas,
            "inicio": self.tela_inicio,
            "menu": self.tela_menu,
            "aprender": self.tela_aprender,
            "trilha_trabalho": self.tela_trilha_trabalho,
            "aula_documento": self.tela_aula_documento,
            "aula_navegador": self.tela_aula_navegador,
            "quiz": self.tela_quiz,
            "resultado": self.tela_resultado,
            "seguranca": self.tela_seguranca,
            "golpe": self.tela_golpe,
            "seguro": self.tela_seguro,
            "simulacoes": self.tela_simulacoes,
            "bancos": self.tela_bancos,
            "pix": self.tela_pix,
            "desafio": self.tela_desafio,
            "progresso": self.tela_progresso,
            "ajuda": self.tela_ajuda,
            "glossario": self.tela_glossario,
            "ajustes": self.tela_ajustes,
        }

    # ----- dados ----------------------------------------------------------

    def salvar(self) -> None:
        salvar(self.dados)

    def concluir(self, chave: str) -> None:
        if chave not in self.dados["concluidas"]:
            self.dados["concluidas"].append(chave)
            self.salvar()

    @property
    def feitas(self) -> int:
        return len(self.dados["concluidas"])

    @property
    def percentual(self) -> int:
        return round(100 * self.feitas / len(ATIVIDADES))

    @property
    def primeiro_nome(self) -> str:
        partes = self.dados["nome"].split()
        return partes[0] if partes else ""

    # ----- texto na tela --------------------------------------------------

    def g(self, texto: str) -> str:
        """Títulos em 'letras grandes': maiúsculas e espaçadas."""
        if not self.dados["letras_grandes"]:
            return texto
        return "   ".join(" ".join(palavra) for palavra in texto.upper().split())

    def limpar(self) -> None:
        if sys.stdout.isatty():
            print("\033[2J\033[H", end="")
        else:
            print("\n" + "=" * LARGURA)

    def marca(self, app: bool = True) -> None:
        print("═" * LARGURA)
        print("LEILA — Letramento e Cidadania" + ("   ·   APRENDA NO SEU RITMO" if app else ""))
        print("═" * LARGURA)

    def titulo(self, texto: str) -> None:
        print(textwrap.fill(self.g(texto), LARGURA))
        print()

    def p(self, texto: str, recuo: str = "") -> None:
        print(textwrap.fill(texto, LARGURA, initial_indent=recuo, subsequent_indent=recuo))
        if self.dados["letras_grandes"]:
            print()

    def cabecalho(self, sobre: str, titulo: str, subtitulo: str = "", app: bool = True) -> None:
        self.limpar()
        self.marca(app)
        print()
        print(f"[ {sobre} ]")
        print()
        self.titulo(titulo)
        if subtitulo:
            self.p(subtitulo)
            print()

    def caixa(self, linhas: list[str]) -> None:
        interior = LARGURA - 6
        corpo: list[str] = []
        for linha in linhas:
            corpo.extend(textwrap.wrap(linha, interior) or [""])
        print("  ┌" + "─" * (interior + 2) + "┐")
        for linha in corpo:
            print("  │ " + linha.ljust(interior) + " │")
        print("  └" + "─" * (interior + 2) + "┘")

    def linha_mensagem(self, texto: str, icones: str) -> None:
        espaco = max(2, LARGURA - 8 - len(texto) - len(icones))
        print("  " + "─" * (LARGURA - 4))
        print("   " + texto + " " * espaco + icones)
        print("  " + "─" * (LARGURA - 4))

    def barra(self, parte: int, total: int, largura: int = 24) -> str:
        cheio = round(largura * parte / total) if total else 0
        return "█" * cheio + "░" * (largura - cheio)

    def situacao(self, chave: str) -> str:
        return "LIGADO" if self.dados[chave] else "desligado"

    # ----- entrada --------------------------------------------------------

    def ler(self, texto: str) -> str:
        try:
            return input(texto)
        except (EOFError, KeyboardInterrupt):
            print()
            raise Sair

    def pausa(self) -> None:
        self.ler("\nAperte Enter para continuar. ")

    def em_breve(self) -> None:
        print()
        self.p("Esta parte ainda não está pronta. Volte em breve!")
        self.pausa()

    def tecla_global(self, resposta: str, menu: bool = True, assistente: bool = True) -> bool:
        """Trata S, M e A. Devolve True se a tecla foi tratada."""
        tecla = resposta.strip().lower()
        if tecla == "s":
            raise Sair
        if tecla == "m" and menu:
            raise IrPara("menu")
        if tecla == "a" and assistente:
            self.assistente()
            return True
        return False

    def mostrar_opcoes(self, opcoes: list[str], voltar: str | None,
                       menu: bool, assistente: bool) -> None:
        print()
        for n, texto in enumerate(opcoes, 1):
            print(textwrap.fill(f"{n}) {texto}", LARGURA,
                                initial_indent="  ", subsequent_indent="     "))
            if self.dados["letras_grandes"]:
                print()
        if voltar:
            print(f"  0) {voltar}")
        atalhos = []
        if menu:
            atalhos.append("M = menu principal")
        if assistente:
            atalhos.append("A = falar com a LEILA")
        atalhos.append("S = sair")
        print()
        print("  " + "   ·   ".join(atalhos))
        print()

    def escolher(self, opcoes: list[str], voltar: str | None = None,
                 menu: bool = True, assistente: bool = True) -> int:
        """Mostra opções numeradas. Devolve o índice (0 = primeira) ou -1 para 'voltar'."""
        mostrar = True
        while True:
            if mostrar:
                self.mostrar_opcoes(opcoes, voltar, menu, assistente)
                mostrar = False
            resposta = self.ler("Sua escolha: ").strip()
            if self.tecla_global(resposta, menu, assistente):
                mostrar = True
                continue
            if resposta.isascii() and resposta.isdigit():
                n = int(resposta)
                if voltar and n == 0:
                    return -1
                if 1 <= n <= len(opcoes):
                    return n - 1
            print("Não entendi. Digite só o número de uma das opções.")

    # ----- assistente -----------------------------------------------------

    def assistente(self) -> None:
        resposta = RESPOSTA_INICIAL
        while True:
            print()
            self.caixa(["LEILA · Assistente virtual", "",
                        "Olá! Eu sou a LEILA, sua parceira de letramento digital.", "",
                        resposta])
            i = self.escolher([pergunta for pergunta, _ in PERGUNTAS_LEILA],
                              voltar="Fechar assistente", menu=False, assistente=False)
            if i == -1:
                return
            resposta = PERGUNTAS_LEILA[i][1]

    # ----- executar -------------------------------------------------------

    def executar(self) -> None:
        tela = "inicio" if self.dados["onboarding_concluido"] else "boas_vindas"
        while True:
            try:
                proxima = self.telas[tela]()
            except IrPara as destino:
                proxima = destino.tela
            if tela != "menu":
                self.ultima = tela
            tela = proxima

    # ----- primeiros passos -----------------------------------------------

    def tela_boas_vindas(self) -> str:
        self.limpar()
        self.marca(app=False)
        print()
        print("[ FÁCIL E PASSO A PASSO ]")
        print()
        self.titulo("Aprenda a usar o celular com confiança.")
        self.p("Vamos aprender juntos. Você pode repetir cada aula quantas vezes quiser.")
        self.escolher(["Começar"], menu=False)
        return "acessibilidade"

    def _ajustes(self, onboarding: bool) -> None:
        while True:
            if onboarding:
                self.cabecalho("1 DE 3", "Como fica melhor para você?",
                               "Escolha como quer usar o aplicativo. Você pode mudar depois.",
                               app=False)
            else:
                self.cabecalho("AJUSTES", "Como fica melhor para você?",
                               "Escolha como quer usar o aplicativo.")
            print(f"  Letras grandes ......... {self.situacao('letras_grandes')}")
            print(f"  Ouvir as instruções .... {self.situacao('ouvir_instrucoes')}")
            print()
            self.p("Obs.: no terminal as instruções não são faladas; "
                   "sua escolha fica guardada.")
            opcoes = ["Ligar ou desligar “Letras grandes”",
                      "Ligar ou desligar “Ouvir as instruções”"]
            if onboarding:
                i = self.escolher(opcoes + ["Continuar", "Pular essa parte"], menu=False)
                if i >= 2:
                    return
            else:
                i = self.escolher(opcoes, voltar="Voltar")
                if i == -1:
                    return
            chave = "letras_grandes" if i == 0 else "ouvir_instrucoes"
            self.dados[chave] = not self.dados[chave]
            self.salvar()

    def tela_acessibilidade(self) -> str:
        self._ajustes(onboarding=True)
        return "nome"

    def tela_ajustes(self) -> str:
        self._ajustes(onboarding=False)
        return "ajuda"

    def tela_nome(self) -> str:
        while True:
            self.cabecalho("2 DE 3", "Escreva seu nome", "Digite seu nome e aperte Enter.",
                           app=False)
            self.p("Seu nome fica guardado só neste computador, no arquivo "
                   f"{ARQUIVO_DADOS.name}.")
            print()
            nome = " ".join(self.ler("Seu nome: ").split())[:60]
            while not nome:
                print("Precisamos do seu nome para continuar. Tente de novo.")
                nome = " ".join(self.ler("Seu nome: ").split())[:60]
            print()
            print("Você se chama:")
            print()
            print("    " + self.g(nome))
            print()
            print("Está certo?")
            if self.escolher(["Sim", "Não"], menu=False) == 0:
                self.dados["nome"] = nome
                self.salvar()
                return "trilhas"

    def tela_trilhas(self) -> str:
        escolhidas: list[str] = []
        for numero, trilha in enumerate(TRILHAS, 1):
            self.cabecalho(f"3 DE 3  ·  {numero} de {len(TRILHAS)}", trilha["titulo"],
                           app=False)
            print("TRILHA DE APRENDIZADO")
            print()
            self.p(trilha["descricao"])
            print()
            print("Você quer aprender isso?")
            if self.escolher(["Sim", "Não"], menu=False) == 0:
                escolhidas.append(trilha["id"])
        self.dados["trilhas"] = escolhidas
        self.dados["onboarding_concluido"] = True
        self.salvar()

        self.cabecalho("PRONTO", "Suas trilhas estão prontas!", app=False)
        if escolhidas:
            self.p("Estas trilhas aparecerão na área Aprender:")
            for trilha in TRILHAS:
                if trilha["id"] in escolhidas:
                    print(f"  ✓ {trilha['titulo']}")
        else:
            self.p("Você poderá escolher uma trilha quando quiser.")
        self.escolher(["Entrar no aplicativo"], menu=False)
        return "inicio"

    # ----- navegação principal --------------------------------------------

    def tela_inicio(self) -> str:
        sobre = f"OLÁ, {self.primeiro_nome.upper()}" if self.primeiro_nome else "OLÁ"
        self.cabecalho(sobre, "O que você quer aprender?",
                       "Escolha uma opção abaixo. Vamos explicar tudo com calma.")
        total = len(ATIVIDADES)
        print(f"Você já concluiu {self.feitas} de {total} aulas")
        print(f"[{self.barra(self.feitas, total)}] {self.percentual}%")
        i = self.escolher([
            "Usar o celular — Aprenda internet, mensagens e aplicativos.",
            "Evitar golpes — Aprenda a reconhecer perigos e proteger seus dados.",
            "Praticar tarefas — Treine Pix, mensagens e pesquisas sem medo de errar.",
        ])
        return ["aprender", "seguranca", "simulacoes"][i]

    def tela_menu(self) -> str:
        self.cabecalho("MENU PRINCIPAL", "Para onde você quer ir?")
        self.p("Precisa de ajuda? Estamos aqui para você. Tecle A para falar com a LEILA.")
        destinos = ["inicio", "aprender", "seguranca", "progresso", "ajuda"]
        i = self.escolher(["Página inicial", "Aprender", "Ficar seguro",
                           "Meu progresso", "Pedir ajuda"], voltar="Voltar", menu=False)
        if i == -1:
            return self.ultima or "inicio"
        return destinos[i]

    def tela_aprender(self) -> str:
        self.cabecalho("SUAS TRILHAS", "O que vamos aprender?",
                       "Escolha uma trilha para ver as aulas.")
        disponiveis = [t for t in TRILHAS if t["id"] in self.dados["trilhas"]]
        if not disponiveis:
            print("Nenhuma trilha escolhida")
            self.p("Responda novamente para escolher o que quer aprender.")
            i = self.escolher(["Escolher trilhas"], voltar="Voltar")
            return "inicio" if i == -1 else "trilhas"
        i = self.escolher([f"{t['titulo']} — {t['curta']}" for t in disponiveis],
                          voltar="Voltar")
        return "inicio" if i == -1 else disponiveis[i]["tela"]

    # ----- ferramentas de trabalho ----------------------------------------

    def tela_trilha_trabalho(self) -> str:
        self.cabecalho("FERRAMENTAS DE TRABALHO", "Documentos e planilhas",
                       "Aprenda tarefas úteis para estudar e trabalhar.")
        feitas = 1 if "documento" in self.dados["concluidas"] else 0
        print(f"{feitas} de {len(AULAS_TRABALHO)} aulas concluídas")
        self.p("Comece pela primeira aula e avance no seu ritmo.")
        opcoes = []
        for titulo, meta, tela in AULAS_TRABALHO:
            feito = "✓ " if tela == "aula_documento" and feitas else ""
            breve = "" if tela else " (em breve)"
            opcoes.append(f"{feito}{titulo} — {meta}{breve}")
        i = self.escolher(opcoes, voltar="Voltar")
        if i == -1:
            return "aprender"
        destino = AULAS_TRABALHO[i][2]
        if destino:
            return destino
        self.em_breve()
        return "trilha_trabalho"

    def tela_aula_documento(self) -> str:
        self.cabecalho("AULA 1 · FERRAMENTAS DE TRABALHO", "Criar um documento",
                       "Vamos escrever e salvar um texto simples.")
        nome = self.primeiro_nome or "Maria"
        self.caixa(["B    A    ☰", "",
                    "Minha apresentação",
                    f"Meu nome é {nome} e estou aprendendo a usar documentos."])
        print()
        print("(1) Toque na página branca")
        self.p("Quando a linha aparecer, você já pode começar a escrever.", "    ")
        i = self.escolher(["Concluir aula"], voltar="Voltar")
        if i == 0:
            self.concluir("documento")
        return "trilha_trabalho"

    # ----- aula e atividades ----------------------------------------------

    def tela_aula_navegador(self) -> str:
        self.cabecalho("AULA · PASSO 2 DE 6", "Usar o navegador",
                       "Vamos aprender juntos, passo a passo.")
        self.caixa(["● ● ●", "", "[ Pesquisar no Google ]"])
        print()
        print("(1) Toque na barra de pesquisa")
        self.p("É aqui que você digita o que deseja encontrar na internet.", "    ")
        i = self.escolher(["Próximo"], voltar="Voltar")
        if i == -1:
            return "aprender"
        self.concluir("navegador")
        return "quiz"

    def tela_quiz(self) -> str:
        self.cabecalho("VAMOS PRATICAR", "Qual botão você tocaria?",
                       "Para anexar uma foto ao enviar uma mensagem.")
        self.linha_mensagem("Escreva uma mensagem...", "📎  ▣")
        while True:
            i = self.escolher(QUIZ_OPCOES, voltar="Voltar")
            if i == -1:
                return "aula_navegador"
            if i == QUIZ_CERTA:
                self.concluir("anexar_quiz")
                return "resultado"
            print()
            self.p("Quase! Esse botão não é o de anexar. Tente de novo.")

    def tela_desafio(self) -> str:
        self.cabecalho("DESAFIO · PASSO 1 DE 3", "Enviar uma mensagem",
                       "Encontre o ícone para anexar uma foto.")
        self.linha_mensagem("Digite uma mensagem...", "📎  ▣")
        while True:
            i = self.escolher(DESAFIO_OPCOES, voltar="Voltar")
            if i == -1:
                return "simulacoes"
            if i == DESAFIO_CERTA:
                self.concluir("desafio_mensagem")
                return "resultado"
            print()
            self.p("Quase! Esse ícone não é o de anexar. Tente de novo.")

    def tela_resultado(self) -> str:
        self.cabecalho("ATIVIDADE CONCLUÍDA", "Parabéns!",
                       "Você encontrou o botão correto. Agora já sabe como anexar "
                       "fotos nas mensagens.")
        print("  ✓")
        i = self.escolher(["Próxima atividade", "Ver explicação"])
        return "simulacoes" if i == 0 else "aula_navegador"

    # ----- segurança ------------------------------------------------------

    def tela_seguranca(self) -> str:
        self.cabecalho("PROTEJA-SE ONLINE", "Segurança na internet",
                       "Aprenda a identificar riscos e navegar com confiança.")
        i = self.escolher([
            "Golpes e fraudes — Saiba como identificar e evitar",
            "Senhas seguras — Proteja seus dados",
            "Privacidade — Cuide das suas informações",
        ], voltar="Voltar")
        return "inicio" if i == -1 else "golpe"

    def tela_golpe(self) -> str:
        self.cabecalho("SIMULAÇÃO DE SEGURANÇA", "Você recebeu esta mensagem",
                       "Leia com atenção e escolha o que faria.")
        self.caixa(["“Parabéns! Você ganhou um prêmio. Clique no link e informe sua "
                    "senha bancária em até 10 minutos.”"])
        while True:
            i = self.escolher([texto for texto, _ in GOLPE_OPCOES], voltar="Voltar")
            if i == -1:
                return "seguranca"
            if i == GOLPE_CERTA:
                self.concluir("golpes")
                return "seguro"
            print()
            self.p(GOLPE_OPCOES[i][1])

    def tela_seguro(self) -> str:
        self.cabecalho("ATIVIDADE CONCLUÍDA", "Muito bem!",
                       "Essa é a opção mais segura. Nunca clique em links de "
                       "remetentes desconhecidos.")
        print("Sinais de alerta:")
        for sinal in ["Promessas de prêmios", "Prazos muito curtos",
                      "Links suspeitos", "Pedido de dados pessoais"]:
            print(f"  • {sinal}")
        self.escolher(["Continuar aprendendo"])
        return "seguranca"

    # ----- simulações -----------------------------------------------------

    def tela_simulacoes(self) -> str:
        self.cabecalho("APRENDA FAZENDO", "Simulações do cotidiano",
                       "Escolha um cenário para praticar.")
        i = self.escolher(["Enviar uma mensagem", "Fazer uma pesquisa",
                           "Bancos e segurança", "Serviços públicos"], voltar="Voltar")
        if i == -1:
            return "inicio"
        return ["desafio", "aula_navegador", "bancos", "aula_navegador"][i]

    def tela_bancos(self) -> str:
        self.cabecalho("DINHEIRO E SEGURANÇA", "Bancos e segurança",
                       "Aprenda a usar serviços bancários digitais com mais confiança.")
        i = self.escolher([
            "Como fazer um Pix — Transfira dinheiro passo a passo",
            "Evitar golpes bancários — Reconheça mensagens e pedidos suspeitos",
            "Proteger sua conta — Cuidados com senhas e acessos",
        ], voltar="Voltar")
        if i == -1:
            return "simulacoes"
        if i == 0:
            self.pix_passo = 0
        return ["pix", "golpe", "seguranca"][i]

    def tela_pix(self) -> str:
        passo = self.pix_passo
        ultimo = passo == len(PIX_PASSOS) - 1
        titulo, texto, demo = PIX_PASSOS[passo]
        self.cabecalho(f"PIX · PASSO {passo + 1} DE {len(PIX_PASSOS)}", "Como fazer um Pix",
                       "Aprenda a transferir dinheiro com atenção e segurança.")
        for n, (nome, _, _) in enumerate(PIX_PASSOS):
            if n < passo:
                sinal, estado = "✓", "Concluído"
            elif n == passo:
                sinal, estado = "▶", "Você está aqui"
            else:
                sinal, estado = "○", "Próximo passo"
            print(f"  {sinal} {n + 1}. {nome} — {estado}")
        print()
        print(self.g(titulo))
        self.p(texto)
        print()
        linhas = ["Banco LEILA", demo]
        if ultimo:
            linhas.append("✓ Dados conferidos")
        self.caixa(linhas)
        print()
        print("ANTES DE CONFIRMAR")
        self.p("Nunca faça um Pix com pressa. Confira o nome completo do destinatário "
               "e desconfie de pedidos urgentes.")
        i = self.escolher(["Concluir aula" if ultimo else "Próximo passo"],
                          voltar="Voltar" if passo else "Sair")
        if i == -1:
            if passo:
                self.pix_passo -= 1
                return "pix"
            return "simulacoes"
        if ultimo:
            self.concluir("pix")
            return "simulacoes"
        self.pix_passo += 1
        return "pix"

    # ----- progresso e ajuda ----------------------------------------------

    def tela_progresso(self) -> str:
        self.cabecalho("SUA JORNADA", "Meu progresso", "Veja tudo o que você já conquistou.")
        total = len(ATIVIDADES)
        feitas = self.dados["concluidas"]
        print(f"{self.percentual}%   [{self.barra(len(feitas), total)}]")
        print(self.g(f"{len(feitas)} de {total} atividades"))
        if not feitas:
            self.p("Vamos começar? Faça sua primeira atividade.")
        elif len(feitas) == total:
            self.p("Você concluiu tudo. Parabéns!")
        else:
            self.p("Você está indo muito bem. Continue assim!")
        print()
        print("Suas atividades")
        for chave, nome in ATIVIDADES.items():
            print(f"  {'✓' if chave in feitas else '○'} {nome}")
        print()
        print("Suas conquistas")
        conquistas = []
        if feitas:
            conquistas.append("Primeiros passos")
        if "golpes" in feitas:
            conquistas.append("Mais segurança")
        if conquistas:
            for conquista in conquistas:
                print(f"  ★ {conquista}")
        else:
            print("  Conclua uma atividade para ganhar sua primeira conquista.")
        i = self.escolher(["Continuar aprendendo"], voltar="Voltar")
        return "inicio" if i == -1 else "aprender"

    def tela_ajuda(self) -> str:
        self.cabecalho("ESTAMOS AQUI PARA VOCÊ", "Central de ajuda",
                       "Encontre respostas ou fale com a nossa equipe.")
        i = self.escolher([
            "Perguntas frequentes — Respostas para as dúvidas mais comuns (em breve)",
            "Glossário digital — Entenda os termos mais usados",
            "Fale conosco — Suporte e orientações (em breve)",
            "Ajustes — Letras grandes e instruções",
        ], voltar="Voltar")
        if i == -1:
            return "inicio"
        if i == 1:
            return "glossario"
        if i == 3:
            return "ajustes"
        self.em_breve()
        return "ajuda"

    def tela_glossario(self) -> str:
        consulta = ""
        while True:
            self.cabecalho("PALAVRAS DA TECNOLOGIA", "Glossário digital",
                           "Pesquise uma palavra para entender o significado.")
            busca = sem_acento(consulta)
            achados = [t for t in TERMOS
                       if busca in sem_acento(f"{t['termo']} {t['simples']}")]
            n = len(achados)
            frase = "palavra encontrada" if n == 1 else "palavras encontradas"
            print(f"{n} {frase}" + (f" para “{consulta}”" if consulta else ""))
            print()
            for termo in achados:
                print(f"  {termo['termo'][0]} — {termo['termo']}")
                self.p(termo["simples"], "      ")
                self.p("Exemplo: " + termo["exemplo"], "      ")
                print()
            if not achados:
                print("Palavra não encontrada")
                self.p("Tente escrever de outra forma ou peça ajuda para a LEILA (tecle A).")
                print()
            print("Digite uma palavra para pesquisar. Enter mostra todas. 0 volta.")
            print("Atalhos: M = menu principal   A = falar com a LEILA   S = sair")
            resposta = self.ler("Pesquisar: ").strip()
            if resposta == "0":
                return "ajuda"
            if self.tecla_global(resposta):
                continue
            consulta = resposta


# ---------------------------------------------------------------------------
# Início do programa
# ---------------------------------------------------------------------------

def resetar() -> int:
    if not ARQUIVO_DADOS.exists():
        print("Não há dados salvos para apagar.")
        return 0
    try:
        resposta = input("Apagar todos os dados salvos? Digite “sim” para confirmar: ")
    except (EOFError, KeyboardInterrupt):
        print()
        return 1
    if resposta.strip().lower() == "sim":
        ARQUIVO_DADOS.unlink()
        print("Dados apagados.")
    else:
        print("Nada foi apagado.")
    return 0


def main() -> int:
    argumentos = sys.argv[1:]
    if argumentos and argumentos[0] in ("-h", "--help", "--ajuda"):
        print(__doc__)
        return 0
    if "--reset" in argumentos:
        return resetar()

    if os.name == "nt":
        os.system("")  # liga as cores/ANSI no console do Windows 10+
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

    app = App()
    try:
        app.executar()
    except Sair:
        pass
    finally:
        app.salvar()
    print(f"\nAté logo! Seu progresso está salvo em:\n{ARQUIVO_DADOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
