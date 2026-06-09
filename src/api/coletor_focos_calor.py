import os
from io import StringIO
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd
import requests


# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_MUNICIPIOS = BASE_DIR / "data" / "external" / "municipios_monitorados.csv"
ARQUIVO_CLIMA = BASE_DIR / "data" / "raw" / "clima_openmeteo.csv"

ARQUIVO_DETALHADO = BASE_DIR / "data" / "raw" / "focos_calor_detalhado.csv"
ARQUIVO_AGREGADO = BASE_DIR / "data" / "raw" / "focos_calor.csv"

MAP_KEY = os.getenv("NASA_FIRMS_MAP_KEY")

SENSOR = "VIIRS_SNPP_NRT"
DAY_RANGE = 5
RAIO_GRAUS = 0.4


# =====================================================
# COLETA NASA FIRMS
# =====================================================

def montar_bbox(lat, lon, raio=RAIO_GRAUS):
    """
    Cria uma área de busca ao redor do município.
    Formato exigido pela NASA FIRMS: west,south,east,north.
    """
    west = lon - raio
    south = lat - raio
    east = lon + raio
    north = lat + raio
    return f"{west},{south},{east},{north}"


def coletar_firms(lat, lon, data_inicio):
    """
    Consulta a API NASA FIRMS para coletar focos de calor
    na região do município monitorado.
    """
    if not MAP_KEY:
        return None

    bbox = montar_bbox(lat, lon)

    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{MAP_KEY}/{SENSOR}/{bbox}/{DAY_RANGE}/{data_inicio}"
    )

    try:
        resposta = requests.get(url, timeout=40)

        if resposta.status_code != 200:
            print(f"   NASA FIRMS retornou status {resposta.status_code}")
            return None

        texto = resposta.text.strip()

        if not texto:
            return None

        if "Invalid" in texto[:300] or "MAP_KEY" in texto[:300]:
            print("   MAP_KEY inválida ou resposta inesperada.")
            return None

        if "latitude" not in texto.splitlines()[0]:
            print("   Resposta sem cabeçalho CSV esperado.")
            return None

        return pd.read_csv(StringIO(texto))

    except Exception as erro:
        print(f"   Erro na requisição: {erro}")
        return None


# =====================================================
# FALLBACK SIMULADO
# =====================================================

def gerar_focos_simulados(linha):
    """
    Gera focos simulados com base em condições climáticas.
    Usado apenas quando a API NASA FIRMS não retorna dados.
    """
    temperatura = linha["temperatura_media"]
    umidade = linha["umidade_media"]
    vento = linha["vento_medio"]
    precipitacao = linha["precipitacao"]
    bioma = linha["bioma"]

    score = 0

    if temperatura >= 33:
        score += 3
    elif temperatura >= 29:
        score += 2
    elif temperatura >= 26:
        score += 1

    if umidade <= 35:
        score += 3
    elif umidade <= 50:
        score += 2
    elif umidade <= 65:
        score += 1

    if vento >= 14:
        score += 2
    elif vento >= 8:
        score += 1

    if precipitacao < 2:
        score += 1

    if bioma == "Pantanal":
        score += 1

    return max(0, int(np.random.poisson(max(score, 0))))


def gerar_fallback_municipio(clima, municipio, estado, bioma):
    """
    Cria registros simulados de focos de calor usando a base climática.
    """
    registros = []

    dados_mun = clima[
        (clima["municipio"] == municipio)
        & (clima["estado"] == estado)
    ]

    for _, linha in dados_mun.iterrows():
        focos = gerar_focos_simulados(linha)

        registros.append({
            "municipio": municipio,
            "estado": estado,
            "bioma": bioma,
            "data": linha["data"],
            "focos_calor": focos,
            "frp_total": round(focos * 12.5, 2),
            "frp_medio": round(12.5 if focos > 0 else 0, 2),
            "fonte_focos": "SIMULADO_CLIMATICO"
        })

    return registros


