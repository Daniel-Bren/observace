
import sys
import time
import logging

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
        municipios = obter_municipios()

        if len(municipios) != 184 or len(set(municipios)) != 184:
            raise ValueError(
                f"Esperados 184 municípios únicos; "
                f"encontrados {len(municipios)} registros "
                f"e {len(set(municipios))} códigos únicos."
            )

    except Exception:
        logger.exception("FALHA | preparação da carga estadual")
        try:
            conexao.rollback()
        except Exception:
            logger.exception("FALHA_ROLLBACK | preparação")
        return 1

    logger.info(
        "INICIO_CARGA | municipios=%s | fluxos=%s | "
        "exercicio=%s | referencia=%s",
        len(municipios),
        len(municipios) * 2,
        exercicio_orcamento,
        data_referencia_doc
    )

    for municipio in municipios:
        for tipo, carregar in [
            ("receitas", carregar_receitas),
            ("despesas", carregar_despesas)
        ]:
            inicio = time.perf_counter()

            try:
                logger.info(
                    "INICIO | fluxo=%s | municipio=%s | "
                    "exercicio=%s | referencia=%s",
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
                    "SUCESSO | fluxo=%s | municipio=%s | "
                    "duracao_s=%.2f",
                    tipo,
                    municipio,
                    time.perf_counter() - inicio
                )

            except Exception:
                falhas.append((municipio, tipo))

                logger.exception(
                    "FALHA | fluxo=%s | municipio=%s | "
                    "exercicio=%s | referencia=%s | "
                    "duracao_s=%.2f",
                    tipo,
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc,
                    time.perf_counter() - inicio
                )

                try:
                    conexao.rollback()
                except Exception:
                    logger.exception(
                        "FALHA_ROLLBACK | fluxo=%s | municipio=%s",
                        tipo,
                        municipio
                    )

    duracao_total = time.perf_counter() - inicio_total

    municipios_com_falha = sorted({
        municipio for municipio, tipo in falhas
    })

    logger.info(
        "RESUMO | municipios=%s | fluxos_previstos=%s | "
        "sucessos=%s | falhas=%s | "
        "municipios_com_falha=%s | duracao_total_s=%.2f",
        len(municipios),
        len(municipios) * 2,
        sucessos,
        len(falhas),
        len(municipios_com_falha),
        duracao_total
    )

    if falhas:
        logger.error(
            "PENDENCIAS_REPROCESSAMENTO | %s",
            falhas
        )

    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(executar_pipeline())
