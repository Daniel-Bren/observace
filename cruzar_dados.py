from coletor_municipios_tce import buscar_municipios_tce, transformar_municipios_tce
from coletor_municipios_ibge import buscar_municipios_ibge, transformar_municipios_ibge


def cruzar_municipios(municipios_transformados_ibge, municipios_transformados_tce):
    municipios_integrados = []

    for municipio_ibge in municipios_transformados_ibge:
        for municipio_tce in municipios_transformados_tce:
            if municipio_ibge["codigo_ibge"] == municipio_tce["codigo_ibge"]:
                municipio_integrado = {
                    "codigo_ibge": municipio_ibge["codigo_ibge"],
                    "nome": municipio_ibge["nome"],
                    "uf": municipio_ibge["uf"],
                    "codigo_tce": municipio_tce["codigo_tce"],
                }

                municipios_integrados.append(municipio_integrado)

    return municipios_integrados


if __name__ == "__main__":
    municipios_tce = buscar_municipios_tce()
    municipios_transformados_tce = transformar_municipios_tce(municipios_tce)

    municipios_ibge = buscar_municipios_ibge()
    municipios_transformados_ibge = transformar_municipios_ibge(municipios_ibge)

    municipios_integrados = cruzar_municipios(
        municipios_transformados_ibge,
        municipios_transformados_tce
    )

    print(len(municipios_integrados))