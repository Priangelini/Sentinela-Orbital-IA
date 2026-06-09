from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_CLIMA = BASE_DIR / "data" / "raw" / "clima_openmeteo.csv"
ARQUIVO_FOCOS = BASE_DIR / "data" / "raw" / "focos_calor.csv"
ARQUIVO_NDVI = BASE_DIR / "data" / "raw" / "ndvi_gee_mensal.csv"

ARQUIVO_SAIDA = BASE_DIR / "data" / "processed" / "dataset_treinamento.csv"


def main():
    print("Preparando dataset de treinamento...\n")

    clima = pd.read_csv(ARQUIVO_CLIMA)
    focos = pd.read_csv(ARQUIVO_FOCOS)
    ndvi = pd.read_csv(ARQUIVO_NDVI)

    clima["data"] = pd.to_datetime(clima["data"])
    focos["data"] = pd.to_datetime(focos["data"])

    clima["ano_mes"] = clima["data"].dt.strftime("%Y-%m")

    dataset = clima.merge(
        focos,
        on=["municipio", "estado", "bioma", "data"],
        how="left"
    )

    dataset = dataset.merge(
        ndvi[["municipio", "estado", "bioma", "ano_mes", "ndvi_medio"]],
        on=["municipio", "estado", "bioma", "ano_mes"],
        how="left"
    )

    dataset["focos_calor"] = dataset["focos_calor"].fillna(0)
    dataset["frp_total"] = dataset["frp_total"].fillna(0)
    dataset["frp_medio"] = dataset["frp_medio"].fillna(0)
    dataset["fonte_focos"] = dataset["fonte_focos"].fillna("SEM_FOCO_REGISTRADO")

    dataset["ndvi_medio"] = dataset["ndvi_medio"].fillna(
        dataset["ndvi_medio"].median()
    )

    dataset["mes"] = dataset["data"].dt.month
    dataset["dia_semana"] = dataset["data"].dt.dayofweek

    temp_norm = dataset["temperatura_media"] / dataset["temperatura_media"].max()
    vento_norm = dataset["vento_medio"] / dataset["vento_medio"].max()
    focos_norm = dataset["focos_calor"] / max(dataset["focos_calor"].max(), 1)
    frp_norm = dataset["frp_total"] / max(dataset["frp_total"].max(), 1)

    umidade_inversa = 1 - (dataset["umidade_media"] / 100)
    chuva_inversa = 1 - (
        dataset["precipitacao"] / max(dataset["precipitacao"].max(), 1)
    )
    ndvi_inverso = 1 - dataset["ndvi_medio"]

    dataset["score_risco"] = (
        0.20 * temp_norm +
        0.20 * umidade_inversa +
        0.15 * vento_norm +
        0.15 * chuva_inversa +
        0.20 * focos_norm +
        0.05 * frp_norm +
        0.05 * ndvi_inverso
    )

    dataset["score_risco"] = dataset["score_risco"].clip(0, 1).round(4)

    # Classificação por percentis para evitar desbalanceamento extremo.
    limite_baixo = dataset["score_risco"].quantile(0.33)
    limite_medio = dataset["score_risco"].quantile(0.66)

    def classificar_risco_por_percentil(score):
        if score <= limite_baixo:
            return "baixo"
        if score <= limite_medio:
            return "medio"
        return "alto"

    dataset["classe_risco"] = dataset["score_risco"].apply(
        classificar_risco_por_percentil
    )

    colunas_finais = [
        "municipio",
        "estado",
        "bioma",
        "latitude",
        "longitude",
        "data",
        "ano_mes",
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
        "fonte_focos",
        "score_risco",
        "classe_risco",
    ]

    dataset_final = dataset[colunas_finais]

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    dataset_final.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")

    print("Dataset preparado com sucesso!")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"Total de registros: {len(dataset_final)}")

    print("\nLimites usados para classificação:")
    print(f"Baixo <= {limite_baixo:.4f}")
    print(f"Médio <= {limite_medio:.4f}")
    print(f"Alto  > {limite_medio:.4f}")

    print("\nDistribuição de risco:")
    print(dataset_final["classe_risco"].value_counts())


if __name__ == "__main__":
    main()