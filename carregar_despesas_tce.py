from coletor_despesas_tce import (buscar_despesas, transformar_balancete_despesa)
from conexao_banco import cursor, conexao
from coletor_balanco_tce import receber_id_municipio_BD
from coletor_despesas_tce import validar_escopo_coleta

def preparar_despesas(registros):
    registros_unicos = {}

    for registro in registros:
        chave = (
            registro["codigo_municipio"],
            registro["exercicio_orcamento"],
            registro["data_referencia_doc"],
            registro["tipo_balancete"],
            registro["codigo_orgao"],
            registro["codigo_unidade_orcamentaria"],
            registro["codigo_funcao"],
            registro["codigo_subfuncao"],
            registro["codigo_programa"],
            registro["codigo_projeto_atividade"],
            registro["numero_projeto_atividade"],
            registro["numero_subprojeto_atividade"],
            registro["codigo_elemento_despesa"],
            registro["tipo_fonte"],
            registro["codigo_fonte"]
        )
        if chave not in registros_unicos:
            registros_unicos[chave] = registro
        elif registros_unicos[chave] != registro:
            raise ValueError(
                f"Conflito de chaves iguais com valores diferentes: {chave}"
            )

    return list(registros_unicos.values())

def inserir_despesa_BD(registro, municipio_id):
    cursor.execute(
        """
            INSERT INTO despesas (
                municipio_id,
                exercicio_orcamento,
                data_referencia_doc,
                tipo_balancete,
                codigo_orgao,
                codigo_unidade_orcamentaria,
                codigo_funcao,
                codigo_subfuncao,
                codigo_programa,
                codigo_projeto_atividade,
                numero_projeto_atividade,
                numero_subprojeto_atividade,
                codigo_elemento_despesa,
                tipo_fonte,
                codigo_fonte,
                valor_fixado_orcamento_bal_despesa,
                valor_suplementado_no_mes,
                valor_suplementado_ate_mes,
                valor_anulacoes_no_mes,
                valor_empenhado_no_mes,
                valor_empenhado_ate_mes,
                valor_saldo_dotacao,
                valor_pago_no_mes,
                valor_pago_ate_mes,
                valor_empenhado_pagar,
                valor_anulacoes_dotacao_ate_mes,
                valor_anulacoes_empenhos_no_mes,
                valor_anulacoes_empenhos_ate_mes,
                valor_liquidado_no_mes,
                valor_liquidado_ate_mes,
                valor_estornos_liquidacao_no_mes,
                valor_estornos_liquidacao_ate_mes,
                valor_estornos_pagos_no_mes,
                valor_estornos_pagos_ate_mes
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT ON CONSTRAINT uq_despesas_posicao
            DO UPDATE SET
                valor_fixado_orcamento_bal_despesa = EXCLUDED.valor_fixado_orcamento_bal_despesa,
                valor_suplementado_no_mes = EXCLUDED.valor_suplementado_no_mes,
                valor_suplementado_ate_mes = EXCLUDED.valor_suplementado_ate_mes,
                valor_anulacoes_no_mes = EXCLUDED.valor_anulacoes_no_mes,
                valor_empenhado_no_mes = EXCLUDED.valor_empenhado_no_mes,
                valor_empenhado_ate_mes = EXCLUDED.valor_empenhado_ate_mes,
                valor_saldo_dotacao = EXCLUDED.valor_saldo_dotacao,
                valor_pago_no_mes = EXCLUDED.valor_pago_no_mes,
                valor_pago_ate_mes = EXCLUDED.valor_pago_ate_mes,
                valor_empenhado_pagar = EXCLUDED.valor_empenhado_pagar,
                valor_anulacoes_dotacao_ate_mes = EXCLUDED.valor_anulacoes_dotacao_ate_mes,
                valor_anulacoes_empenhos_no_mes = EXCLUDED.valor_anulacoes_empenhos_no_mes,
                valor_anulacoes_empenhos_ate_mes = EXCLUDED.valor_anulacoes_empenhos_ate_mes,
                valor_liquidado_no_mes = EXCLUDED.valor_liquidado_no_mes,
                valor_liquidado_ate_mes = EXCLUDED.valor_liquidado_ate_mes,
                valor_estornos_liquidacao_no_mes = EXCLUDED.valor_estornos_liquidacao_no_mes,
                valor_estornos_liquidacao_ate_mes = EXCLUDED.valor_estornos_liquidacao_ate_mes,
                valor_estornos_pagos_no_mes = EXCLUDED.valor_estornos_pagos_no_mes,
                valor_estornos_pagos_ate_mes = EXCLUDED.valor_estornos_pagos_ate_mes
            WHERE (
                despesas.valor_fixado_orcamento_bal_despesa,
                despesas.valor_suplementado_no_mes,
                despesas.valor_suplementado_ate_mes,
                despesas.valor_anulacoes_no_mes,
                despesas.valor_empenhado_no_mes,
                despesas.valor_empenhado_ate_mes,
                despesas.valor_saldo_dotacao,
                despesas.valor_pago_no_mes,
                despesas.valor_pago_ate_mes,
                despesas.valor_empenhado_pagar,
                despesas.valor_anulacoes_dotacao_ate_mes,
                despesas.valor_anulacoes_empenhos_no_mes,
                despesas.valor_anulacoes_empenhos_ate_mes,
                despesas.valor_liquidado_no_mes,
                despesas.valor_liquidado_ate_mes,
                despesas.valor_estornos_liquidacao_no_mes,
                despesas.valor_estornos_liquidacao_ate_mes,
                despesas.valor_estornos_pagos_no_mes,
                despesas.valor_estornos_pagos_ate_mes
            ) IS DISTINCT FROM (
                EXCLUDED.valor_fixado_orcamento_bal_despesa,
                EXCLUDED.valor_suplementado_no_mes,
                EXCLUDED.valor_suplementado_ate_mes,
                EXCLUDED.valor_anulacoes_no_mes,
                EXCLUDED.valor_empenhado_no_mes,
                EXCLUDED.valor_empenhado_ate_mes,
                EXCLUDED.valor_saldo_dotacao,
                EXCLUDED.valor_pago_no_mes,
                EXCLUDED.valor_pago_ate_mes,
                EXCLUDED.valor_empenhado_pagar,
                EXCLUDED.valor_anulacoes_dotacao_ate_mes,
                EXCLUDED.valor_anulacoes_empenhos_no_mes,
                EXCLUDED.valor_anulacoes_empenhos_ate_mes,
                EXCLUDED.valor_liquidado_no_mes,
                EXCLUDED.valor_liquidado_ate_mes,
                EXCLUDED.valor_estornos_liquidacao_no_mes,
                EXCLUDED.valor_estornos_liquidacao_ate_mes,
                EXCLUDED.valor_estornos_pagos_no_mes,
                EXCLUDED.valor_estornos_pagos_ate_mes
            );
        """,
            (
                municipio_id,
                registro["exercicio_orcamento"],
                registro["data_referencia_doc"],
                registro["tipo_balancete"],
                registro["codigo_orgao"],
                registro["codigo_unidade_orcamentaria"],
                registro["codigo_funcao"],
                registro["codigo_subfuncao"],
                registro["codigo_programa"],
                registro["codigo_projeto_atividade"],
                registro["numero_projeto_atividade"],
                registro["numero_subprojeto_atividade"],
                registro["codigo_elemento_despesa"],
                registro["tipo_fonte"],
                registro["codigo_fonte"],
                registro["valor_fixado_orcamento_bal_despesa"],
                registro["valor_suplementado_no_mes"],
                registro["valor_suplementado_ate_mes"],
                registro["valor_anulacoes_no_mes"],
                registro["valor_empenhado_no_mes"],
                registro["valor_empenhado_ate_mes"],
                registro["valor_saldo_dotacao"],
                registro["valor_pago_no_mes"],
                registro["valor_pago_ate_mes"],
                registro["valor_empenhado_pagar"],
                registro["valor_anulacoes_dotacao_ate_mes"],
                registro["valor_anulacoes_empenhos_no_mes"],
                registro["valor_anulacoes_empenhos_ate_mes"],
                registro["valor_liquidado_no_mes"],
                registro["valor_liquidado_ate_mes"],
                registro["valor_estornos_liquidacao_no_mes"],
                registro["valor_estornos_liquidacao_ate_mes"],
                registro["valor_estornos_pagos_no_mes"],
                registro["valor_estornos_pagos_ate_mes"],
            )
    )

def carregar_despesas(codigo_municipio, exercicio_orcamento, data_referencia_doc):
    dados = buscar_despesas(codigo_municipio, exercicio_orcamento, data_referencia_doc)

    if not dados:
        raise ValueError("Coleta sem registros. Carga interrompida.")

    registros = transformar_balancete_despesa(dados)
    registros = preparar_despesas(registros)

    if not validar_escopo_coleta(registros, codigo_municipio, exercicio_orcamento, data_referencia_doc):
        raise ValueError("Dados, municipio ou periodo solicitado estao incorretos ou divergentes.")

    try:
        municipio_id = receber_id_municipio_BD(codigo_municipio)

        for registro in registros:
            inserir_despesa_BD(registro, municipio_id)

        conexao.commit()
        print(f"Carga concluida: {len(registros)} registros unicos.")

    except Exception:
        conexao.rollback()
        raise

if __name__ == "__main__":
    carregar_despesas("057", 202600, 202604)