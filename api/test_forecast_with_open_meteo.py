import joblib
import numpy as np
import pandas as pd
import requests
from datetime import timedelta


MODELS_PATH = "models"

REGION = "Salvador - BA"
LATITUDE = -12.9714
LONGITUDE = -38.5014

FEATURES = [
    "HORA",
    "PRECIPITACAO_TOTAL_HORARIO",
    "RADIACAO_GLOBAL",
    "PRESSAO_ATMOSFERICA",
    "TEMPERATURA_DO_AR",
    "UMIDADE_RELATIVA",
    "VENTO_VELOCIDADE",
    "CHANCE_CHUVA",
    "SEVERIDADE_SECA",
    "CHANCE_QUEIMA",
    "TEMP_MEDIA_24H",
    "UMIDADE_MEDIA_24H",
    "CHUVA_ACUM_24H",
]


def fetch_open_meteo_data():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timezone": "America/Bahia",
        "past_days": 1,
        "forecast_days": 7,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "surface_pressure",
            "wind_speed_10m",
            "shortwave_radiation",
        ]),
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def prepare_dataframe(open_meteo_response):
    hourly = open_meteo_response["hourly"]

    df = pd.DataFrame({
        "TEMPO_HORA": pd.to_datetime(hourly["time"]),
        "TEMPERATURA_DO_AR": hourly["temperature_2m"],
        "UMIDADE_RELATIVA": hourly["relative_humidity_2m"],
        "PRECIPITACAO_TOTAL_HORARIO": hourly["precipitation"],
        "PRESSAO_ATMOSFERICA": hourly["surface_pressure"],
        "VENTO_VELOCIDADE": hourly["wind_speed_10m"],
        "RADIACAO_GLOBAL": hourly["shortwave_radiation"],
    })

    df = df.dropna().sort_values("TEMPO_HORA")

    df["HORA"] = df["TEMPO_HORA"].dt.hour * 100

    df["DELTA_PRESSAO_3H"] = df["PRESSAO_ATMOSFERICA"].diff(3).fillna(0)

    fator_pressao = np.clip(-df["DELTA_PRESSAO_3H"], 0, 5) * 6

    chance_chuva = (df["UMIDADE_RELATIVA"] * 0.7) + fator_pressao
    df["CHANCE_CHUVA"] = np.clip(chance_chuva, 0, 100).round(1)

    angstrom_index = (
        df["UMIDADE_RELATIVA"] / 20
    ) + ((df["TEMPERATURA_DO_AR"] - 27) / 10)

    chance_queima = ((4.0 - angstrom_index) / 3.0) * 100
    df["CHANCE_QUEIMA"] = np.clip(chance_queima, 0, 100).round(1)

    balanco_horario = df["PRECIPITACAO_TOTAL_HORARIO"].fillna(0)
    balanco_7dias = balanco_horario.rolling(window=168, min_periods=1).sum()

    capacidade_agua_solo = 50.0

    severidade_seca = (
        np.clip(-balanco_7dias, 0, capacidade_agua_solo)
        / capacidade_agua_solo
    ) * 100

    df["SEVERIDADE_SECA"] = severidade_seca.round(1)

    df["TEMP_MEDIA_24H"] = df["TEMPERATURA_DO_AR"].rolling(
        window=24,
        min_periods=1
    ).mean()

    df["UMIDADE_MEDIA_24H"] = df["UMIDADE_RELATIVA"].rolling(
        window=24,
        min_periods=1
    ).mean()

    df["CHUVA_ACUM_24H"] = df["PRECIPITACAO_TOTAL_HORARIO"].rolling(
        window=24,
        min_periods=1
    ).sum()

    return df


def get_daily_rows(df):
    """
    Pega uma linha representativa por dia futuro.
    Aqui estou usando 12:00 como referência.
    Se não existir 12:00, pega a linha mais próxima.
    """

    now = pd.Timestamp.now().normalize()

    future_df = df[df["TEMPO_HORA"].dt.normalize() > now].copy()

    daily_rows = []

    for day, group in future_df.groupby(future_df["TEMPO_HORA"].dt.date):
        group = group.copy()

        group["DISTANCE_TO_NOON"] = abs(group["TEMPO_HORA"].dt.hour - 12)

        selected_row = group.sort_values("DISTANCE_TO_NOON").head(1)

        daily_rows.append(selected_row)

    if not daily_rows:
        return pd.DataFrame()

    return pd.concat(daily_rows).head(7)


