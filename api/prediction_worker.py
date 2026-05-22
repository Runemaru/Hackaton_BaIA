import asyncio

from Hackaton_BaIA.api.weather_client import fetch_open_meteo_data
from Hackaton_BaIA.api.ml_predictor import MLPredictor


predictor = MLPredictor()

async def consume_prediction_events(callback):
    while True:
        try:
            print("Gerando previsão...", flush=True)

            open_meteo_data = fetch_open_meteo_data()
            print("Dados Open-Meteo recebidos", flush=True)

            prediction = predictor.predict(open_meteo_data)

            await callback(prediction)
            print("Previsão enviada via WebSocket", flush=True)

        except Exception as error:
            print("Erro ao gerar previsão:", repr(error), flush=True)

        await asyncio.sleep(60)
