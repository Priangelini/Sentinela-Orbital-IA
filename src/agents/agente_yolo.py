"""
Agente YOLO - Detecção Visual Integrada

Projeto:
Sentinela Orbital IA

Responsável por:
- Receber a imagem definida pelo Agente Visual.
- Executar YOLOv8 sobre a imagem Sentinel-2.
- Retornar detecções para o Orquestrador.
- Salvar uma imagem anotada para o Dashboard.

Observação:
O modelo yolov8n.pt é genérico e foi treinado no COCO.
Em imagens orbitais Sentinel-2, é esperado que existam poucas ou nenhuma detecção.
Para produção, o ideal seria treinar um modelo YOLO específico para imagens
orbitais de fumaça, cicatrizes de queimada, solo exposto e áreas degradadas.
"""

from pathlib import Path
from collections import Counter

import cv2
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[2]

PASTA_SAIDA = (
    BASE_DIR
    / "docs"
    / "imagens"
    / "yolo"
)

MODELO_YOLO = "yolov8n.pt"

CONFIANCA_MINIMA = 0.50


def carregar_modelo_yolo():
    """
    Carrega o modelo YOLOv8.
    """
    return YOLO(MODELO_YOLO)


def resumir_deteccoes(deteccoes):
    """
    Gera resumo das classes detectadas.
    """
    if not deteccoes:
        return {}

    contador = Counter(
        item["classe"] for item in deteccoes
    )

    return dict(contador)


def classificar_risco_yolo(deteccoes):
    """
    Classifica risco visual com base nas detecções do YOLO.

    Como o modelo é genérico, a regra é conservadora:
    - fire/smoke não existem no COCO padrão, mas ficam previstos
      caso seja usado um modelo treinado no futuro.
    - Detecções urbanas ou veículos não indicam incêndio diretamente.
    """

    if not deteccoes:
        return "baixo"

    classes_alto = [
        "fire",
        "smoke",
        "flame",
        "wildfire"
    ]

    classes_medio = [
        "car",
        "truck",
        "bus",
        "person",
        "boat"
    ]

    nomes = [
        item["classe"].lower()
        for item in deteccoes
    ]

    for classe in classes_alto:
        if classe in nomes:
            return "alto"

    for classe in classes_medio:
        if classe in nomes:
            return "medio"

    return "baixo"


def gerar_observacao(total_deteccoes, risco_yolo):
    """
    Gera observação interpretativa para relatório e dashboard.
    """
    if total_deteccoes == 0:
        return (
            "YOLO executado com sucesso. Não foram detectados objetos com "
            f"confiança mínima de {int(CONFIANCA_MINIMA * 100)}%. "
            "Em imagens orbitais Sentinel-2, esse resultado é esperado, pois o "
            "modelo YOLOv8n padrão foi treinado para objetos do cotidiano e não "
            "especificamente para queimadas, fumaça orbital ou cicatrizes de fogo."
        )

    return (
        f"YOLO executado com sucesso. Foram detectados {total_deteccoes} objeto(s) "
        f"com confiança mínima de {int(CONFIANCA_MINIMA * 100)}%. "
        f"A classificação visual auxiliar pelo YOLO foi definida como "
        f"{risco_yolo.upper()}."
    )


def executar_agente_yolo(caminho_imagem):
    """
    Executa o YOLO sobre a imagem recebida do Orquestrador.

    Parâmetro:
    - caminho_imagem: caminho da imagem Sentinel selecionada pelo Agente Visual.
    """

    if not caminho_imagem:
        return {
            "agente": "Agente YOLO",
            "status": "imagem_indisponivel",
            "modelo": MODELO_YOLO,
            "confianca_minima": CONFIANCA_MINIMA,
            "imagem_entrada": None,
            "imagem_anotada": None,
            "deteccoes": [],
            "resumo_deteccoes": {},
            "total_deteccoes": 0,
            "risco_yolo": "indisponivel",
            "observacao": "Nenhuma imagem foi recebida para análise YOLO."
        }

    caminho_imagem = Path(caminho_imagem)

    if not caminho_imagem.exists():
        return {
            "agente": "Agente YOLO",
            "status": "imagem_nao_encontrada",
            "modelo": MODELO_YOLO,
            "confianca_minima": CONFIANCA_MINIMA,
            "imagem_entrada": str(caminho_imagem),
            "imagem_anotada": None,
            "deteccoes": [],
            "resumo_deteccoes": {},
            "total_deteccoes": 0,
            "risco_yolo": "indisponivel",
            "observacao": "Imagem informada ao YOLO não foi encontrada."
        }

    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True
    )

    modelo = carregar_modelo_yolo()

    resultados = modelo.predict(
        source=str(caminho_imagem),
        conf=CONFIANCA_MINIMA,
        save=False,
        verbose=False
    )

    resultado = resultados[0]

    deteccoes = []

    if resultado.boxes is not None:
        for box in resultado.boxes:
            classe_id = int(box.cls[0])
            confianca = float(box.conf[0])
            nome_classe = modelo.names[classe_id]

            if confianca < CONFIANCA_MINIMA:
                continue

            deteccoes.append({
                "classe": nome_classe,
                "confianca": round(confianca * 100, 2)
            })

    resumo = resumir_deteccoes(deteccoes)

    risco_yolo = classificar_risco_yolo(deteccoes)

    nome_saida = (
        caminho_imagem.stem
        + "_yolo.png"
    )

    caminho_saida = (
        PASTA_SAIDA
        / nome_saida
    )

    imagem_anotada = resultado.plot()

    cv2.imwrite(
        str(caminho_saida),
        imagem_anotada
    )

    observacao = gerar_observacao(
        total_deteccoes=len(deteccoes),
        risco_yolo=risco_yolo
    )

    return {
        "agente": "Agente YOLO",
        "status": "sucesso",
        "modelo": MODELO_YOLO,
        "confianca_minima": CONFIANCA_MINIMA,
        "imagem_entrada": str(caminho_imagem),
        "imagem_anotada": str(caminho_saida),
        "deteccoes": deteccoes,
        "resumo_deteccoes": resumo,
        "total_deteccoes": len(deteccoes),
        "risco_yolo": risco_yolo,
        "observacao": observacao
    }