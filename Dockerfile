FROM apache/airflow:2.9.1
USER root
RUN apt-get update && apt-get install -y git libpq-dev gcc && apt-get clean
USER airflow
# Instalando as bibliotecas essenciais para o projeto
RUN pip install --no-cache-dir apache-airflow-providers-postgres pandas psycopg2-binary