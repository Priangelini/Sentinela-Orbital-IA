"""
Agente de Risco

Responsável por:
- Consultar o modelo XGBoost treinado.
- Obter a previsão real de risco de incêndio.
- Preparar a resposta para o orquestrador.
"""

from src.ml.prever_risco_real import prever_risco_por_municipio


def executar_agente_risco(municipio=None):
    """
    Executa a predição de risco para um município específico
    ou para o registro mais recente do dataset.
    """

    resultado = prever_risco_por_municipio(municipio)

    return {
        "agente": "Agente de Risco",
        "status": "sucesso",
        "municipio": resultado["municipio"],
        "estado": resultado["estado"],
        "bioma": resultado["bioma"],
        "data": resultado["data"],
        "classe_prevista": resultado["classe_prevista"],
        "probabilidades": resultado["probabilidades"],
        "dados_entrada": resultado["dados_entrada"],
    }


if __name__ == "__main__":
    resposta = executar_agente_risco()
    print(resposta)