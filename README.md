# Classificador de Imóveis em Piracicaba

Este projeto tem como objetivo oferecer uma visão abrangente do mercado imobiliário em Piracicaba, utilizando técnicas de webscraping e algoritmos de classificação para coletar dados e prever o preço de mercado dos imóveis com base em diversos fatores, tais como localização, tipo de imóvel, tamanho, idade e comodidades.

## Tecnologias Utilizadas

- Python
- BeautifulSoup
- Pandas
- Streamlit

### Pré-requisitos

- Python 3.x
- Bibliotecas BeautifulSoup e Pandas instaladas
- Streamlit instalado

## Como utilizar

O projeto é composto por um código em Python que realiza o webscraping das principais imobiliárias da região de Piracicaba, coleta os dados dos imóveis e agrega os mesmos em uma visualização de fácil compreensão.

Para utilizar o Classificador acesse o link abaixo:

https://real-estate-predictor.streamlit.app/

## Funções

O código contém as seguintes funções:

- webscraping: coleta os dados dos imóveis nas principais imobiliárias de Piracicaba;
- apresentação: apresenta os resultados das previsões em uma tabela dentro do aplicativo e em um arquivo csv

## Contribuição

Se você deseja contribuir para este projeto, siga os seguintes passos:

1. Faça um fork do repositório
2. Crie um branch com sua contribuição: `git checkout -b minha-contribuicao`
3. Realize as mudanças e faça o commit: `git commit -m 'Minha contribuição'`
4. Faça o push para o seu branch: `git push origin minha-contribuicao`
5. Crie um Pull Request no repositório original

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

# Agradecimentos
Gostaría de agradecer ao professor Dr. Gustavo Voltani Von Atzingen pela orientação e disponibilidade durante o desenvolvimento do projeto.

## Catálogo local de São Paulo e app iOS

Os coletores `LopesLT` e `LopesRTG` extraem anúncios de venda de São Paulo capital, com limites de coleta sequencial (duas páginas e dez imóveis destacados, respectivamente). Eles estão desativados no orquestrador agendado por enquanto; a exportação local abaixo pode usá-los diretamente, sem credenciais de banco:

```sh
uv sync
uv run python scripts/export_catalog.py --sources LopesLT LopesRTG Premier --output ../real-estate-web/backend/catalog.json
cp ../real-estate-web/backend/catalog.json ../real-estate-web/ios/RealEstate/Resources/catalog.json
```

O exportador informa falhas de fontes, deduplica por URL, mantém fontes anteriores que não foram atualizadas e grava o arquivo atomicamente. Se não houver resultados válidos, preserva o arquivo anterior. Campos ausentes permanecem nulos. Esta primeira coleta não cobre todo o catálogo das imobiliárias.

O app SwiftUI e as instruções de instalação pessoal ficam em `real-estate-web/ios`. Não há publicação na App Store ou serviço público nesta versão.

### Banco com várias cidades

Para banco novo: `sql/init.sql` já inclui `cidade` e `uf`. Para banco existente: aplique manualmente `sql/catalog_cities.sql` e depois `sql/security.sql` antes de ativar os novos coletores em `config/config.json`. Registros antigos recebem cidade `Piracicaba` por padrão. Revise esse padrão se o banco já contiver anúncios de outras cidades.

O carregamento usa uma transação para staging, lookups e promoção para `imovel`; atualiza anúncios por URL preservando o histórico de primeira coleta e atualizando `last_seen`. Extrações vazias não apagam dados. Bancos antigos sem as colunas de cidade continuam aceitando Piracicaba; outras cidades exigem a migração. A migração opcional de particionamento `sql/partition_imovel.sql` NÃO é compatível com o upsert por URL desta versão e não deve ser aplicada.

```sh
uv run pytest -q
```

Os testes de transação usam SQLite com adaptação de TRUNCATE; não substituem a validação de migração em uma cópia do Postgres real.
