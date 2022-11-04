FROM binakot/postgresql-postgis-timescaledb:latest
RUN apk add wget \
    && wget -q https://timescaledata.blob.core.windows.net/datasets/nyc_data.tar.gz \
    && mkdir data sql \
    && tar -xzf nyc_data.tar.gz -C ./data \
    && rm nyc_data.tar.gz 
COPY startup.psql ./
COPY wait-for-it.sh ./
COPY nyc_data_contagg.sql ./sql
RUN chmod +x wait-for-it.sh