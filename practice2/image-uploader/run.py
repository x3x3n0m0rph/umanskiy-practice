import time
import base64
import requests
import logging

from app.models import Base, WeatherReport
from app.utils import pass_or_die

logging.basicConfig(level="INFO", format=pass_or_die("DEFAULT_LOG_FORMAT"))

from http import HTTPStatus
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

# init connections
while True:
    try:
        eng = create_engine(pass_or_die("DB_CONNECTION_URL"))
        Base.metadata.bind = eng
        sess = Session(eng)
        break
    except OperationalError as ex:
        logging.warning(f"Unable to connect to DB: {ex}. Repeating...")
        continue
    except Exception as ex:
        logging.fatal(ex)
        exit(1)

interval = int(pass_or_die("REQUEST_INTERVAL"))
api_host = pass_or_die("IMAGE_API_HOST")
api_method = pass_or_die("IMAGE_API_METHOD")
api_key = pass_or_die("IMAGE_API_KEY")

api_url = f"https://{api_host}/{api_method}"

while True:
    try:
        report = sess.query(WeatherReport).filter(
            WeatherReport.upload_status == None
        ).one_or_none()
        if report is None:
            continue

        params = {
            'image': base64.b64encode(report.image_blob),
            'name': f"Weather report #{report.id}",
            'expiration ': 60000,
            'key': api_key
        }
        r = requests.post(
            api_url,
            params
        )
        report.uploaded_at = datetime.now()
        report.upload_status = r.status_code

        if r.status_code == HTTPStatus.OK:
            result = r.json()
            report.upload_url = result['data']['url']
            logging.info(f"New report uploaded: {report.upload_url}")
        else:
            logging.warning(f"Unexpected status code: {r.status_code}")
            logging.warning(f"Response: {r.json()}")

        sess.add(report)
        sess.commit()
    except Exception as ex:
        sess.rollback()
        logging.error(ex)
    finally:
        time.sleep(interval)
