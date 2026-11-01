from coletor_balanco_tce import carregar_receitas
from carregar_despesas_tce import carregar_despesas
from conexao_banco import conexao
import sys


municipios = ["002", "057"]
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
                print(f"Iniciando {tipo} do municipio {municipio}")

                carregar(
                    municipio,
                    exercicio_orcamento,
                    data_referencia_doc
                )

                print(f"SUCESSO: {municipio} - {tipo}")

            except Exception as erro:
                falhou = True
                conexao.rollback()
                print(f"FALHA: {municipio} - {tipo}: {erro}")
    return 1 if falhou else 0


if __name__ == "__main__":
    executar_pipeline()