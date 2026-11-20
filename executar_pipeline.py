
import sys
import time
import logging
import os

from coletor_balanco_tce import carregar_receitas
from carregar_despesas_tce import carregar_despesas
from conexao_banco import conexao


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

exercicio_orcamento = 202600
data_referencia_doc = 202604

TAMANHO_LOTE = 20


def obter_municipios():
    with conexao.cursor() as cursor:
        cursor.execute("""
            SELECT codigo_tce
            FROM municipios
            WHERE codigo_tce IS NOT NULL
            ORDER BY codigo_tce
        """)
        municipios = [linha[0] for linha in cursor.fetchall()]

    conexao.commit()
    return municipios


def executar_pipeline():
    inicio_total = time.perf_counter()
    sucessos = 0
    falhas = []

    try:
        todos_municipios = obter_municipios()

        if (
            len(todos_municipios) != 184
            or len(set(todos_municipios)) != 184
        ):
            raise ValueError(
                f"Esperados 184 municípios únicos; "
                f"encontrados {len(todos_municipios)} registros "
                f"e {len(set(todos_municipios))} códigos únicos."
            )

        total_lotes = (
            len(todos_municipios) + TAMANHO_LOTE - 1
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

    except Exception:
        logger.exception("FALHA | preparação do lote")

        try:
            conexao.rollback()
        except Exception:
            logger.exception("FALHA_ROLLBACK | preparação")

        return 1

    logger.info(
        "INICIO_LOTE | lote=%s | total_lotes=%s | "
        "municipios=%s | codigos=%s | "
        "exercicio=%s | referencia=%s",
        lote,
        total_lotes,
        len(municipios),
        municipios,
        exercicio_orcamento,
        data_referencia_doc
    )

    for municipio in municipios:
        for tipo, carregar in [
            ("receitas", carregar_receitas),
            ("despesas", carregar_despesas)
        ]:
            inicio_fluxo = time.perf_counter()

            try:
                logger.info(
                    "INICIO | lote=%s | fluxo=%s | "
                    "municipio=%s | exercicio=%s | referencia=%s",
                    lote,
                    tipo,
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc
                )

                carregar(
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc
                )

                sucessos += 1

                logger.info(
                    "SUCESSO | lote=%s | fluxo=%s | "
                    "municipio=%s | duracao_s=%.2f",
                    lote,
                    tipo,
                    municipio,
                    time.perf_counter() - inicio_fluxo
                )

            except Exception:
                falhas.append((municipio, tipo))

                logger.exception(
                    "FALHA | lote=%s | fluxo=%s | "
                    "municipio=%s | exercicio=%s | "
                    "referencia=%s | duracao_s=%.2f",
                    lote,
                    tipo,
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc,
                    time.perf_counter() - inicio_fluxo
                )

                try:
                    conexao.rollback()
                except Exception:
                    logger.exception(
                        "FALHA_ROLLBACK | lote=%s | "
                        "fluxo=%s | municipio=%s",
                        lote,
                        tipo,
                        municipio
                    )

    duracao_total = time.perf_counter() - inicio_total

    municipios_com_falha = sorted({
        municipio for municipio, tipo in falhas
    })

    logger.info(
        "RESUMO_LOTE | lote=%s | municipios=%s | "
        "fluxos_previstos=%s | sucessos=%s | "
        "falhas=%s | municipios_com_falha=%s | "
        "duracao_total_s=%.2f",
        lote,
        len(municipios),
        len(municipios) * 2,
        sucessos,
        len(falhas),
        len(municipios_com_falha),
        duracao_total
    )

    if falhas:
        logger.error(
            "PENDENCIAS_REPROCESSAMENTO | lote=%s | %s",
            lote,
            falhas
        )

    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(executar_pipeline())