#Ideia de como utilizar o joblib, mas basicamente segue a utilização de brokers e mensageria pra conseguir fazer essa ponte entre o dado, e nosso modelo já criado desta vez.
import joblib
import numpy as np
import pandas as pd

class ClimaPredictor:
    def __init__(self):
        # 1. Carrega os modelos salvos ao iniciar o servidor
        self.modelos_chuva = joblib.load('modelos_chuva_5d.pkl')
        self.modelos_seca = joblib.load('modelos_seca_5d.pkl')
        self.modelos_queima = joblib.load('modelos_queima_7d.pkl')
        
    def _processar_tempo_ciclico(self, data_hora_str):
        # Converte a string de data para calcular Seno e Cosseno
        dt = pd.to_datetime(data_hora_str)
        hora = dt.hour
        mes = dt.month
        
        return {
            'HORA_SIN': np.sin(2 * np.pi * hora / 24.0),
            'HORA_COS': np.cos(2 * np.pi * hora / 24.0),
            'MES_SIN': np.sin(2 * np.pi * mes / 12.0),
            'MES_COS': np.cos(2 * np.pi * mes / 12.0)
        }

    def prever(self, dados_brutos: dict):
        """
        Recebe um dicionário/JSON com os dados atuais do sensor
        e retorna as previsões futuras.
        """
        # 1. Processa o tempo cíclico
        tempo_ciclico = self._processar_tempo_ciclico(dados_brutos['timestamp'])
        
        # 2. Monta o dicionário final de features esperado pelo LightGBM
        features_input = {
            'HORA_SIN': tempo_ciclico['HORA_SIN'],
            'HORA_COS': tempo_ciclico['HORA_COS'],
            'MES_SIN': tempo_ciclico['MES_SIN'],
            'MES_COS': tempo_ciclico['MES_COS'],
            'PRECIPITACAO_TOTAL_HORARIO': dados_brutos['precipitacao'],
            'RADIACAO_GLOBAL': dados_brutos['radiacao'],
            'PRESSAO_ATMOSFERICA': dados_brutos['pressao'],
            'TEMPERATURA_DO_AR': dados_brutos['temperatura'],
            'UMIDADE_RELATIVA': dados_brutos['umidade'],
            'VENTO_VELOCIDADE': dados_brutos['vento_velocidade'],
            'CHANCE_CHUVA': dados_brutos['chance_chuva_atual'],
            'SEVERIDADE_SECA': dados_brutos['severidade_seca_atual'],
            'CHANCE_QUEIMA': dados_brutos['chance_queima_atual'],
            'TEMP_MEDIA_24H': dados_brutos['temp_media_24h'],
            'UMIDADE_MEDIA_24H': dados_brutos['umidade_media_24h'],
            'CHUVA_ACUM_24H': dados_brutos['chuva_acum_24h']
        }
        
        # Converte para DataFrame (formato que o Scikit-Learn/LGBM exige)
        df_input = pd.DataFrame([features_input])
        
        # 3. Executa as previsões diárias
        previsoes = {
            "chuva_5dias": [float(np.clip(self.modelos_chuva[d].predict(df_input)[0], 0, 100).round(1)) for d in range(1, 6)],
            "seca_5dias": [float(np.clip(self.modelos_seca[d].predict(df_input)[0], 0, 100).round(1)) for d in range(1, 6)],
            "queima_7dias": [float(np.clip(self.modelos_queima[d].predict(df_input)[0], 0, 100).round(1)) for d in range(1, 8)]
        }
        
        return previsoes

# --- EXEMPLO DE EXECUÇÃO ---
if __name__ == "__main__":
    predictor = ClimaPredictor()
    
    # Exemplo de payload JSON enviado por um Broker ou API
    payload_sensor = {
        "timestamp": "2025-02-15 14:00:00",
        "precipitacao": 0.0,
        "radiacao": 850.0,
        "pressao": 1012.0,
        "temperatura": 31.5,
        "umidade": 50.0,
        "vento_velocidade": 2.5,
        "chance_chuva_atual": 15.0,
        "severidade_seca_atual": 10.0,
        "chance_queima_atual": 25.0,
        "temp_media_24h": 28.0,
        "umidade_media_24h": 60.0,
        "chuva_acum_24h": 2.0
    }
    
    resultado = predictor.prever(payload_sensor)
    print(resultado)