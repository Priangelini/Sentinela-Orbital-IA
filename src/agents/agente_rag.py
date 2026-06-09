"""
Agente RAG - Base de Conhecimento

Projeto:
Sentinela Orbital IA

Responsável por:
- Ler documentos locais da base de conhecimento.
- Recuperar trechos relevantes conforme a classe de risco.
- Fornecer contexto adicional para o Agente Relatório.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

PASTA_BASE_CONHECIMENTO = (
    BASE_DIR
    / "docs"
    / "base_conhecimento"
)


def carregar_documentos():
    """
    Carrega todos os arquivos .txt da base de conhecimento.
    """

    textos = []

    if not PASTA_BASE_CONHECIMENTO.exists():
        return ""

    for arquivo in PASTA_BASE_CONHECIMENTO.glob("*.txt"):
        conteudo = arquivo.read_text(
            encoding="utf-8"
        )

        textos.append(
            f"ARQUIVO: {arquivo.name}\n{conteudo}"
        )

    return "\n\n".join(textos)


def recuperar_contexto(classe_risco):
    """
    Recupera trechos relevantes conforme a classe de risco.
    """

    base = carregar_documentos()

    if not base:
        return "Base de conhecimento não encontrada."

    classe = str(classe_risco).lower()

    palavras_chave = [
        classe,
        "governança",
        "boas práticas",
        "apoio à decisão"
    ]

    blocos = base.split("\n\n")

    trechos_relevantes = []

    for bloco in blocos:
        texto_bloco = bloco.lower()

        if any(palavra in texto_bloco for palavra in palavras_chave):
            trechos_relevantes.append(bloco)

    if not trechos_relevantes:
        trechos_relevantes.append(base)

    return "\n\n".join(
        trechos_relevantes[:5]
    )


def executar_agente_rag(classe_risco):
    """
    Executa o agente RAG.
    """

    contexto = recuperar_contexto(
        classe_risco
    )

    return {
        "agente": "Agente RAG",
        "status": "sucesso",
        "classe_risco": classe_risco,
        "contexto_recuperado": contexto
    }


if __name__ == "__main__":
    resultado = executar_agente_rag("medio")

    print("=" * 60)
    print("AGENTE RAG")
    print("=" * 60)
    print(resultado["contexto_recuperado"])