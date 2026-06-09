"""
Coletor de NDVI mensal via Google Earth Engine.

Projeto: Sentinela Orbital IA

Objetivo:
- Calcular o NDVI médio mensal para os municípios monitorados.
- Gerar um arquivo CSV com 12 meses de NDVI por município.
- Usar o NDVI como variável complementar no modelo XGBoost.

Saída:
data/raw/ndvi_gee_mensal.csv
"""

import os
from pathlib import Path
from datetime import date

import pandas as pd
import ee


# Project ID configurado no Google Earth Engine / Google Cloud
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "sentinela-orbital-ia")


# Caminho base do projeto:
# arquivo atual: src/api/coletor_ndvi_gee.py
# parents[2] aponta para: Global-Solution-2
BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_MUNICIPIOS = BASE_DIR / "data" / "external" / "municipios_monitorados.csv"
ARQUIVO_SAIDA = BASE_DIR / "data" / "raw" / "ndvi_gee_mensal.csv"


def autenticar_google_earth_engine():
    """
    Inicializa o Google Earth Engine usando o Project ID.

    Na primeira execução, o navegador poderá ser aberto para autenticação.
    Depois disso, o token fica salvo localmente.
    """
    try:
        ee.Initialize(project=PROJECT_ID)
        print(f"Google Earth Engine inicializado com sucesso. Projeto: {PROJECT_ID}")

    except Exception:
        print("Autenticação necessária no Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)
        print(f"Google Earth Engine autenticado e inicializado. Projeto: {PROJECT_ID}")


def gerar_periodos_mensais(qtd_meses=12):
    """
    Gera os últimos N meses fechados.

    Exemplo:
    Se hoje for 2026-06, o script coleta:
    2025-06 até 2026-05.
    """
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    periodos = []

    for _ in range(qtd_meses):
        mes -= 1

        if mes == 0:
            mes = 12
            ano -= 1

        data_inicio = date(ano, mes, 1)

        if mes == 12:
            data_fim = date(ano + 1, 1, 1)
        else:
            data_fim = date(ano, mes + 1, 1)

        ano_mes = f"{ano}-{mes:02d}"

        periodos.append({
            "ano": ano,
            "mes": mes,
            "ano_mes": ano_mes,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat()
        })

    return list(reversed(periodos))


def calcular_ndvi_mensal(latitude, longitude, data_inicio, data_fim):
    """
    Calcula o NDVI médio mensal usando Sentinel-2 SR Harmonized.

    NDVI = (NIR - RED) / (NIR + RED)

    Sentinel-2:
    - B8 = Near Infrared (NIR)
    - B4 = Red

    Retorna:
    - float com NDVI médio
    - None se não houver imagem válida no período
    """
    ponto = ee.Geometry.Point([longitude, latitude])

    colecao = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(ponto)
        .filterDate(data_inicio, data_fim)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 70))
    )

    quantidade = colecao.size().getInfo()

    if quantidade == 0:
        return None

    imagem_mediana = colecao.median()

    bandas = imagem_mediana.bandNames().getInfo()

    if "B8" not in bandas or "B4" not in bandas:
        return None

    ndvi = imagem_mediana.normalizedDifference(["B8", "B4"]).rename("NDVI")

    resultado = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=ponto.buffer(5000),
        scale=30,
        maxPixels=1e9
    ).getInfo()

    valor_ndvi = resultado.get("NDVI")

    if valor_ndvi is None:
        return None

    return round(float(valor_ndvi), 4)


def main():
    """
    Fluxo principal:
    1. Lê municípios monitorados.
    2. Gera os últimos 12 meses fechados.
    3. Calcula NDVI mensal para cada município.
    4. Salva o CSV final.
    """
    if not ARQUIVO_MUNICIPIOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_MUNICIPIOS}")

    autenticar_google_earth_engine()

    municipios = pd.read_csv(ARQUIVO_MUNICIPIOS)
    periodos = gerar_periodos_mensais(qtd_meses=12)

    registros = []

    for _, linha in municipios.iterrows():
        municipio = linha["municipio"]
        estado = linha["estado"]
        bioma = linha["bioma"]
        latitude = float(linha["latitude"])
        longitude = float(linha["longitude"])

        print(f"\nCalculando NDVI mensal para: {municipio} - {estado}")

        for periodo in periodos:
            ano_mes = periodo["ano_mes"]
            data_inicio = periodo["data_inicio"]
            data_fim = periodo["data_fim"]

            try:
                ndvi_medio = calcular_ndvi_mensal(
                    latitude=latitude,
                    longitude=longitude,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )

                print(f"  {ano_mes}: {ndvi_medio}")

            except Exception as erro:
                print(f"  Erro em {municipio} ({ano_mes}): {erro}")
                ndvi_medio = None

            registros.append({
                "municipio": municipio,
                "estado": estado,
                "bioma": bioma,
                "latitude": latitude,
                "longitude": longitude,
                "ano_mes": ano_mes,
                "ndvi_medio": ndvi_medio
            })

    df_saida = pd.DataFrame(registros)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_saida.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")

    print("\nColeta de NDVI mensal finalizada!")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"Total de registros: {len(df_saida)}")


if __name__ == "__main__":
    main()
