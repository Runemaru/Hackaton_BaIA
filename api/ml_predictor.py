import joblib
import numpy as np
import pandas as pd


REGION = "Salvador - BA"

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


class MLPredictor:
    def __init__(self):
        self.modelos_chuva = joblib.load("models/modelos_chuva_7d.pkl")
        self.modelos_seca = joblib.load("models/modelos_seca_7d.pkl")
        self.modelos_queima = joblib.load("models/modelos_queima_7d.pkl")

    def prepare_dataframe(self, open_meteo_response):
        hourly = open_meteo_response["hourly"]

        df = pd.DataFrame({
            "TEMPO_HORA": pd.to_datetime(hourly["time"]),
            "TEMPERATURA_DO_AR": hourly["temperature_2m"],
            "UMIDADE_RELATIVA": hourly["relative_humidity_2m"],
            "PRECIPITACAO_TOTAL_HORARIO": hourly["precipitation"],
            "PRESSAO_ATMOSFERICA": hourly["surface_pressure"],
            "VENTO_VELOCIDADE": hourly["wind_speed_10m"],
            "RADIACAO_GLOBAL": hourly["shortwave_radiation"],
            "PRECIPITATION_PROBABILITY": hourly["precipitation_probability"],
            "WIND_GUSTS": hourly["wind_gusts_10m"],
            "CLOUD_COVER": hourly["cloud_cover"],
            "SOIL_TEMPERATURE": hourly["soil_temperature_0cm"],
            "SOIL_MOISTURE": hourly["soil_moisture_0_to_1cm"],
        })

        df = df.dropna().sort_values("TEMPO_HORA")

        df["HORA"] = df["TEMPO_HORA"].dt.hour * 100

        df["DELTA_PRESSAO_3H"] = df["PRESSAO_ATMOSFERICA"].diff(3).fillna(0)

        fator_pressao = np.clip(-df["DELTA_PRESSAO_3H"], 0, 5) * 6

        df["CHANCE_CHUVA"] = np.clip(
            (df["UMIDADE_RELATIVA"] * 0.45)
            + (df["PRECIPITATION_PROBABILITY"] * 0.45)
            + fator_pressao,
            0,
            100,
        ).round(1)

        angstrom_index = (
            df["UMIDADE_RELATIVA"] / 20
        ) + ((df["TEMPERATURA_DO_AR"] - 27) / 10)

        wind_factor = np.clip(df["WIND_GUSTS"] / 40, 0, 1) * 10
        soil_factor = np.clip((0.4 - df["SOIL_MOISTURE"]) * 100, 0, 20)

        df["CHANCE_QUEIMA"] = np.clip(
            (((4.0 - angstrom_index) / 3.0) * 100)
            + wind_factor
            + soil_factor,
            0,
            100,
        ).round(1)

        # Mantém a lógica mais compatível com o modelo original.
        balanco_horario = df["PRECIPITACAO_TOTAL_HORARIO"].fillna(0)
        balanco_7dias = balanco_horario.rolling(window=168, min_periods=1).sum()

        capacidade_agua_solo = 50.0

        df["SEVERIDADE_SECA"] = (
            np.clip(-balanco_7dias, 0, capacidade_agua_solo)
            / capacidade_agua_solo
        ) * 100

        df["SEVERIDADE_SECA"] = df["SEVERIDADE_SECA"].round(1)

        df["TEMP_MEDIA_24H"] = df["TEMPERATURA_DO_AR"].rolling(
            window=24,
            min_periods=1,
        ).mean()

        df["UMIDADE_MEDIA_24H"] = df["UMIDADE_RELATIVA"].rolling(
            window=24,
            min_periods=1,
        ).mean()

        df["CHUVA_ACUM_24H"] = df["PRECIPITACAO_TOTAL_HORARIO"].rolling(
            window=24,
            min_periods=1,
        ).sum()

        return df

    def get_daily_rows(self, df):
        today = pd.Timestamp.now().normalize()

        future_df = df[df["TEMPO_HORA"].dt.normalize() > today].copy()

        daily_rows = []

        for _, group in future_df.groupby(future_df["TEMPO_HORA"].dt.date):
            group = group.copy()

            # escolhe o horário mais próximo de 12h
            group["DISTANCE_TO_NOON"] = abs(group["TEMPO_HORA"].dt.hour - 12)

            selected_row = group.sort_values("DISTANCE_TO_NOON").head(1)

            daily_rows.append(selected_row)

        if not daily_rows:
            return pd.DataFrame()

        return pd.concat(daily_rows).head(7)

    def classify_rain(self, value):
        if value <= 30:
            return "BAIXA"
        if value <= 60:
            return "MÉDIA"
        return "ALTA"

    def classify_drought(self, value):
        if value <= 30:
            return "BAIXA"
        if value <= 60:
            return "MÉDIA"
        return "ALTA"

    def classify_burning(self, value):
        if value <= 0:
            return "NULA"
        if value <= 24:
            return "BAIXO RISCO"
        if value <= 50:
            return "MÉDIO RISCO"
        if value <= 75:
            return "RISCO CONSIDERÁVEL"
        if value <= 90:
            return "RISCO ELEVADO"
        return "RISCO PROVÁVEL"

    def predict(self, open_meteo_response):
        df = self.prepare_dataframe(open_meteo_response)
        daily_rows = self.get_daily_rows(df)

        week_forecast = []

        for index, (_, row) in enumerate(daily_rows.iterrows(), start=1):
            model_day = min(index, 7)

            input_row = row[FEATURES].to_frame().T.astype(float)

            rain = np.clip(
                self.modelos_chuva[model_day].predict(input_row)[0],
                0,
                100,
            )

            drought = np.clip(
                self.modelos_seca[model_day].predict(input_row)[0],
                0,
                100,
            )

            burning = np.clip(
                self.modelos_queima[model_day].predict(input_row)[0],
                0,
                100,
            )

            forecast_date = row["TEMPO_HORA"]

            rain = round(float(rain), 2)
            drought = round(float(drought), 2)
            burning = round(float(burning), 2)

            week_forecast.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "date_label": forecast_date.strftime("%d/%m/%Y"),
                "hour_label": forecast_date.strftime("%H:%M"),

                "rain": {
                    "percentage": rain,
                    "level": self.classify_rain(rain),
                },

                "drought": {
                    "percentage": drought,
                    "level": self.classify_drought(drought),
                },

                "burning": {
                    "percentage": burning,
                    "level": self.classify_burning(burning),
                },

                "debug_inputs": {
                    "temperature": round(float(row["TEMPERATURA_DO_AR"]), 2),
                    "humidity": round(float(row["UMIDADE_RELATIVA"]), 2),
                    "precipitation": round(float(row["PRECIPITACAO_TOTAL_HORARIO"]), 2),
                    "pressure": round(float(row["PRESSAO_ATMOSFERICA"]), 2),
                    "wind_speed": round(float(row["VENTO_VELOCIDADE"]), 2),
                    "wind_gusts": round(float(row["WIND_GUSTS"]), 2),
                    "soil_moisture": round(float(row["SOIL_MOISTURE"]), 4),
                    "cloud_cover": round(float(row["CLOUD_COVER"]), 2),
                }
            })

        generated_at = pd.Timestamp.now(tz="America/Bahia")

        return {
            "event_type": "weekly_environment_forecast",
            "source": "open_meteo_ml_model",
            "region": REGION,
            "generated_at": generated_at.strftime("%Y-%m-%d %H:%M"),
            "generated_at_label": generated_at.strftime("%d/%m/%Y %H:%M"),
            "tomorrow": week_forecast[0] if week_forecast else None,
            "week_forecast": week_forecast,
        }
