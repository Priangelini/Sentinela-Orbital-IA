"""
Módulo de predição real de risco de incêndio.

Projeto: Sentinela Orbital IA

Este arquivo pode ser usado de 3 formas:
1. Executado diretamente no terminal.
2. Importado pelo Agente de Risco.
3. Importado pelo Dashboard Streamlit.

Entradas:
- Dataset consolidado: data/processed/dataset_treinamento.csv
- Modelo XGBoost: src/models/modelo_xgboost.pkl
- Label Encoder: src/models/label_encoder.pkl
"""

from pathlib import Path
import pandas as pd
import joblib


# =====================================================
# CAMINHOS DO PROJETO
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_DATASET = BASE_DIR / "data" / "processed" / "dataset_treinamento.csv"
ARQUIVO_MODELO = BASE_DIR / "src" / "models" / "modelo_xgboost.pkl"
ARQUIVO_ENCODER = BASE_DIR / "src" / "models" / "label_encoder.pkl"


# =====================================================
# FEATURES USADAS NO TREINAMENTO DO MODELO
# =====================================================

FEATURES = [
    "latitude",
    "longitude",
    "mes",
    "dia_semana",
    "temperatura_media",
    "umidade_media",
    "precipitacao",
    "vento_medio",
    "ndvi_medio",
    "focos_calor",
    "frp_total",
    "frp_medio",
]


# =====================================================
# FUNÇÕES PRINCIPAIS
# =====================================================

def carregar_modelo():
    """
    Carrega o modelo XGBoost e o Label Encoder.
    """
    modelo = joblib.load(ARQUIVO_MODELO)
    encoder = joblib.load(ARQUIVO_ENCODER)
    return modelo, encoder


def carregar_dataset():
    """
    Carrega o dataset consolidado com dados reais.
    """
    df = pd.read_csv(ARQUIVO_DATASET)
    df["data"] = pd.to_datetime(df["data"])
    return df


def obter_registro_mais_recente(municipio=None):
    """
    Retorna o registro mais recente do dataset.

    Se municipio for informado, filtra pelo município.
    Caso contrário, retorna o registro mais recente geral.
    """
    df = carregar_dataset()

    if municipio:
        df = df[df["municipio"].str.lower() == municipio.lower()]

        if df.empty:
            raise ValueError(f"Município não encontrado no dataset: {municipio}")

    registro = df.sort_values("data", ascending=False).iloc[0]
    return registro


def prever_risco(registro):
    """
    Executa a predição de risco usando um registro do dataset.

    Retorna um dicionário pronto para uso em agente, dashboard ou terminal.
    """
    modelo, encoder = carregar_modelo()

    entrada = pd.DataFrame([registro[FEATURES]])

    predicao = modelo.predict(entrada)
    probabilidades = modelo.predict_proba(entrada)[0]

    classe_prevista = encoder.inverse_transform(predicao)[0]

    probabilidades_dict = {
        classe: round(float(probabilidades[indice]) * 100, 2)
        for indice, classe in enumerate(encoder.classes_)
    }

    resultado = {
        "municipio": registro["municipio"],
        "estado": registro["estado"],
        "bioma": registro["bioma"],
        "data": str(registro["data"].date()),
        "classe_prevista": classe_prevista,
        "probabilidades": probabilidades_dict,
        "dados_entrada": {
            "latitude": float(registro["latitude"]),
            "longitude": float(registro["longitude"]),
            "temperatura_media": float(registro["temperatura_media"]),
            "umidade_media": float(registro["umidade_media"]),
            "precipitacao": float(registro["precipitacao"]),
            "vento_medio": float(registro["vento_medio"]),
            "ndvi_medio": float(registro["ndvi_medio"]),
            "focos_calor": int(registro["focos_calor"]),
            "frp_total": float(registro["frp_total"]),
            "frp_medio": float(registro["frp_medio"]),
            "fonte_focos": registro["fonte_focos"],
        },
    }

    return resultado


def prever_risco_por_municipio(municipio=None):
    """
    Função principal para integração.

    Uso:
    - prever_risco_por_municipio()
    - prever_risco_por_municipio("Pocone")
    - prever_risco_por_municipio("Porto Velho")
    """
    registro = obter_registro_mais_recente(municipio)
    return prever_risco(registro)


def imprimir_resultado(resultado):
    """
    Exibe o resultado da predição no terminal.
    """
    print("=" * 60)
    print("PREDIÇÃO REAL DE RISCO DE INCÊNDIO")
    print("=" * 60)

    print(f"Município: {resultado['municipio']} - {resultado['estado']}")
    print(f"Bioma: {resultado['bioma']}")
    print(f"Data: {resultado['data']}")

    dados = resultado["dados_entrada"]

    print("\nDados observados:")
    print(f"Temperatura média: {dados['temperatura_media']} °C")
    print(f"Umidade média: {dados['umidade_media']}%")
    print(f"Precipitação: {dados['precipitacao']} mm")
    print(f"Vento médio: {dados['vento_medio']} km/h")
    print(f"NDVI médio: {dados['ndvi_medio']}")
    print(f"Focos de calor: {dados['focos_calor']}")
    print(f"FRP total: {dados['frp_total']}")
    print(f"Fonte dos focos: {dados['fonte_focos']}")

    print("\nResultado:")
    print(f"Classe prevista: {resultado['classe_prevista'].upper()}")

    print("\nProbabilidades:")
    for classe, valor in resultado["probabilidades"].items():
        print(f"{classe}: {valor}%")


# =====================================================
# EXECUÇÃO DIRETA PELO TERMINAL
# =====================================================

if __name__ == "__main__":
    # Altere aqui para testar município específico.
    # Exemplos: "Pocone", "Porto Velho", "Corumba"
    MUNICIPIO_TESTE = None

    resultado_predicao = prever_risco_por_municipio(MUNICIPIO_TESTE)
    imprimir_resultado(resultado_predicao)