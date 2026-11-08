import time

from coletor_balanco_tce import carregar_receitas
from carregar_despesas_tce import carregar_despesas
from conexao_banco import conexao
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

municipios = ["002", "057", "074", "084", "094", "162","164", "167"]
exercicio_orcamento = 202600
data_referencia_doc = 202604

def executar_pipeline():
    falhou = False
    for municipio in municipios:
        for tipo, carregar in [
            ("receitas", carregar_receitas),
            ("despesas", carregar_despesas)
        ]:
            try:
                inicio = time.perf_counter()
                logger.info(
                    "INICIO | fluxo=%s | municipio=%s | exercicio=%s | referencia=%s",
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
                duracao = time.perf_counter() - inicio

                logger.info(
                    "SUCESSO | fluxo=%s | municipio=%s | exercicio=%s | referencia=%s | duracao_s=%.2f",
                    tipo,
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc,
                    duracao
                )

            except Exception as erro:
                falhou = True
                conexao.rollback()
                logger.exception(
                    "FALHA | fluxo=%s | municipio=%s | exercicio=%s | referencia=%s | duracao_s=%.2f",
                    tipo,
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc,
                    time.perf_counter() - inicio
                )
    return 1 if falhou else 0

if __name__ == "__main__":
    sys.exit(executar_pipeline())