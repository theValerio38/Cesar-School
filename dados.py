import json
from pathlib import Path  

ARQUIVO = Path(__file__).with_name("leila_dados.json")

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
