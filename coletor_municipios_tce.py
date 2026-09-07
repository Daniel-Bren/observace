import requests

url = "https://api-dados-abertos.tce.ce.gov.br/sim/municipios"

params = {
    "$count": 185,
    "$start_index": 0,
}

response = requests.get(url, params=params)
response.raise_for_status()

dados = response.json()
municipios = dados["elements"]

municipios_transformados = []

for municipio in municipios:
    dicionario = {
        "codigo_tce": municipio["codigo_municipio"],
        "nome": municipio["nome_municipio"],
        "codigo_ibge": municipio["codigo_municipio_ibge"],
        "uf": "CE",
    }

    municipios_transformados.append(dicionario)

print(municipios_transformados)