def load_models():
    modelos_chuva = joblib.load(f"{MODELS_PATH}/modelos_chuva_7d.pkl")
    modelos_seca = joblib.load(f"{MODELS_PATH}/modelos_seca_7d.pkl")
    modelos_queima = joblib.load(f"{MODELS_PATH}/modelos_queima_7d.pkl")

    return modelos_chuva, modelos_seca, modelos_queima


def predict_with_future_rows(df):
    modelos_chuva, modelos_seca, modelos_queima = load_models()

    daily_rows = get_daily_rows(df)

    results = []

    for index, (_, row) in enumerate(daily_rows.iterrows(), start=1):
        model_day = min(index, 7)

        input_row = row[FEATURES].to_frame().T.astype(float)

        rain_prediction = np.clip(
            modelos_chuva[model_day].predict(input_row)[0],
            0,
            100
        )

        drought_prediction = np.clip(
            modelos_seca[model_day].predict(input_row)[0],
            0,
            100
        )

        burning_prediction = np.clip(
            modelos_queima[model_day].predict(input_row)[0],
            0,
            100
        )

        results.append({
            "day": index,
            "date": row["TEMPO_HORA"],
            "input_temperature": row["TEMPERATURA_DO_AR"],
            "input_humidity": row["UMIDADE_RELATIVA"],
            "input_precipitation": row["PRECIPITACAO_TOTAL_HORARIO"],
            "input_wind": row["VENTO_VELOCIDADE"],
            "input_pressure": row["PRESSAO_ATMOSFERICA"],
            "feature_chance_chuva": row["CHANCE_CHUVA"],
            "feature_chance_queima": row["CHANCE_QUEIMA"],
            "feature_severidade_seca": row["SEVERIDADE_SECA"],
            "pred_rain": round(float(rain_prediction), 2),
            "pred_drought": round(float(drought_prediction), 2),
            "pred_burning": round(float(burning_prediction), 2),
        })

    return results


def print_dataframe_debug(df):
    print("\n==============================")
    print("DADOS OPEN-METEO PROCESSADOS")
    print("==============================")

    print("\nIntervalo recebido:")
    print("Início:", df["TEMPO_HORA"].min())
    print("Fim:   ", df["TEMPO_HORA"].max())

    print("\nÚltimas 5 linhas processadas:")
    print(
        df[
            [
                "TEMPO_HORA",
                "TEMPERATURA_DO_AR",
                "UMIDADE_RELATIVA",
                "PRECIPITACAO_TOTAL_HORARIO",
                "PRESSAO_ATMOSFERICA",
                "VENTO_VELOCIDADE",
                "RADIACAO_GLOBAL",
                "CHANCE_CHUVA",
                "SEVERIDADE_SECA",
                "CHANCE_QUEIMA",
            ]
        ].tail()
    )


def print_predictions(results):
    print("\n==============================")
    print("PREVISÕES USANDO LINHAS FUTURAS")
    print("==============================")

    for item in results:
        print(f"\nDia {item['day']} - {item['date']}")
        print(
            f"Inputs Open-Meteo | "
            f"Temp: {item['input_temperature']}°C | "
            f"Umidade: {item['input_humidity']}% | "
            f"Chuva: {item['input_precipitation']}mm | "
            f"Vento: {item['input_wind']}km/h | "
            f"Pressão: {item['input_pressure']}hPa"
        )
        print(
            f"Features calculadas | "
            f"CHANCE_CHUVA: {item['feature_chance_chuva']} | "
            f"SEVERIDADE_SECA: {item['feature_severidade_seca']} | "
            f"CHANCE_QUEIMA: {item['feature_chance_queima']}"
        )
        print(
            f"Predições ML | "
            f"Chuva: {item['pred_rain']}% | "
            f"Seca: {item['pred_drought']}% | "
            f"Queima: {item['pred_burning']}%"
        )


def main():
    print("Buscando dados da Open-Meteo...")

    open_meteo_data = fetch_open_meteo_data()

    print("Preparando dataframe...")

    df = prepare_dataframe(open_meteo_data)

    print_dataframe_debug(df)

    print("\nGerando previsões...")

    results = predict_with_future_rows(df)

    print_predictions(results)


if __name__ == "__main__":
    main()
