import requests


LATITUDE = -12.9714
LONGITUDE = -38.5014


def fetch_open_meteo_data():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timezone": "America/Bahia",
        "past_days": 2,
        "forecast_days": 7,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "surface_pressure",
            "wind_speed_10m",
            "wind_gusts_10m",
            "shortwave_radiation",
            "cloud_cover",
            "soil_temperature_0cm",
            "soil_moisture_0_to_1cm",
        ]),
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()
