import requests

url = "https://api-dados-abertos.tce.ce.gov.br/sim/municipios"

params_tce = {
    "$count": 185,
    "$start_index": 0,
}


def buscar_municipios_tce():
    response = requests.get(url, params=params_tce)
    response.raise_for_status()

    dados_tce = response.json()

    return dados_tce["elements"]


def transformar_municipios_tce(municipios_tce):
    municipios_transformados_tce = []

    for municipio in municipios_tce:
        dicionario_tce = {
            "codigo_tce": municipio["codigo_municipio"],
            "nome": municipio["nome_municipio"],
            "codigo_ibge": municipio["codigo_municipio_ibge"],
            "uf": "CE",
        }

        municipios_transformados_tce.append(dicionario_tce)

    return municipios_transformados_tce


def obter_codigos_ibge_validos(municipios_transformados_tce):
    codigos_ibge = []

    for municipio in municipios_transformados_tce:
        if municipio["codigo_ibge"] is not None:
            codigos_ibge.append(municipio["codigo_ibge"])

    return codigos_ibge

if __name__ == "__main__":
    municipios_tce = buscar_municipios_tce()
    municipios_transformados_tce = transformar_municipios_tce(municipios_tce)
    codigos_ibge = obter_codigos_ibge_validos(municipios_transformados_tce)

    print("Total de códigos válidos:", len(codigos_ibge))

