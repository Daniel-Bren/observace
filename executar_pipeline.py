
import sys
import time
import logging
import os
from uuid import uuid4

from controle_fluxos import (
    obter_controle,
    registrar_inicio,
    registrar_sucesso,
    registrar_falha,
)
from coletor_balanco_tce import carregar_receitas
from carregar_despesas_tce import carregar_despesas
from conexao_banco import conexao


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

EXERCICIO_ORCAMENTO = 202600
DATA_REFERENCIA_DOC = 202604

TOTAL_MUNICIPIOS = 184
TAMANHO_LOTE = 10

FLUXOS = (
    ("receitas", carregar_receitas),
    ("despesas", carregar_despesas),
)


def obter_municipios():
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT codigo_tce
            FROM municipios
            WHERE codigo_tce IS NOT NULL
            ORDER BY codigo_tce
            """
        )
        municipios = [
            linha[0] for linha in cursor.fetchall()
        ]

    conexao.commit()
    return municipios


def preparar_lote():
    todos_municipios = obter_municipios()

    quantidade = len(todos_municipios)
    quantidade_unicos = len(set(todos_municipios))

    if (
        quantidade != TOTAL_MUNICIPIOS
        or quantidade_unicos != TOTAL_MUNICIPIOS
    ):
        raise ValueError(
            f"Esperados {TOTAL_MUNICIPIOS} municípios únicos; "
            f"encontrados {quantidade} registros "
            f"e {quantidade_unicos} códigos únicos."
        )

    total_lotes = (
        quantidade + TAMANHO_LOTE - 1
    ) // TAMANHO_LOTE

    lote = int(os.environ["LOTE"])

    if not 0 <= lote < total_lotes:
        raise ValueError(
            f"Lote inválido: {lote}. "
            f"Valores permitidos: 0 a {total_lotes - 1}."
        )

    inicio = lote * TAMANHO_LOTE
    municipios = todos_municipios[
        inicio:inicio + TAMANHO_LOTE
    ]

    return lote, total_lotes, municipios


def executar_pipeline():
    inicio_total = time.perf_counter()

    sucessos = 0
    ignorados = 0
    falhas = []

    # Identificador único mesmo em execuções manuais.
    execucao_id = (
        os.getenv("EXECUCAO_ID")
        or f"pipeline-{uuid4().hex}"
    )

    # Permite atualizar um fluxo já concluído.
    forcar = (
        os.getenv("FORCAR_REPROCESSAMENTO", "0") == "1"
    )

    try:
        lote, total_lotes, municipios = preparar_lote()

    except Exception:
        logger.exception("FALHA | preparacao_lote")

        try:
            conexao.rollback()
        except Exception:
            logger.exception(
                "FALHA_ROLLBACK | preparacao_lote"
            )

        return 1

    logger.info(
        "INICIO_LOTE | lote=%s | total_lotes=%s | "
        "municipios=%s | codigos=%s | "
        "exercicio=%s | referencia=%s | "
        "execucao_id=%s | forcar=%s",
        lote,
        total_lotes,
        len(municipios),
        municipios,
        EXERCICIO_ORCAMENTO,
        DATA_REFERENCIA_DOC,
        execucao_id,
        forcar,
    )

    for municipio in municipios:
        for tipo, carregar in FLUXOS:

            inicio_fluxo = time.perf_counter()

            # 1. Consultar estado anterior.
            try:
                controle = obter_controle(
                    municipio,
                    tipo,
                    EXERCICIO_ORCAMENTO,
                    DATA_REFERENCIA_DOC,
                )

            except Exception:
                logger.exception(
                    "FALHA_MONITORAMENTO | consulta | "
                    "municipio=%s | fluxo=%s",
                    municipio,
                    tipo,
                )

                conexao.rollback()
                return 1

            # 2. Evitar repetir fluxos concluídos.
            if (
                controle is not None
                and controle[0] == "SUCESSO"
                and not forcar
            ):
                ignorados += 1

                logger.info(
                    "IGNORADO_SUCESSO | lote=%s | "
                    "municipio=%s | fluxo=%s",
                    lote,
                    municipio,
                    tipo,
                )

                continue

            # 3. Registrar tentativa antes da coleta.
            try:
                registrar_inicio(
                    municipio,
                    tipo,
                    EXERCICIO_ORCAMENTO,
                    DATA_REFERENCIA_DOC,
                    execucao_id,
                )

            except Exception:
                logger.exception(
                    "FALHA_MONITORAMENTO | inicio | "
                    "municipio=%s | fluxo=%s",
                    municipio,
                    tipo,
                )

                conexao.rollback()
                return 1

            logger.info(
                "INICIO | lote=%s | fluxo=%s | "
                "municipio=%s | exercicio=%s | referencia=%s",
                lote,
                tipo,
                municipio,
                EXERCICIO_ORCAMENTO,
                DATA_REFERENCIA_DOC,
            )

            # 4. Executar coleta e persistência fiscal.
            try:
                carregar(
                    municipio,
                    EXERCICIO_ORCAMENTO,
                    DATA_REFERENCIA_DOC,
                )

            except Exception as erro:
                logger.exception(
                    "FALHA | lote=%s | fluxo=%s | "
                    "municipio=%s | duracao_s=%.2f",
                    lote,
                    tipo,
                    municipio,
                    time.perf_counter() - inicio_fluxo,
                )

                # 5. Desfazer transação pendente.
                try:
                    conexao.rollback()

                except Exception:
                    logger.exception(
                        "FALHA_ROLLBACK | lote=%s | "
                        "fluxo=%s | municipio=%s",
                        lote,
                        tipo,
                        municipio,
                    )

                    return 1

                # 6. Persistir a falha após o rollback.
                try:
                    registrar_falha(
                        municipio,
                        tipo,
                        EXERCICIO_ORCAMENTO,
                        DATA_REFERENCIA_DOC,
                        erro,
                    )

                except Exception:
                    logger.exception(
                        "FALHA_MONITORAMENTO | registro_falha | "
                        "municipio=%s | fluxo=%s",
                        municipio,
                        tipo,
                    )

                    conexao.rollback()
                    return 1

                falhas.append((municipio, tipo))
                continue

            # 7. O coletor já confirmou os dados fiscais.
            # Agora registrar o sucesso no monitoramento.
            try:
                registrar_sucesso(
                    municipio,
                    tipo,
                    EXERCICIO_ORCAMENTO,
                    DATA_REFERENCIA_DOC,
                )

            except Exception:
                logger.exception(
                    "FALHA_MONITORAMENTO | registro_sucesso | "
                    "municipio=%s | fluxo=%s",
                    municipio,
                    tipo,
                )

                # A carga fiscal pode estar confirmada.
                # Não classificar como falha da coleta.
                conexao.rollback()
                return 1

            sucessos += 1

            logger.info(
                "SUCESSO | lote=%s | fluxo=%s | "
                "municipio=%s | duracao_s=%.2f",
                lote,
                tipo,
                municipio,
                time.perf_counter() - inicio_fluxo,
            )

    # 8. Resumo da execução.
    duracao_total = (
        time.perf_counter() - inicio_total
    )

    municipios_com_falha = sorted({
        municipio
        for municipio, _ in falhas
    })

    fluxos_previstos = (
        len(municipios) * len(FLUXOS)
    )

    logger.info(
        "RESUMO_LOTE | lote=%s | "
        "municipios=%s | fluxos_previstos=%s | "
        "sucessos=%s | ignorados=%s | falhas=%s | "
        "municipios_com_falha=%s | duracao_total_s=%.2f | "
        "execucao_id=%s",
        lote,
        len(municipios),
        fluxos_previstos,
        sucessos,
        ignorados,
        len(falhas),
        len(municipios_com_falha),
        duracao_total,
        execucao_id,
    )

    if falhas:
        logger.error(
            "PENDENCIAS_REPROCESSAMENTO | "
            "lote=%s | %s",
            lote,
            falhas,
        )

    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(executar_pipeline())
