from datetime import datetime, timezone
from conexao_banco import conexao


def obter_controle(municipio, fluxo, exercicio, referencia):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT status, tentativas
            FROM controle_fluxos_fiscais
            WHERE codigo_tce = %s
              AND fluxo = %s
              AND exercicio = %s
              AND referencia = %s
            """,
            (municipio, fluxo, exercicio, referencia)
        )
        resultado = cursor.fetchone()

    conexao.commit()
    return resultado


def registrar_inicio(
    municipio, fluxo, exercicio, referencia, execucao_id
):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO controle_fluxos_fiscais (
                codigo_tce, fluxo, exercicio, referencia,
                status, tentativas, iniciado_em, execucao_id
            )
            VALUES (
                %s, %s, %s, %s,
                'EXECUTANDO', 1, NOW(), %s
            )
            ON CONFLICT ON CONSTRAINT uq_controle_fluxos_fiscais
            DO UPDATE SET
                status = 'EXECUTANDO',
                tentativas = controle_fluxos_fiscais.tentativas + 1,
                iniciado_em = NOW(),
                finalizado_em = NULL,
                execucao_id = EXCLUDED.execucao_id,
                ultimo_erro = NULL
            """,
            (municipio, fluxo, exercicio, referencia, execucao_id)
        )

    conexao.commit()


def registrar_sucesso(municipio, fluxo, exercicio, referencia):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            UPDATE controle_fluxos_fiscais
            SET status = 'SUCESSO',
                finalizado_em = NOW(),
                ultimo_sucesso_em = NOW(),
                ultimo_erro = NULL
            WHERE codigo_tce = %s
              AND fluxo = %s
              AND exercicio = %s
              AND referencia = %s
            """,
            (municipio, fluxo, exercicio, referencia)
        )

    conexao.commit()


def registrar_falha(municipio, fluxo, exercicio, referencia, erro):
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            UPDATE controle_fluxos_fiscais
            SET status = 'FALHA',
                finalizado_em = NOW(),
                ultimo_erro = %s
            WHERE codigo_tce = %s
              AND fluxo = %s
              AND exercicio = %s
              AND referencia = %s
            """,
            (
                str(erro)[:1000],
                municipio, fluxo, exercicio, referencia
            )
        )

    conexao.commit()