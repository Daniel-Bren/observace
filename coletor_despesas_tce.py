import requests


url = "https://api-dados-abertos.tce.ce.gov.br/sim/balancetes_despesas_orcamentarias"

def buscar_despesas(codigo_municipio, exercicio_orcamento, data_referencia_doc):
    limite = 1000
    inicio = 0

    todos_registros = []

    while True:
        parametros = {

            "codigo_municipio": codigo_municipio,
            "exercicio_orcamento": exercicio_orcamento,
            "data_referencia_doc": data_referencia_doc,
            "$count":limite,
            "$start_index":inicio
        }

        response = requests.get(url, params=parametros)
        response.raise_for_status()

        dados = response.json()
        pagina = dados.get("elements")

        if not isinstance(pagina, list):
            raise ValueError("Resposta inválida da API: 'elements' não é uma lista")

        todos_registros.extend(pagina)

        print(f"Inicio: {inicio} | Recebidos: {len(pagina)}")
        if len(pagina) < limite:
            break

        inicio += limite

    return todos_registros

def transformar_balancete_despesa(dados):
    despesas_transformadas = []

    for despesa in dados:
        dict_balanco = {
            "codigo_municipio": despesa['codigo_municipio'].strip(),
            "exercicio_orcamento": despesa['exercicio_orcamento'],
            "data_referencia_doc": despesa['data_referencia_doc'],
            "tipo_balancete": despesa['tipo_balancete'].strip(),
            "codigo_orgao": despesa['codigo_orgao'].strip(),
            "codigo_unidade_orcamentaria": despesa['codigo_unidade_orcamentaria'].strip(),
            "codigo_funcao": despesa['codigo_funcao'].strip(),
            "codigo_subfuncao": despesa['codigo_subfuncao'].strip(),
            "codigo_programa": despesa['codigo_programa'].strip(),
            "codigo_projeto_atividade": despesa['codigo_projeto_atividade'].strip(),
            "numero_projeto_atividade": despesa['numero_projeto_atividade'].strip(),
            "numero_subprojeto_atividade": despesa['numero_subprojeto_atividade'].strip(),
            "codigo_elemento_despesa": despesa['codigo_elemento_despesa'].strip(),
            "valor_fixado_orcamento_bal_despesa": despesa['valor_fixado_orcamento_bal_despesa'],
            "valor_suplementado_no_mes": despesa['valor_suplementado_no_mes'],
            "valor_suplementado_ate_mes": despesa['valor_suplementado_ate_mes'],
            "valor_anulacoes_no_mes": despesa['valor_anulacoes_no_mes'],
            "valor_empenhado_no_mes": despesa['valor_empenhado_no_mes'],
            "valor_empenhado_ate_mes": despesa['valor_empenhado_ate_mes'],
            "valor_saldo_dotacao": despesa['valor_saldo_dotacao'],
            "valor_pago_no_mes": despesa['valor_pago_no_mes'],
            "valor_pago_ate_mes": despesa['valor_pago_ate_mes'],
            "valor_empenhado_pagar": despesa['valor_empenhado_pagar'],
            "valor_anulacoes_dotacao_ate_mes": despesa['valor_anulacoes_dotacao_ate_mes'],
            "valor_anulacoes_empenhos_no_mes": despesa['valor_anulacoes_empenhos_no_mes'],
            "valor_anulacoes_empenhos_ate_mes": despesa['valor_anulacoes_empenhos_ate_mes'],
            "valor_liquidado_no_mes": despesa['valor_liquidado_no_mes'],
            "valor_liquidado_ate_mes": despesa['valor_liquidado_ate_mes'],
            "valor_estornos_liquidacao_no_mes": despesa['valor_estornos_liquidacao_no_mes'],
            "valor_estornos_liquidacao_ate_mes": despesa['valor_estornos_liquidacao_ate_mes'],
            "valor_estornos_pagos_no_mes": despesa['valor_estornos_pagos_no_mes'],
            "valor_estornos_pagos_ate_mes": despesa['valor_estornos_pagos_ate_mes'],
            "tipo_fonte": despesa['tipo_fonte'].strip(),
            "codigo_fonte": despesa['codigo_fonte'].strip(),
        }
        despesas_transformadas.append(dict_balanco)
    return despesas_transformadas

def validar_escopo_coleta(registros, codigo_municipio, exercicio_orcamento, data_referencia_doc):

    municipio_valido = all(
        registro["codigo_municipio"] == codigo_municipio
        and registro["exercicio_orcamento"] == exercicio_orcamento
        and registro["data_referencia_doc"] == data_referencia_doc

        for registro in registros
    )


    return bool(registros) and municipio_valido


if __name__ == "__main__":
    dados = buscar_despesas("002", 202600, 202604)
    despesas = transformar_balancete_despesa(dados)

    print("Lista vazia:", validar_escopo_coleta([], "002", 202600, 202604))
    print("Registros transformados:", len(despesas))
    print("Primeiro registro:", despesas[0])
    print("Campos transformados:", len(despesas[0]))
    print("Registros transformados:", len(despesas))
    print("Escopo correto:", validar_escopo_coleta(
        despesas, "002", 202600, 202604
    ))

    print("Escopo incorreto:", validar_escopo_coleta(
        despesas, "057", 202600, 202604
    ))

