# ObservaCE

Plataforma de dados públicos dos municípios do Ceará.

## Objetivo

Organizar e disponibilizar dados públicos municipais de forma mais acessível,
começando por informações fiscais e cadastrais dos municípios do Ceará.

## Fonte de dados atual
API de Dados Abertos do Tribunal de Contas do Estado do Ceará (TCE-CE).

Endpoint utilizado atualmente:

`https://api-dados-abertos.tce.ce.gov.br/sim/municipios`

## Coleta

O coletor consulta os municípios disponíveis na API do TCE-CE e transforma
os dados para o formato mínimo definido pelo ObservaCE:

- código TCE
- nome
- código IBGE
- UF

## Como executar

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python coletor_municipios_tce.py