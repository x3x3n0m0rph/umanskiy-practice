FROM python:3.10-slim
RUN pip install --no-cache-dir psycopg2-binary sqlalchemy requests
RUN pip install --no-cache-dir matplotlib
RUN mkdir app
COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "-u", "run.py"]