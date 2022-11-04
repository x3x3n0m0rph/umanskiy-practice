FROM python:3.10-slim
RUN mkdir app
COPY app app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "-u", "run.py"]
