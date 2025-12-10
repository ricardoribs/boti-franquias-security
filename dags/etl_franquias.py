from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import random
import hashlib # <--- BIBLIOTECA DE CRIPTOGRAFIA (SEGURANÇA)

# --- FUNÇÕES ---

def encrypt_pii(texto):
    """
    REQUISITO DA VAGA: Implementar segurança e criptografia.
    Recebe um E-mail real e transforma num código (Hash) impossível de reverter.
    Isso protege o dado do cliente (LGPD).
    """
    if texto:
        # Transforma "joao@gmail.com" em "a5b3c9..."
        return hashlib.sha256(texto.encode()).hexdigest()
    return None

def extrair_dados_api_mock():
    """
    REQUISITO DA VAGA: Extração de dados via APIs de terceiros.
    Simula o Salesforce (CRM) enviando dados de vendas.
    """
    dados = []
    franquias = [101, 102, 103, 104, 105]
    
    # Gera 50 vendas falsas
    for _ in range(50):
        email_fake = f"cliente{random.randint(1,9999)}@gmail.com"
        
        dados.append({
            "id_venda": random.randint(10000, 99999),
            "id_franquia": random.choice(franquias),
            "valor_venda": round(random.uniform(50.0, 500.0), 2),
            "data_venda": datetime.now().strftime("%Y-%m-%d"),
            "email_cliente": email_fake # DADO SENSÍVEL (PERIGOSO!)
        })
    
    df = pd.DataFrame(dados)
    
    # --- APLICAÇÃO DA SEGURANÇA ---
    # Aqui a mágica acontece. Criptografamos o e-mail antes de salvar.
    df['email_hash'] = df['email_cliente'].apply(encrypt_pii)
    
    # Removemos a coluna original para ninguém ver o e-mail real
    df_seguro = df.drop(columns=['email_cliente'])
    
    # Salva num arquivo temporário
    df_seguro.to_csv("/tmp/vendas_franquias_seguro.csv", index=False)
    print("Dados extraídos e criptografados com sucesso!")

def carregar_no_banco():
    """
    REQUISITO DA VAGA: Carga em Data Warehousing.
    Lê o CSV seguro e salva no Postgres.
    """
    # Conecta no banco do Airflow
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    engine = pg_hook.get_sqlalchemy_engine()
    
    # Lê o arquivo
    df = pd.read_csv("/tmp/vendas_franquias_seguro.csv")
    
    # Salva na tabela 'vendas_raw'
    df.to_sql('vendas_raw', engine, if_exists='replace', index=False)
    print("Dados carregados no Banco de Dados!")

# --- DAG (O FLUXO) ---
with DAG(
    dag_id="boti_franquias_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    # Passo 1: Extrair e Criptografar
    t1 = PythonOperator(
        task_id="extracao_segura_api",
        python_callable=extrair_dados_api_mock
    )

    # Passo 2: Carregar no Banco
    t2 = PythonOperator(
        task_id="carga_banco_dados",
        python_callable=carregar_no_banco
    )

    t1 >> t2