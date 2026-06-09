"""
Agente Visual - BLIP + Sentinel-2

Seleciona a imagem Sentinel correspondente ao município e mês.
Se a imagem exata não existir, usa a imagem mais próxima disponível.

Também traduz/interpreta a descrição original do BLIP para português.
"""

from pathlib import Path
from datetime import datetime

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


BASE_DIR = Path(__file__).resolve().parents[2]

PASTA_IMAGENS = (
    BASE_DIR
    / "data"
    / "raw"
    / "imagens_satelite"
)


def carregar_blip():
    """
    Carrega o modelo BLIP pré-treinado.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    modelo = "Salesforce/blip-image-captioning-base"

    processor = BlipProcessor.from_pretrained(modelo)
    model = BlipForConditionalGeneration.from_pretrained(modelo).to(device)

    return processor, model, device


def gerar_descricao(caminho_imagem):
    """
    Gera descrição automática da imagem usando BLIP.
    O BLIP normalmente retorna texto em inglês.
    """
    processor, model, device = carregar_blip()

    imagem = Image.open(caminho_imagem).convert("RGB")

    inputs = processor(
        images=imagem,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=40,
            num_beams=5
        )

    descricao = processor.decode(
        output[0],
        skip_special_tokens=True
    )

    return descricao


def traduzir_descricao_visual(descricao_original):
    """
    Traduz/interpreta descrições comuns do BLIP
    para português, mantendo contexto ambiental.
    """

    texto = descricao_original.lower().strip()

    traducoes_exatas = {
        "an aerial view of a city from space":
            "Vista aérea de uma área urbana observada por satélite.",

        "a satellite image of a city":
            "Imagem de satélite mostrando uma área urbana.",

        "a satellite image of a river":
            "Imagem de satélite mostrando um rio e seu entorno.",

        "a satellite image of a forest":
            "Imagem de satélite mostrando uma área florestal.",

        "a satellite image of agricultural land":
            "Imagem de satélite mostrando área agrícola.",

        "a satellite image of farmland":
            "Imagem de satélite mostrando área agrícola.",

        "a satellite image of vegetation":
            "Imagem de satélite mostrando cobertura vegetal.",

        "an aerial view of farmland":
            "Vista aérea de uma área agrícola.",

        "an aerial view of a forest":
            "Vista aérea de uma área florestal.",

        "an aerial view of a river":
            "Vista aérea de um rio e áreas próximas.",

        "an aerial view of a field":
            "Vista aérea de uma área de campo ou vegetação aberta.",
    }

    if texto in traducoes_exatas:
        return traducoes_exatas[texto]

    if "smoke" in texto:
        return "A imagem apresenta indícios visuais de fumaça ou névoa sobre a região monitorada."

    if "fire" in texto or "burning" in texto or "wildfire" in texto:
        return "A imagem apresenta indícios visuais associados a fogo ou queimada."

    if "burned" in texto:
        return "A imagem apresenta possível área queimada ou vegetação degradada."

    if "city" in texto:
        return "Imagem orbital com presença de área urbana na região monitorada."

    if "river" in texto or "water" in texto or "lake" in texto:
        return "Imagem orbital com presença de corpo hídrico na região monitorada."

    if "forest" in texto or "trees" in texto:
        return "Imagem orbital com presença de área florestal ou cobertura vegetal densa."

    if "vegetation" in texto or "green" in texto:
        return "Imagem orbital com presença de cobertura vegetal."

    if "agricultural" in texto or "farmland" in texto or "farm" in texto:
        return "Imagem orbital com presença de áreas agrícolas."

    if "soil" in texto or "brown" in texto or "dry" in texto or "land" in texto:
        return "Imagem orbital com presença de solo exposto, vegetação seca ou áreas abertas."

    return f"Descrição automática gerada pelo BLIP: {descricao_original}"


def classificar_risco_visual(descricao_original):
    """
    Classifica o risco visual com base na descrição original do BLIP.
    """

    texto = descricao_original.lower()

    palavras_alto = [
        "fire",
        "smoke",
        "burning",
        "burned",
        "wildfire",
        "forest fire",
        "black smoke",
        "flames"
    ]

    palavras_medio = [
        "dry",
        "vegetation",
        "field",
        "soil",
        "land",
        "forest",
        "grass",
        "agricultural",
        "farm",
        "brown",
        "farmland"
    ]

    for palavra in palavras_alto:
        if palavra in texto:
            return "alto"

    for palavra in palavras_medio:
        if palavra in texto:
            return "medio"

    return "baixo"


def normalizar_nome(municipio, estado):
    """
    Normaliza nome do município e estado
    para bater com o padrão dos arquivos.
    """
    return (
        f"{municipio}_{estado}"
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def converter_ano_mes_para_data(ano_mes):
    """
    Converte 2026-06 ou 2026_06 para datetime.
    """
    ano_mes = ano_mes.replace("_", "-")
    return datetime.strptime(ano_mes, "%Y-%m")


def extrair_ano_mes_do_arquivo(nome_arquivo, prefixo):
    """
    Exemplo:
    barao_de_melgaco_mt_2026_05.png
    retorna 2026-05
    """
    parte = (
        nome_arquivo
        .replace(prefixo + "_", "")
        .replace(".png", "")
    )

    return parte.replace("_", "-")


def localizar_imagem_municipio_mes(municipio, estado, ano_mes):
    """
    Primeiro tenta localizar a imagem exata.
    Se não existir, busca a imagem temporalmente mais próxima.
    """

    ano_mes_formatado = ano_mes.replace("-", "_")

    prefixo = normalizar_nome(municipio, estado)

    nome_exato = f"{prefixo}_{ano_mes_formatado}.png"
    caminho_exato = PASTA_IMAGENS / nome_exato

    if caminho_exato.exists():
        return caminho_exato, ano_mes, "exata"

    imagens = list(PASTA_IMAGENS.glob(f"{prefixo}_*.png"))

    if not imagens:
        return None, None, "nao_encontrada"

    data_alvo = converter_ano_mes_para_data(ano_mes)

    candidatas = []

    for imagem in imagens:
        try:
            ano_mes_img = extrair_ano_mes_do_arquivo(
                imagem.name,
                prefixo
            )

            data_img = converter_ano_mes_para_data(ano_mes_img)

            diferenca = abs(
                (data_img.year - data_alvo.year) * 12
                + (data_img.month - data_alvo.month)
            )

            candidatas.append(
                {
                    "caminho": imagem,
                    "ano_mes": ano_mes_img,
                    "diferenca": diferenca
                }
            )

        except Exception:
            continue

    if not candidatas:
        return None, None, "nao_encontrada"

    melhor = sorted(
        candidatas,
        key=lambda item: item["diferenca"]
    )[0]

    return (
        melhor["caminho"],
        melhor["ano_mes"],
        "aproximada"
    )


def executar_agente_visual(municipio, estado, ano_mes):
    """
    Executa o agente visual completo.
    """

    caminho_imagem, ano_mes_imagem, tipo_correspondencia = (
        localizar_imagem_municipio_mes(
            municipio,
            estado,
            ano_mes
        )
    )

    if caminho_imagem is None:
        return {
            "agente": "Agente Visual",
            "status": "imagem_nao_encontrada",
            "ano_mes_solicitado": ano_mes,
            "ano_mes_imagem": None,
            "tipo_correspondencia": tipo_correspondencia,
            "imagem": None,
            "descricao_original_blip": None,
            "descricao_visual": "Imagem não encontrada.",
            "risco_visual": "indisponivel"
        }

    descricao_original = gerar_descricao(caminho_imagem)

    descricao_traduzida = traduzir_descricao_visual(
        descricao_original
    )

    risco_visual = classificar_risco_visual(
        descricao_original
    )

    return {
        "agente": "Agente Visual",
        "status": "sucesso",
        "ano_mes_solicitado": ano_mes,
        "ano_mes_imagem": ano_mes_imagem,
        "tipo_correspondencia": tipo_correspondencia,
        "imagem": str(caminho_imagem),
        "descricao_original_blip": descricao_original,
        "descricao_visual": descricao_traduzida,
        "risco_visual": risco_visual
    }


if __name__ == "__main__":
    resultado = executar_agente_visual(
        municipio="Barao de Melgaco",
        estado="MT",
        ano_mes="2026-06"
    )

    print("=" * 60)
    print("AGENTE VISUAL")
    print("=" * 60)
    print(f"Status: {resultado['status']}")
    print(f"Ano/Mês solicitado: {resultado['ano_mes_solicitado']}")
    print(f"Ano/Mês imagem usada: {resultado['ano_mes_imagem']}")
    print(f"Correspondência: {resultado['tipo_correspondencia']}")
    print(f"Imagem: {resultado['imagem']}")
    print(f"Descrição original BLIP: {resultado['descricao_original_blip']}")
    print(f"Descrição visual: {resultado['descricao_visual']}")
    print(f"Risco Visual: {resultado['risco_visual']}")