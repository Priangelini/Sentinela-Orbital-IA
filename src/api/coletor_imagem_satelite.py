"""
Coletor de Imagens Sentinel-2

Projeto:
Sentinela Orbital IA

Objetivo:
Gerar imagens mensais Sentinel-2 para cada município
monitorado utilizando Google Earth Engine.

Saída:

data/raw/imagens_satelite/

"""

from pathlib import Path
from datetime import date

import ee
import requests
import pandas as pd


# =====================================================
# CAMINHOS
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_MUNICIPIOS = (
    BASE_DIR
    / "data"
    / "external"
    / "municipios_monitorados.csv"
)

PASTA_IMAGENS = (
    BASE_DIR
    / "data"
    / "raw"
    / "imagens_satelite"
)


# =====================================================
# GOOGLE EARTH ENGINE
# =====================================================

def inicializar_gee():
    """
    Inicializa Earth Engine.
    """

    try:

        ee.Initialize(
            project="sentinela-orbital-ia"
        )

        print(
            "Earth Engine inicializado."
        )

    except Exception:

        print(
            "Autenticação necessária..."
        )

        ee.Authenticate()

        ee.Initialize(
            project="sentinela-orbital-ia"
        )

        print(
            "Earth Engine autenticado."
        )


# =====================================================
# PERÍODOS MENSAIS
# =====================================================

def gerar_periodos_mensais(
    quantidade_meses=12
):
    """
    Gera os últimos N meses.
    """

    hoje = date.today()

    ano = hoje.year
    mes = hoje.month

    periodos = []

    for _ in range(quantidade_meses):

        mes -= 1

        if mes == 0:

            mes = 12
            ano -= 1

        inicio = (
            f"{ano}-{mes:02d}-01"
        )

        if mes == 12:

            fim = (
                f"{ano + 1}-01-01"
            )

        else:

            fim = (
                f"{ano}-{mes + 1:02d}-01"
            )

        periodos.append(
            {
                "ano_mes":
                    f"{ano}_{mes:02d}",

                "inicio":
                    inicio,

                "fim":
                    fim
            }
        )

    return list(reversed(periodos))


# =====================================================
# BUSCA IMAGEM SENTINEL
# =====================================================

def obter_imagem_sentinel(
    latitude,
    longitude,
    data_inicio,
    data_fim
):
    """
    Obtém melhor imagem Sentinel-2
    para o período informado.
    """

    ponto = ee.Geometry.Point(
        [longitude, latitude]
    )

    colecao = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(ponto)
        .filterDate(
            data_inicio,
            data_fim
        )
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                20
            )
        )
        .sort(
            "CLOUDY_PIXEL_PERCENTAGE"
        )
    )

    quantidade = (
        colecao.size()
        .getInfo()
    )

    if quantidade == 0:

        return None

    return colecao.first()


# =====================================================
# URL THUMBNAIL
# =====================================================

def gerar_url_imagem(
    imagem,
    latitude,
    longitude
):
    """
    Cria URL da imagem RGB.
    """

    regiao = (
        ee.Geometry.Point(
            [longitude, latitude]
        )
        .buffer(10000)
        .bounds()
    )

    return imagem.getThumbURL(
        {
            "bands":
                ["B4", "B3", "B2"],

            "min":
                0,

            "max":
                3000,

            "region":
                regiao,

            "dimensions":
                1024,

            "format":
                "png"
        }
    )


# =====================================================
# DOWNLOAD
# =====================================================

def baixar_imagem(
    url,
    destino
):
    """
    Faz download da imagem.
    """

    resposta = requests.get(
        url,
        timeout=120
    )

    if resposta.status_code != 200:

        return False

    with open(
        destino,
        "wb"
    ) as arquivo:

        arquivo.write(
            resposta.content
        )

    return True


# =====================================================
# EXECUÇÃO
# =====================================================

def main():

    inicializar_gee()

    PASTA_IMAGENS.mkdir(
        parents=True,
        exist_ok=True
    )

    municipios = pd.read_csv(
        ARQUIVO_MUNICIPIOS
    )

    periodos = (
        gerar_periodos_mensais(
            quantidade_meses=12
        )
    )

    total = 0

    for _, linha in municipios.iterrows():

        municipio = (
            linha["municipio"]
        )

        estado = (
            linha["estado"]
        )

        latitude = float(
            linha["latitude"]
        )

        longitude = float(
            linha["longitude"]
        )

        print()
        print(
            f"Município: "
            f"{municipio} - {estado}"
        )

        for periodo in periodos:

            ano_mes = (
                periodo["ano_mes"]
            )

            inicio = (
                periodo["inicio"]
            )

            fim = (
                periodo["fim"]
            )

            nome_arquivo = (
                f"{municipio}_{estado}_{ano_mes}"
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
                + ".png"
            )

            destino = (
                PASTA_IMAGENS
                / nome_arquivo
            )

            print(
                f"  Gerando "
                f"{ano_mes}"
            )

            try:

                imagem = (
                    obter_imagem_sentinel(
                        latitude,
                        longitude,
                        inicio,
                        fim
                    )
                )

                if imagem is None:

                    print(
                        "    Sem imagem."
                    )

                    continue

                url = gerar_url_imagem(
                    imagem,
                    latitude,
                    longitude
                )

                sucesso = (
                    baixar_imagem(
                        url,
                        destino
                    )
                )

                if sucesso:

                    total += 1

                    print(
                        f"    OK -> "
                        f"{nome_arquivo}"
                    )

                else:

                    print(
                        "    Falha download"
                    )

            except Exception as erro:

                print(
                    f"    Erro: "
                    f"{erro}"
                )

    print()
    print("=" * 60)
    print(
        "COLETA DE IMAGENS FINALIZADA"
    )
    print("=" * 60)

    print(
        f"Total de imagens: "
        f"{total}"
    )

    print(
        f"Pasta: "
        f"{PASTA_IMAGENS}"
    )


if __name__ == "__main__":
    main()