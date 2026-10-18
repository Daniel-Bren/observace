import requests
from conexao_banco import cursor, conexao

url = "https://api-dados-abertos.tce.ce.gov.br/sim/balancetes_receitas_orcamentarias"

def buscar_balanco_orcamento(codigo_municipio, exercicio_orcamento, data_referencia_doc):
    limite = 1000
    inicio = 0

    todos_registros = []

    while True:
        parametros = {
            "codigo_municipio": codigo_municipio,
            "exercicio_orcamento": exercicio_orcamento,
            "data_referencia_doc": data_referencia_doc,
            "$count": limite,
            "$start_index": inicio
        }

        response = requests.get(url, params=parametros)
        response.raise_for_status()

        dados = response.json()
        pagina = dados["elements"]

        # Adiciona os registros da página à lista principal
        todos_registros.extend(pagina)

        print(f"Início: {inicio} | Recebidos: {len(pagina)}")

        # Encerra quando a página vier incompleta
        if len(pagina) < limite:
            break

        # Avança para a próxima página
        inicio += limite

    return todos_registros

def transformar_balancete_receita(dados):
    balanco_transformado = []

    for receita in dados:
        dict_balanco = {
            "codigo_municipio": receita["codigo_municipio"],
            "exercicio_orcamento": receita["exercicio_orcamento"],
            "codigo_orgao": receita["codigo_orgao"],
            "codigo_unidade_orcamentaria": receita["codigo_unidade_orcamentaria"].strip(),
            "codigo_rubrica": receita["codigo_rubrica"],
            "tipo_fonte": receita["tipo_fonte"],
            "codigo_fonte": receita["codigo_fonte"],
            "data_referencia_doc": receita["data_referencia_doc"],
            "tipo_balancete": receita["tipo_balancete"],
            "valor_previsto": receita["valor_previsto_orcamento"],
            "arrecadacao_mes": receita["valor_arrecadacao_no_mes"],
            "arrecadacao_acumulada": receita["valor_arrecadacao_ate_mes"],
            "anulacoes_mes": receita["valor_anulacoes_no_mes"],
            "anulacoes_acumuladas": receita["valor_anulacoes_ate_mes"],
        }
        balanco_transformado.append(dict_balanco)
    return balanco_transformado

def validar_chaves_unicas(registros):
    validar_chaves = set()

    for chaves in registros:
        validacao_chaves = (
            chaves["codigo_municipio"],
            chaves["exercicio_orcamento"],
            chaves["codigo_orgao"],
            chaves["codigo_unidade_orcamentaria"],
            chaves["codigo_rubrica"],
            chaves["tipo_fonte"],
            chaves["codigo_fonte"],
            chaves["data_referencia_doc"],
        )

        validar_chaves.add(validacao_chaves)

    return len(registros) == len(validar_chaves)

def validar_escopo_coleta(registros, codigo_municipio, exercicio_orcamento, data_referencia_doc):

    for registro in registros:
        if (
            registro["codigo_municipio"] != codigo_municipio
            or registro["exercicio_orcamento"] != exercicio_orcamento
            or registro["data_referencia_doc"] != data_referencia_doc
        ):
            return False
    return True

def verificar_valores_none(registros):
        for registro in registros:
            for campo, valor in registro.items():
                if valor is None:
                    return False
        return True

def verificar_campos_vazios(registros):
    for registro in registros:
        for campo, valor in registro.items():
            if isinstance(valor, str) and valor.strip() == "":
                return False
    return True

def receber_id_municipio_BD(codigo_tce):
    cursor.execute(
        "SELECT id FROM municipios WHERE codigo_tce = %s",
        (codigo_tce,)
    )
    resultado = cursor.fetchone()
    if resultado is None:
        raise ValueError(f"Municipio TCE{codigo_tce} nao encontrado")
    return resultado[0]

def inserir_receitas_BD(registro, municipio_id):
    cursor.execute(
        """INSERT INTO receitas (municipio_id,
                                codigo_orgao,
                                exercicio_orcamento,
                                codigo_unidade_orcamentaria,
                                codigo_rubrica,
                                tipo_fonte,
                                codigo_fonte,
                                data_referencia_doc,
                                tipo_balancete,
                                valor_previsto,
                                arrecadacao_mes,
                                arrecadacao_acumulada,
                                anulacoes_mes,
                                anulacoes_acumuladas) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                                (
                                    municipio_id,
                                    registro["codigo_orgao"],
                                    registro["exercicio_orcamento"],
                                    registro["codigo_unidade_orcamentaria"],
                                    registro["codigo_rubrica"],
                                    registro["tipo_fonte"],
                                    registro["codigo_fonte"],
                                    registro["data_referencia_doc"],
                                    registro["tipo_balancete"],
                                    registro["valor_previsto"],
                                    registro["arrecadacao_mes"],
                                    registro["arrecadacao_acumulada"],
                                    registro["anulacoes_mes"],
                                    registro["anulacoes_acumuladas"],
                                )
    )



if __name__ == "__main__":

    todos_registros = buscar_balanco_orcamento("057", 202600, 202604)
    if not todos_registros:
        print("Nenhum registro encontrado")
    else:
        balanco_transformado = transformar_balancete_receita(todos_registros)

        validacao_tupla = validar_chaves_unicas(balanco_transformado)

        # ALTERAÇÃO 3: passar os parâmetros para a validação
        escopo_valido = validar_escopo_coleta(
            balanco_transformado, "057", 202600, 202604
        )


        campos_preenchidos = verificar_valores_none(
            balanco_transformado
            )

        campos_vazios = verificar_campos_vazios(
            balanco_transformado
            )

        dados_validos = (
                          escopo_valido
                         and validacao_tupla
                         and campos_preenchidos
                         and campos_vazios
                         )

        codigo_tce = todos_registros[0]["codigo_municipio"]
        municipio_id = receber_id_municipio_BD(codigo_tce)

        ###print("Verificar vazios:", campos_vazios)
        ###print("Sem valores None:", campos_preenchidos)
        ###print("Registros:", len(balanco_transformado))
        ###print("Chaves únicas:", (validacao_tupla))
        ###print("Escopo válido:", escopo_valido)
        ###print("Dados válidos:", dados_validos)
        if dados_validos:
            try:
                for registro in balanco_transformado:
                    inserir_receitas_BD(registro,municipio_id)
                conexao.commit()
                print("Carga realizada.")
            except Exception:
                conexao.rollback()
                raise
