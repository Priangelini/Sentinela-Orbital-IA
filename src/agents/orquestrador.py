"""
Orquestrador Multiagente

Projeto:
Sentinela Orbital IA

Responsável por:
- Executar Agente de Risco
- Executar Agente Climático
- Executar Agente Visual com BLIP
- Executar Agente YOLO
- Executar Agente Relatório com OpenAI/RAG/fallback local
- Consolidar os resultados para terminal, dashboard e documentação
"""

from src.agents.agente_risco import executar_agente_risco
from src.agents.agente_clima import executar_agente_clima
from src.agents.agente_visual import executar_agente_visual
from src.agents.agente_yolo import executar_agente_yolo
from src.agents.agente_relatorio import executar_agente_relatorio


def gerar_recomendacao(risco_modelo, risco_visual, risco_yolo):
    """
    Gera recomendação base do orquestrador.
    """

    risco_modelo = str(risco_modelo).lower()
    risco_visual = str(risco_visual).lower()
    risco_yolo = str(risco_yolo).lower()

    if risco_modelo == "alto":
        return (
            "Monitoramento intensivo recomendado. "
            "Acionar equipes preventivas e manter acompanhamento contínuo."
        )

    if risco_modelo == "medio" and (
        risco_visual == "alto" or risco_yolo == "alto"
    ):
        return (
            "Condições climáticas moderadas, porém a análise visual indica "
            "atenção especial. Recomenda-se reforço no monitoramento."
        )

    if risco_modelo == "medio":
        return (
            "Monitoramento periódico recomendado, especialmente pela baixa "
            "ou ausência de precipitação observada no período."
        )

    if risco_visual == "alto" or risco_yolo == "alto":
        return (
            "Apesar do baixo risco climático, a análise visual indica possível "
            "anomalia. Recomenda-se verificação complementar."
        )

    return "Condições estáveis no momento."


def executar_orquestrador(municipio=None):
    """
    Executa todo o fluxo multiagente.

    Parâmetro:
    - municipio: opcional. Se informado, analisa o registro mais recente
      daquele município no dataset.
    """

    print("\nExecutando Agente de Risco...")
    resultado_risco = executar_agente_risco(municipio)
    print("OK")

    dados_entrada = resultado_risco["dados_entrada"]

    print("Executando Agente Climático...")
    resultado_clima = executar_agente_clima(dados_entrada)
    print("OK")

    data_analise = str(resultado_risco["data"])
    ano_mes_solicitado = data_analise[0:7]

    print("Executando Agente Visual...")
    resultado_visual = executar_agente_visual(
        municipio=resultado_risco["municipio"],
        estado=resultado_risco["estado"],
        ano_mes=ano_mes_solicitado
    )
    print("OK")

    print("Executando Agente YOLO...")
    resultado_yolo = executar_agente_yolo(
        resultado_visual.get("imagem")
    )
    print("OK")

    classe_prevista = resultado_risco["classe_prevista"]

    risco_visual = resultado_visual.get(
        "risco_visual",
        "indisponivel"
    )

    risco_yolo = resultado_yolo.get(
        "risco_yolo",
        "indisponivel"
    )

    recomendacao = gerar_recomendacao(
        classe_prevista,
        risco_visual,
        risco_yolo
    )

    resultado_final = {
        "sistema": "Sentinela Orbital IA",
        "status": "concluido",

        "municipio": resultado_risco["municipio"],
        "estado": resultado_risco["estado"],
        "bioma": resultado_risco["bioma"],
        "data": resultado_risco["data"],

        "ano_mes_solicitado": ano_mes_solicitado,
        "ano_mes_imagem": resultado_visual.get("ano_mes_imagem"),
        "tipo_correspondencia_imagem": resultado_visual.get(
            "tipo_correspondencia",
            "indisponivel"
        ),

        "classe_prevista": classe_prevista,
        "probabilidades": resultado_risco["probabilidades"],

        "analise_climatica": resultado_clima["analise_climatica"],

        "descricao_original_blip": resultado_visual.get(
            "descricao_original_blip",
            None
        ),
        "descricao_visual": resultado_visual.get(
            "descricao_visual",
            "Sem descrição visual disponível."
        ),
        "risco_visual": risco_visual,
        "imagem": resultado_visual.get("imagem"),

        "yolo": {
            "status": resultado_yolo.get("status"),
            "modelo": resultado_yolo.get("modelo"),
            "imagem_anotada": resultado_yolo.get("imagem_anotada"),
            "deteccoes": resultado_yolo.get("deteccoes", []),
            "resumo_deteccoes": resultado_yolo.get("resumo_deteccoes", {}),
            "total_deteccoes": resultado_yolo.get("total_deteccoes", 0),
            "risco_yolo": risco_yolo,
            "observacao": resultado_yolo.get("observacao")
        },

        "recomendacao": recomendacao
    }

    print("Executando Agente Relatório...")
    resultado_relatorio = executar_agente_relatorio(resultado_final)
    print("OK")

    resultado_final["agente_relatorio"] = {
        "status": resultado_relatorio.get("status"),
        "modelo": resultado_relatorio.get("modelo"),
        "rag_status": resultado_relatorio.get("rag_status"),
        "erro": resultado_relatorio.get("erro")
    }

    resultado_final["rag"] = {
        "status": resultado_relatorio.get(
            "rag_status",
            "indisponivel"
        ),
        "contexto_recuperado": resultado_relatorio.get(
            "contexto_rag",
            "Contexto RAG não disponível nesta execução."
        )
    }

    resultado_final["relatorio_executivo"] = resultado_relatorio["relatorio"]

    return resultado_final


