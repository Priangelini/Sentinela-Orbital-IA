from pathlib import Path
import joblib

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

from xgboost import XGBClassifier


BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_DATASET = BASE_DIR / "data" / "processed" / "dataset_treinamento.csv"

PASTA_MODELOS = BASE_DIR / "src" / "models"
PASTA_IMAGENS = BASE_DIR / "docs" / "imagens"

ARQUIVO_MODELO = PASTA_MODELOS / "modelo_xgboost.pkl"
ARQUIVO_LABEL_ENCODER = PASTA_MODELOS / "label_encoder.pkl"

ARQUIVO_MATRIZ_CONFUSAO = PASTA_IMAGENS / "matriz_confusao_xgboost.png"
ARQUIVO_IMPORTANCIA = PASTA_IMAGENS / "importancia_features_xgboost.png"


def main():
    print("Iniciando treinamento do modelo XGBoost...\n")

    if not ARQUIVO_DATASET.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {ARQUIVO_DATASET}")

    df = pd.read_csv(ARQUIVO_DATASET)

    features = [
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

    alvo = "classe_risco"

    X = df[features]
    y = df[alvo]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.25,
        random_state=42,
        stratify=y_encoded
    )

    modelo = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42
    )

    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    print("Treinamento finalizado!\n")
    print("Classes do modelo:")
    for indice, classe in enumerate(label_encoder.classes_):
        print(f"{indice}: {classe}")

    print("\nRelatório de classificação:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=label_encoder.classes_
        )
    )

    PASTA_MODELOS.mkdir(parents=True, exist_ok=True)
    PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)

    joblib.dump(modelo, ARQUIVO_MODELO)
    joblib.dump(label_encoder, ARQUIVO_LABEL_ENCODER)

    matriz = confusion_matrix(y_test, y_pred)

    display = ConfusionMatrixDisplay(
        confusion_matrix=matriz,
        display_labels=label_encoder.classes_
    )

    display.plot(values_format="d")
    plt.title("Matriz de Confusão - XGBoost")
    plt.tight_layout()
    plt.savefig(ARQUIVO_MATRIZ_CONFUSAO, dpi=300)
    plt.close()

    importancia = pd.DataFrame({
        "feature": features,
        "importancia": modelo.feature_importances_
    }).sort_values(by="importancia", ascending=True)

    plt.figure(figsize=(8, 6))
    plt.barh(importancia["feature"], importancia["importancia"])
    plt.title("Importância das Variáveis - XGBoost")
    plt.xlabel("Importância")
    plt.tight_layout()
    plt.savefig(ARQUIVO_IMPORTANCIA, dpi=300)
    plt.close()

    print("\nArquivos gerados:")
    print(f"Modelo: {ARQUIVO_MODELO}")
    print(f"Label Encoder: {ARQUIVO_LABEL_ENCODER}")
    print(f"Matriz de Confusão: {ARQUIVO_MATRIZ_CONFUSAO}")
    print(f"Importância das Variáveis: {ARQUIVO_IMPORTANCIA}")


if __name__ == "__main__":
    main()