import logging
import pytesseract
import time
import io
import json

from app.models import Base, OCRRequest
from app.utils import pass_or_die

logging.basicConfig(level="INFO", format=pass_or_die("DEFAULT_LOG_FORMAT"))

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from threading import Thread, Event
from PIL import Image
from datetime import datetime
from flask import request, Flask, jsonify
from pprint import pprint
from http import HTTPStatus
from pytesseract import Output

fetch_interval = int(pass_or_die("FETCH_INTERVAL"))

# init connections
while True:
    try:
        eng = create_engine(pass_or_die("DB_CONNECTION_URL"))
        Base.metadata.bind = eng
        Base.metadata.create_all()
        sess = Session(eng)
        break
    except OperationalError as ex:
        logging.warning(f"Unable to connect to DB: {ex}. Repeating...")
        continue
    except Exception as ex:
        logging.fatal(ex)
        exit(1)


app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def post_ocr_request():
    if request.headers.get('Content-Type').split("/")[0] == 'image':
        try:
            image_buffer = request.get_data()
            image = Image.open(io.BytesIO(image_buffer))
            logging.info(f"Received image: {image.info}")

            new_request = OCRRequest(
                user = request.remote_addr,
                image_blob = image_buffer
            )
            sess.add(new_request)
            sess.commit()
            return jsonify(new_request.serialize()), HTTPStatus.ACCEPTED
        except Exception as ex:
            logging.error(ex)
            return jsonify({"error": "Bad request"}), HTTPStatus.BAD_REQUEST
    else:
        return jsonify({"error": "Bad request"}), HTTPStatus.BAD_REQUEST


@app.route("/ocr/<int:id>", methods=["GET"])
def get_ocr_request(id):
    try:
        request = sess.get(OCRRequest, id)
        
        if request is None:
            return jsonify({"error": "Not found"}), HTTPStatus.NOT_FOUND
        else:
            return jsonify(request.serialize()), HTTPStatus.FOUND
    except Exception as ex:
        logging.error(ex)
        return jsonify({"error": "Bad request"}), HTTPStatus.BAD_REQUEST


class OCRProcesserThread(Thread):
    def __init__(self, group = None, target = None, name = "OCR Processing Thread", args = None, kwargs = None, *, daemon = None) -> None:
        self._stopped = Event()
        self._sess = Session(eng.connect())
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def soft_stop(self):
        self._stopped.set()

    def run(self) -> None:
        while not self._stopped.is_set():
            try:
                requests = self._sess.query(OCRRequest).filter(OCRRequest.status == 'waiting').order_by(asc(OCRRequest.created_at)).limit(10).all()
                if len(requests) > 0:
                    logging.info(f"Found {len(requests)} requests for OCR processing")
                for request in requests:
                    try:
                        image = Image.open(io.BytesIO(request.image_blob))
                        recog = pytesseract.image_to_boxes(image, output_type=Output.DICT)
                        logging.info(f"Request id={request.id} recognized as: {recog}")
                        request.result = json.dumps(recog)
                        request.status = 'success'
                        request.updated_at = datetime.now()

                        self._sess.merge(request)
                        self._sess.commit()
                    except Exception as ex:
                        logging.info(f"Request id={request.id} failed: {ex}")
                        request.status = 'failed'
                        request.updated_at = datetime.now()
                        self._sess.merge(request)
                        self._sess.commit()

            except Exception as ex:
                self._sess.rollback()
                logging.warning(ex)
            finally:
                time.sleep(fetch_interval)


processing_thread = OCRProcesserThread()
processing_thread.start()

app.run("0.0.0.0")