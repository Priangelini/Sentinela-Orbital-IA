"""
Agente Climático

Responsável por:
- Interpretar os dados ambientais.
- Gerar uma análise textual simples sobre clima e risco.
"""


def executar_agente_clima(dados_entrada):
    """
    Recebe os dados utilizados pelo modelo e gera uma leitura climática.
    """

    temperatura = dados_entrada["temperatura_media"]
    umidade = dados_entrada["umidade_media"]
    precipitacao = dados_entrada["precipitacao"]
    vento = dados_entrada["vento_medio"]
    ndvi = dados_entrada["ndvi_medio"]
    focos = dados_entrada["focos_calor"]

    alertas = []

    if temperatura >= 33:
        alertas.append("temperatura elevada")
    elif temperatura >= 28:
        alertas.append("temperatura moderada")

    if umidade <= 35:
        alertas.append("umidade muito baixa")
    elif umidade <= 55:
        alertas.append("umidade moderada")

    if precipitacao <= 1:
        alertas.append("baixa ou nenhuma precipitação")

    if vento >= 12:
        alertas.append("vento favorável à propagação do fogo")

    if ndvi < 0.35:
        alertas.append("vegetação com baixo vigor")

    if focos > 0:
        alertas.append("presença de focos de calor detectados")

    if not alertas:
        alertas.append("condições ambientais sem sinais críticos imediatos")

    return {
        "agente": "Agente Climático",
        "status": "sucesso",
        "analise_climatica": alertas,
    }