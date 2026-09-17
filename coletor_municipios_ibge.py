import requests



url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/CE/municipios"

def buscar_municipios_ibge():
    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def transformar_municipios_ibge(municipios_ibge):
    municipios_transformados_ibge = []

    for municipio in municipios_ibge:
        dicionario_ibge = {
            "codigo_ibge": str(municipio["id"]),
            "nome": municipio["nome"],
            "uf": "CE",
            "codigo_tce":None
            }
        municipios_transformados_ibge.append(dicionario_ibge)

    return municipios_transformados_ibge


if __name__ == "__main__":
    municipios_ibge = buscar_municipios_ibge()
    municipios_transformados_ibge = transformar_municipios_ibge(municipios_ibge)

    print("Total de municípios:", len(municipios_transformados_ibge))