if __name__ == "__main__":

    resultado = executar_orquestrador()

    print("\n")
    print("=" * 70)
    print("SENTINELA ORBITAL IA")
    print("=" * 70)

    print(f"Município: {resultado['municipio']}")
    print(f"Estado: {resultado['estado']}")
    print(f"Bioma: {resultado['bioma']}")
    print(f"Data: {resultado['data']}")

    print()
    print(f"Classe Prevista: {resultado['classe_prevista'].upper()}")

    print()
    print("Probabilidades:")
    for classe, valor in resultado["probabilidades"].items():
        print(f"{classe}: {valor:.2f}%")

    print()
    print("Análise Climática:")
    for alerta in resultado["analise_climatica"]:
        print(f"- {alerta}")

    print()
    print("Análise Visual Orbital - BLIP:")
    print(f"Período solicitado: {resultado['ano_mes_solicitado']}")
    print(f"Imagem utilizada: {resultado['ano_mes_imagem']}")
    print(f"Correspondência: {resultado['tipo_correspondencia_imagem'].upper()}")

    print()
    print("Descrição original BLIP:")
    print(resultado["descricao_original_blip"])

    print()
    print("Descrição Visual Interpretada:")
    print(resultado["descricao_visual"])

    print()
    print(f"Risco Visual BLIP: {resultado['risco_visual'].upper()}")

    print()
    print("Análise Visual - YOLO:")
    print(f"Status: {resultado['yolo']['status']}")
    print(f"Modelo: {resultado['yolo']['modelo']}")
    print(f"Total de detecções: {resultado['yolo']['total_deteccoes']}")
    print(f"Risco YOLO: {resultado['yolo']['risco_yolo'].upper()}")

    if resultado["yolo"]["deteccoes"]:
        print("Detecções:")
        for item in resultado["yolo"]["deteccoes"]:
            print(f"- {item['classe']}: {item['confianca']}%")
    else:
        print("Detecções: nenhuma")

    print()
    print("Observação YOLO:")
    print(resultado["yolo"]["observacao"])

    print()
    print("RAG:")
    print(f"Status: {resultado['rag']['status']}")

    print()
    print("Contexto RAG recuperado:")
    print(resultado["rag"]["contexto_recuperado"])

    print()
    print("Imagem analisada:")
    print(resultado["imagem"])

    print()
    print("Imagem anotada YOLO:")
    print(resultado["yolo"]["imagem_anotada"])

    print()
    print("Recomendação Base:")
    print(resultado["recomendacao"])

    print()
    print("=" * 70)
    print("RELATÓRIO EXECUTIVO GERADO")
    print("=" * 70)
    print(f"Modelo do relatório: {resultado['agente_relatorio']['modelo']}")
    print(f"Status: {resultado['agente_relatorio']['status']}")
    print(f"Status RAG: {resultado['agente_relatorio']['rag_status']}")

    if resultado["agente_relatorio"].get("erro"):
        print(f"Erro/Fallback: {resultado['agente_relatorio']['erro']}")

    print()
    print(resultado["relatorio_executivo"])