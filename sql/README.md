# Estrutura do banco de dados — ObservaCE

## Objetivo

O arquivo `schema.sql` contém a estrutura das tabelas utilizadas pelo ObservaCE para armazenar informações municipais, receitas e despesas públicas.

Ele foi exportado utilizando o PostgreSQL 17.11 e contém as definições das tabelas `municipios`, `receitas` e `despesas`, incluindo seus tipos de dados, chaves e restrições.

**Importante:** o arquivo não contém registros e não cria o banco de dados. Ele cria a estrutura dentro de um banco PostgreSQL já existente.

## Como utilizar

Primeiro, crie um banco PostgreSQL vazio, utilizando o nome desejado.

Depois, execute o arquivo SQL nesse banco:

```bash
psql -U postgres -d nome_do_banco -v ON_ERROR_STOP=1 -f sql/schema.sql
```

O PostgreSQL executará as instruções do arquivo para criar as tabelas e suas restrições.
