import requests
from conexao_banco import cursor, conexao

url = "https://api-dados-abertos.tce.ce.gov.br/sim/balancetes_receitas_orcamentarias?codigo_municipio=057&exercicio_orcamento=202600&data_referencia_doc=202604"


def buscar_balanco_orcamento():
    limite = 1000
    inicio = 0

    todos_registros = []

    while True:
        parametros = {
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

    for balanco in dados:
        dict_balanco = {
            "codigo_municipio": balanco["codigo_municipio"],
            "exercicio_orcamento": balanco["exercicio_orcamento"],
            "codigo_orgao": balanco["codigo_orgao"],
            "codigo_unidade_orcamentaria": balanco["codigo_unidade_orcamentaria"].strip(),
            "codigo_rubrica": balanco["codigo_rubrica"],
            "tipo_fonte": balanco["tipo_fonte"],
            "codigo_fonte": balanco["codigo_fonte"],
            "data_referencia_doc": balanco["data_referencia_doc"],
            "tipo_balancete": balanco["tipo_balancete"],
            "valor_previsto": balanco["valor_previsto_orcamento"],
            "arrecadacao_mes": balanco["valor_arrecadacao_no_mes"],
            "arrecadacao_acumulada": balanco["valor_arrecadacao_ate_mes"],
            "anulacoes_mes": balanco["valor_anulacoes_no_mes"],
            "anulacoes_acumuladas": balanco["valor_anulacoes_ate_mes"],
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

def validar_escopo_coleta(registros):

    for registro in registros:
        if (
            registro["codigo_municipio"] != "057"
            or registro["exercicio_orcamento"] != 202600
            or registro["data_referencia_doc"] != 202604
        ):
            return False
    return True

def validar_tipos(registros):

    tipos_esperados = {
        "codigo_municipio": str,
        "exercicio_orcamento": int,
        "codigo_orgao": str,
        "codigo_unidade_orcamentaria": str,
        "codigo_rubrica": str,
        "tipo_fonte": str,
        "codigo_fonte": str,
        "data_referencia_doc": int,
        "tipo_balancete": str,
        "valor_previsto": (float, int),
        "arrecadacao_mes": (float, int),
        "arrecadacao_acumulada": (float, int),
        "anulacoes_mes": (float, int),
        "anulacoes_acumuladas": (float, int),
    }
    for registro in registros:
        for campo, tipo_esperado in tipos_esperados.items():
            if not isinstance(registro[campo], tipo_esperado):
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



todos_registros = buscar_balanco_orcamento()
if not todos_registros:
    print("Nenhum registro encontrado")
else:
    balanco_transformado = transformar_balancete_receita(todos_registros)

    validacao_tupla = validar_chaves_unicas(balanco_transformado)

    escopo_valido = validar_escopo_coleta(balanco_transformado)

    tipos_validos = validar_tipos(balanco_transformado)

    campos_preenchidos = verificar_valores_none(
        balanco_transformado
        )

    campos_vazios = verificar_campos_vazios(
        balanco_transformado
        )

    dados_validos = (tipos_validos
                     and escopo_valido
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
    ###print("Tipos válidos:", tipos_validos)
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

