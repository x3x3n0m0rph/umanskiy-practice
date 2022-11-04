import time
import io
import logging
import random
import matplotlib.pyplot as plt

from app.models import Base, Location, WeatherStatus, WeatherReport
from app.utils import pass_or_die

logging.basicConfig(level="INFO", format=pass_or_die("DEFAULT_LOG_FORMAT"))

from http import HTTPStatus
from datetime import datetime, timedelta
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

report_interval = int(pass_or_die("REPORT_INTERVAL"))
DPI = 96

report_width = int(pass_or_die("GRAPICS_WIDTH"))
report_height = int(pass_or_die("GRAPICS_HEIGHT"))

while True:
    try:
        # creating the graph

        fig, axs = plt.subplots(3)
        fig.set_size_inches(report_width/DPI, report_height/DPI)
        fig.suptitle(f"Weather statistics in last {report_interval} sec")

        report = WeatherReport(
            interval_start=datetime.now() - timedelta(seconds=report_interval),
            interval_stop=datetime.now() 
        )

        # generating the report

        locations = sess.query(Location).all()
        for location in locations:

            # pseudorandom color for each location
            rand = random.Random(location.id*2 + 5)
            color = (rand.random(),rand.random(),rand.random())

            query = sess.query(WeatherStatus).filter(
                WeatherStatus.status_code == HTTPStatus.OK,
                WeatherStatus.created_at >= report.interval_start,
                WeatherStatus.created_at < report.interval_stop,
                WeatherStatus.location == location
            ).all()

            # some mapping
            dts = [x.created_at for x in query]
            points = [(x.temperature, x.humidity, x.pressure) for x in query]

            # drawing 3 lines per location for each graph
            axs[0].plot(dts, [x[0] for x in points], '-o', color=color, label=location.name or f"{location.lat};{location.lon}")
            axs[1].plot(dts, [x[1] for x in points], '--x', color=color, label=location.name or f"{location.lat};{location.lon}")
            axs[2].plot(dts, [x[2] for x in points], '-.+', color=color, label=location.name or f"{location.lat};{location.lon}")
        axs[0].set_title("Temperature")
        axs[1].set_title("Humidity")
        axs[2].set_title("Pressure")
        _ = [x.legend() for x in axs]

        # save to db
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        report.image_blob = buf.read()
        sess.add(report)
        sess.commit()
        
        logging.info("New report generated")

    except Exception as ex:
        sess.rollback()
        logging.warn(ex)
    finally:
        time.sleep(report_interval)
