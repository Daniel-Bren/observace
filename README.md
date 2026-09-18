# ObservaCE

Plataforma de dados públicos dos municípios do Ceará.

## Objetivo

Organizar e disponibilizar dados públicos municipais de forma mais acessível,
começando por informações fiscais e cadastrais dos municípios do Ceará.

## Fonte de dados

### TCE Ceará
Utilizando para obtenção dos municípios e dos seus respectivos códigos internos utilizados pelo TCE.

Endpoint utilizado atualmente:

`https://api-dados-abertos.tce.ce.gov.br/sim/municipios`

### IBGE
Utilizando para obtenção de dados oficiais de municípios do Ceará

Endpoint:
`https://servicodados.ibge.gov.br/api/v1/localidades/estados/CE/municipios`

## Integração
O campo `codigo_ibge` é utilizado como identificador comum entre os dois endpoints

Validação:
- O IBGE retornou 184 municípios
- O TCE retornou 185 registros (Uma espécie de registro do tribunal com a sigla `T.C.M`, sem código do IBGE)
- 184 registros do TCE correspondem aos 184 registros do IBGE.

## Coleta

O coletor consulta os municípios disponíveis na API do TCE-CE e transforma
os dados para o formato mínimo definido pelo ObservaCE:

- código TCE
- nome
- código IBGE
- UF

## Fluxo
1. Coleta municípios do TCE.
2. Transformar os dados para o formato do ObservaCE.
3. Coletar municípios do IBGE.
4. Transformar os dados para o mesmo formato.
5. Cruzar as duas dontes utilizando `codigo_ibge`.