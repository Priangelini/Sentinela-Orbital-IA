"""
Agente Relatório - OpenAI + RAG + fallback local

Projeto:
Sentinela Orbital IA

Responsável por:
- Receber o resultado consolidado do Orquestrador.
- Consultar a base de conhecimento local via Agente RAG.
- Gerar um relatório executivo em linguagem natural.
- Usar OpenAI quando disponível.
- Usar fallback local se a API falhar.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.agents.agente_rag import executar_agente_rag


BASE_DIR = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = BASE_DIR / ".env"

load_dotenv(ARQUIVO_ENV)


def gerar_relatorio_local(resultado, contexto_rag):
    """
    Fallback local caso a API OpenAI não esteja disponível.
    """

    alertas = "\n".join(
        f"- {item}" for item in resultado["analise_climatica"]
    )

    return f"""
RELATÓRIO EXECUTIVO AMBIENTAL - SENTINELA ORBITAL IA

Município analisado: {resultado["municipio"]} - {resultado["estado"]}
Bioma: {resultado["bioma"]}
Data da análise: {resultado["data"]}

O modelo preditivo XGBoost classificou o risco de incêndio como {resultado["classe_prevista"].upper()}.

Probabilidades calculadas:
- Alto: {resultado["probabilidades"].get("alto", 0):.2f}%
- Médio: {resultado["probabilidades"].get("medio", 0):.2f}%
- Baixo: {resultado["probabilidades"].get("baixo", 0):.2f}%

Análise climática:
{alertas}

Análise visual orbital:
A imagem solicitada corresponde ao período {resultado["ano_mes_solicitado"]}.
A imagem utilizada foi do período {resultado["ano_mes_imagem"]}, com correspondência {resultado["tipo_correspondencia_imagem"]}.
Descrição original do BLIP: {resultado["descricao_original_blip"]}
Descrição visual interpretada: {resultado["descricao_visual"]}
Risco visual BLIP: {resultado["risco_visual"].upper()}

Análise YOLO:
Modelo: {resultado["yolo"]["modelo"]}
Total de detecções: {resultado["yolo"]["total_deteccoes"]}
Risco YOLO: {resultado["yolo"]["risco_yolo"].upper()}
Observação: {resultado["yolo"]["observacao"]}

Contexto recuperado da base de conhecimento:
{contexto_rag}

Recomendação:
{resultado["recomendacao"]}
""".strip()


def montar_prompt(resultado, contexto_rag):
    """
    Monta o prompt enviado ao modelo generativo com contexto RAG.
    """

    return f"""
Você é um agente especialista em análise ambiental, incêndios florestais,
dados orbitais, visão computacional, governança de IA e geração de relatórios executivos.

Gere um relatório técnico-executivo em português, claro, objetivo e acadêmico,
usando exclusivamente os dados fornecidos abaixo e o contexto recuperado da base de conhecimento.

Regras obrigatórias:
- Não invente dados.
- Não diga que houve fogo se a análise visual não indicou fogo.
- Não afirme que a imagem é do mês exato se a correspondência for aproximada.
- Explique que a imagem orbital pode ser aproximada quando o mês exato não estiver disponível.
- Use o contexto RAG apenas para enriquecer recomendações e governança.
- Não altere os dados técnicos calculados pelo sistema.
- Não inclua assinatura.
- Não inclua campos genéricos como [Nome do Analista], [Instituição] ou similares.
- Não crie nomes de responsáveis.
- Não inclua rodapé fictício.
- Finalize com conclusão e recomendação operacional.
- Use subtítulos curtos e objetivos.

Dados do sistema:

Município: {resultado["municipio"]}
Estado: {resultado["estado"]}
Bioma: {resultado["bioma"]}
Data da análise: {resultado["data"]}

Classe prevista pelo XGBoost: {resultado["classe_prevista"]}

Probabilidades:
- Alto: {resultado["probabilidades"].get("alto", 0):.2f}%
- Médio: {resultado["probabilidades"].get("medio", 0):.2f}%
- Baixo: {resultado["probabilidades"].get("baixo", 0):.2f}%

Análise climática:
{resultado["analise_climatica"]}

Análise visual orbital - BLIP:
- Período solicitado: {resultado["ano_mes_solicitado"]}
- Período da imagem utilizada: {resultado["ano_mes_imagem"]}
- Correspondência da imagem: {resultado["tipo_correspondencia_imagem"]}
- Descrição original BLIP: {resultado["descricao_original_blip"]}
- Descrição interpretada: {resultado["descricao_visual"]}
- Risco visual BLIP: {resultado["risco_visual"]}

Análise visual complementar - YOLO:
- Modelo: {resultado["yolo"]["modelo"]}
- Total de detecções: {resultado["yolo"]["total_deteccoes"]}
- Detecções: {resultado["yolo"]["deteccoes"]}
- Risco YOLO: {resultado["yolo"]["risco_yolo"]}
- Observação técnica: {resultado["yolo"]["observacao"]}

Recomendação base do orquestrador:
{resultado["recomendacao"]}

Contexto recuperado via RAG:
{contexto_rag}
""".strip()


def gerar_relatorio_openai(resultado, contexto_rag):
    """
    Gera relatório usando OpenAI.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada no .env")

    client = OpenAI(api_key=api_key)

    prompt = montar_prompt(
        resultado,
        contexto_rag
    )

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.25,
        max_output_tokens=950
    )

    return resposta.output_text


def executar_agente_relatorio(resultado):
    """
    Executa o agente relatório.

    1. Consulta Agente RAG.
    2. Tenta usar OpenAI.
    3. Se falhar, usa relatório local.
    """

    resultado_rag = executar_agente_rag(
        resultado["classe_prevista"]
    )

    contexto_rag = resultado_rag[
        "contexto_recuperado"
    ]

    try:
        relatorio = gerar_relatorio_openai(
            resultado,
            contexto_rag
        )

        return {
            "agente": "Agente Relatório",
            "status": "sucesso_openai",
            "modelo": "gpt-4.1-mini",
            "rag_status": resultado_rag["status"],
            "contexto_rag": contexto_rag,
            "relatorio": relatorio
        }

    except Exception as erro:
        relatorio = gerar_relatorio_local(
            resultado,
            contexto_rag
        )

        return {
            "agente": "Agente Relatório",
            "status": "fallback_local",
            "modelo": "local",
            "rag_status": resultado_rag["status"],
            "contexto_rag": contexto_rag,
            "erro": str(erro),
            "relatorio": relatorio
        }