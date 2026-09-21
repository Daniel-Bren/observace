import os
import psycopg
from dotenv import load_dotenv
from coletor_municipios_tce import buscar_municipios_tce, transformar_municipios_tce
from coletor_municipios_ibge import buscar_municipios_ibge, transformar_municipios_ibge
from cruzar_dados import cruzar_municipios

load_dotenv()

municipios_tce = buscar_municipios_tce()
municipios_transformados_tce = transformar_municipios_tce(municipios_tce)

municipios_ibge = buscar_municipios_ibge()
municipios_transformados_ibge = transformar_municipios_ibge(municipios_ibge)

municipios_integrados = cruzar_municipios(
    municipios_transformados_ibge,
    municipios_transformados_tce
)

conexao = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cursor = conexao.cursor()

for municipio in municipios_integrados:
    cursor.execute(
        """INSERT INTO municipios(codigo_ibge, nome, uf, codigo_tce)
        VALUES 
        (%s, %s, %s, %s)
        ON CONFLICT (codigo_ibge) DO NOTHING
        """,
        (
            municipio["codigo_ibge"],
            municipio["nome"],
            municipio["uf"],
            municipio["codigo_tce"],
        )
    )

conexao.commit()

cursor.close()
conexao.close()

