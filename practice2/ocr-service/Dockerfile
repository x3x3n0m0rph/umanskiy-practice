FROM python:3.10-slim
RUN pip install --no-cache-dir psycopg2-binary sqlalchemy requests
RUN apt-get update && apt-get -y install tesseract-ocr
RUN pip install --no-cache-dir pytesseract flask
RUN mkdir app
COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "-u", "run.py"]