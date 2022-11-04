import requests
import time
import logging
logging.basicConfig(level="INFO")

from app.models import Base, Location, WeatherStatus
from app.utils import pass_or_die

from http import HTTPStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# init connections
try:
    eng = create_engine(pass_or_die("DB_CONNECTION_URL"))
    Base.metadata.bind = eng
    Base.metadata.create_all()
    sess = Session(eng)
except Exception as ex:
    logging.fatal(ex)
    exit(1)

api_host = pass_or_die("WEATHER_API_HOST")
api_method = pass_or_die("WEATHER_API_METHOD")
api_key = pass_or_die("WEATHER_API_KEY")
api_interval = int(pass_or_die("REQUEST_INTERVAL"))

api_url = f"http://{api_host}/{api_method}"

while True:
    try:
        locations = sess.query(Location).all()
        for location in locations:
            params = {
                'lat': location.lat,
                'lon': location.lon,
                'units': 'metric',
                'appid': api_key
            }
            r = requests.get(
                api_url,
                params
            )
            status = WeatherStatus(
                location=location,
                status_code = r.status_code
            )
            if r.status_code == HTTPStatus.OK:
                result = r.json()
                status.temperature = result['main']['temp']
                status.humidity = result['main']['humidity']
                status.pressure = result['main']['pressure']
            sess.add(status)
            sess.commit()
    except Exception as ex:
        sess.rollback()
        logging.warn(ex)
    finally:
        time.sleep(api_interval)
