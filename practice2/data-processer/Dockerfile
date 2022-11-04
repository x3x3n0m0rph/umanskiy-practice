FROM python:3.10-slim
RUN mkdir app
WORKDIR app
COPY ./app ./
RUN pip install --no-cache-dir psycopg2 sqlalchemy requests
RUN pip install --no-cache-dir matplotlib
ENTRYPOINT ["python", "-u", "run.py"]