from coletor_municipios_tce import buscar_municipios_tce, transformar_municipios_tce
from coletor_municipios_ibge import buscar_municipios_ibge, transformar_municipios_ibge


if __name__ == "__main__":
    municipios_tce = buscar_municipios_tce()
    municipios_transformados_tce = transformar_municipios_tce(municipios_tce)

    municipios_ibge = buscar_municipios_ibge()
    municipios_transformados_ibge = transformar_municipios_ibge(municipios_ibge)

    quantidade = 0

    for municipio_ibge in municipios_transformados_ibge:
        for municipio_tce in municipios_transformados_tce:
            if municipio_ibge["codigo_ibge"] == municipio_tce["codigo_ibge"]:
                quantidade += 1

    print(quantidade)

    for municipio_tce in municipios_transformados_tce:
        encontrado = False

        for municipio_ibge in municipios_transformados_ibge:
            if municipio_tce["codigo_ibge"] == municipio_ibge["codigo_ibge"]:
                encontrado = True
                break

        if not encontrado:
            print(municipio_tce)