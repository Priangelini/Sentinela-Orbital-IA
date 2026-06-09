import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta


BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_MUNICIPIOS = BASE_DIR / "data" / "external" / "municipios_monitorados.csv"
ARQUIVO_SAIDA = BASE_DIR / "data" / "raw" / "clima_openmeteo.csv"


def coletar_clima_openmeteo(latitude, longitude, data_inicio, data_fim):
    url = "https://archive-api.open-meteo.com/v1/archive"

    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": data_inicio,
        "end_date": data_fim,
        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_mean",
        ],
        "timezone": "America/Sao_Paulo",
    }

    resposta = requests.get(url, params=parametros, timeout=30)
    resposta.raise_for_status()

    return resposta.json()


def main():
    if not ARQUIVO_MUNICIPIOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_MUNICIPIOS}")

    municipios = pd.read_csv(ARQUIVO_MUNICIPIOS)

    data_fim = date.today() - timedelta(days=2)
    data_inicio = data_fim - timedelta(days=30)

    registros = []

    for _, linha in municipios.iterrows():
        municipio = linha["municipio"]
        estado = linha["estado"]
        bioma = linha["bioma"]
        latitude = linha["latitude"]
        longitude = linha["longitude"]

        print(f"Coletando dados climáticos: {municipio} - {estado}")

        dados = coletar_clima_openmeteo(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio.isoformat(),
            data_fim=data_fim.isoformat(),
        )

        daily = dados.get("daily", {})

        for i, data_ref in enumerate(daily.get("time", [])):
            registros.append({
                "municipio": municipio,
                "estado": estado,
                "bioma": bioma,
                "latitude": latitude,
                "longitude": longitude,
                "data": data_ref,
                "temperatura_media": daily["temperature_2m_mean"][i],
                "umidade_media": daily["relative_humidity_2m_mean"][i],
                "precipitacao": daily["precipitation_sum"][i],
                "vento_medio": daily["wind_speed_10m_mean"][i],
            })

    df = pd.DataFrame(registros)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")

    print("\nColeta finalizada com sucesso!")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"Total de registros: {len(df)}")


if __name__ == "__main__":
    main()