# =====================================================
# AGREGAÇÃO DOS DADOS REAIS
# =====================================================

def agregar_dados_reais(df_nasa, municipio, estado, bioma):
    """
    Agrega os dados reais por data, gerando:
    - quantidade de focos;
    - FRP total;
    - FRP médio.
    """
    agregado = (
        df_nasa
        .groupby("acq_date")
        .agg(
            focos_calor=("acq_date", "size"),
            frp_total=("frp", "sum"),
            frp_medio=("frp", "mean")
        )
        .reset_index()
        .rename(columns={"acq_date": "data"})
    )

    registros = []

    for _, linha in agregado.iterrows():
        registros.append({
            "municipio": municipio,
            "estado": estado,
            "bioma": bioma,
            "data": linha["data"],
            "focos_calor": int(linha["focos_calor"]),
            "frp_total": round(float(linha["frp_total"]), 2),
            "frp_medio": round(float(linha["frp_medio"]), 2),
            "fonte_focos": "NASA_FIRMS"
        })

    return registros


# =====================================================
# EXECUÇÃO PRINCIPAL
# =====================================================

def main():
    print("Iniciando coleta de focos de calor - NASA FIRMS\n")

    if not ARQUIVO_MUNICIPIOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_MUNICIPIOS}")

    municipios = pd.read_csv(ARQUIVO_MUNICIPIOS)

    clima = pd.read_csv(ARQUIVO_CLIMA) if ARQUIVO_CLIMA.exists() else None

    if MAP_KEY:
        print("MAP_KEY encontrada. Tentando coletar dados reais da NASA FIRMS.\n")
    else:
        print("MAP_KEY não encontrada. Usando fallback simulado.\n")

    data_inicio = (date.today() - timedelta(days=DAY_RANGE)).isoformat()

    registros_detalhados = []
    registros_agregados = []

    for _, mun in municipios.iterrows():
        municipio = mun["municipio"]
        estado = mun["estado"]
        bioma = mun["bioma"]
        lat = float(mun["latitude"])
        lon = float(mun["longitude"])

        print(f"Processando: {municipio} - {estado}")

        df_nasa = coletar_firms(lat, lon, data_inicio)

        if df_nasa is not None and not df_nasa.empty and "acq_date" in df_nasa.columns:
            df_nasa["municipio"] = municipio
            df_nasa["estado"] = estado
            df_nasa["bioma"] = bioma
            df_nasa["latitude_municipio"] = lat
            df_nasa["longitude_municipio"] = lon
            df_nasa["fonte_focos"] = "NASA_FIRMS"

            registros_detalhados.append(df_nasa)
            registros_agregados.extend(
                agregar_dados_reais(df_nasa, municipio, estado, bioma)
            )

            print(f"   {len(df_nasa)} focos reais coletados")

        else:
            print("   Sem dados reais. Usando fallback simulado.")

            if clima is not None:
                registros_agregados.extend(
                    gerar_fallback_municipio(clima, municipio, estado, bioma)
                )
            else:
                print("   Arquivo climático ausente. Fallback não executado.")

    df_detalhado = (
        pd.concat(registros_detalhados, ignore_index=True)
        if registros_detalhados
        else pd.DataFrame()
    )

    df_agregado = pd.DataFrame(registros_agregados)

    ARQUIVO_DETALHADO.parent.mkdir(parents=True, exist_ok=True)

    df_detalhado.to_csv(ARQUIVO_DETALHADO, index=False, encoding="utf-8")
    df_agregado.to_csv(ARQUIVO_AGREGADO, index=False, encoding="utf-8")

    print("\nColeta finalizada!")
    print(f"Detalhado: {ARQUIVO_DETALHADO}")
    print(f"Agregado:  {ARQUIVO_AGREGADO}")
    print(f"Total de focos reais detalhados: {len(df_detalhado)}")
    print(f"Total de registros agregados: {len(df_agregado)}")


if __name__ == "__main__":
    main()

