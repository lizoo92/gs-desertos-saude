# Distribuição das UBS por habitante nos distritos da cidade de São Paulo

Projeto da **Global Solution FIAP 2026/2 (CitizenTech)**, curso de Ciência de Dados.
Ideia #4: *onde faltam serviços de saúde*.

- Grupo: Luiz Fernando de Oliveira Pupo, Victor Cabrini, Tiago Sanches Biscari
- Vídeo (até 5 min): [preencher link do YouTube]
- Repositório público no GitHub.

## 1. O que o projeto faz

Cruza a população de cada um dos **96 distritos** do município de São Paulo (IBGE, Censo 2022)
com as **UBS públicas** (GeoSampa) e mostra o resultado em um mapa coroplético interativo.

Indicador principal: **UBS públicas por 100 mil habitantes**, calculado como
`qtd_ubs / população × 100.000`.

O indicador mede a **oferta pública de UBS por habitante**, e não a necessidade de saúde.
Por isso o mapa usa os termos "menor oferta" e "maior oferta".

Como o mapa é construído:
- Classe 0: distritos sem nenhuma UBS pública dentro do limite (4 distritos).
- Classes 1 a 7: 7 faixas por quantil entre os distritos com UBS, excluindo os outliers
  (1 = menor oferta, 7 = maior oferta).
- Classe 8: outliers (Marsilac e Parelheiros). Critério: indicador acima da cerca de Tukey
  **e** densidade abaixo da cerca de Tukey (na escala logarítmica).
  Nesses dois distritos de território extenso e pouco povoado, o indicador por habitante
  pode superestimar a oferta, pois não mede distância.

O que o mapa tem:
- Camadas nomeadas, que podem ser ligadas e desligadas: distritos (UBS por 100 mil habitantes) e pontos das UBS públicas.
- Ao passar o mouse sobre um distrito: população, área (km²), número de UBS, o indicador e a faixa.
- Nomes dos distritos que aparecem conforme o zoom, com anticolisão automática.
- Legenda com as 7 faixas, os outliers e os distritos sem UBS, e uma nota dizendo que o mapa mede
  oferta, e não necessidade, e que o valor é do distrito, e não de cada bairro.
- Ranking de distritos ordenável: clique no título da coluna para ordenar.
  Distritos sem UBS aparecem como "sem UBS no distrito", e os outliers com "(outlier)".
- Aviso nos distritos sem UBS: pode haver cobertura por UBS de distritos vizinhos, e a população flutuante não é contada.

## 2. Principais resultados (exploratórios)

Todos os números vêm das saídas dos scripts deste repositório.

- 96 distritos analisados; 4 sem nenhuma UBS pública; 481 UBS no total.
- Cerca de um terço dos distritos tem 2 UBS ou menos.
- Associação inversa forte entre renda e oferta de UBS: correlação de Spearman de
  aproximadamente -0,7 (entre -0,70 e -0,73, conforme o recorte e a medida de renda).
- Entre os 20 distritos com renda média do responsável acima de R$ 8.000
  (cerca de 5 salários mínimos), a mediana foi de 1,8 UBS por 100 mil habitantes,
  contra 4,3 nos demais 76.
- Esses distritos de renda alta não são menores nem mais densos que a mediana da cidade.
  Portanto, a área não explica a diferença.

**Interpretação (hipótese, não testada):** menor dependência do SUS em áreas de renda mais alta
pode explicar parte do padrão. Os dados mostram associação, não causa.

## 3. Estrutura do repositório

```
.
├── codigo/       scripts em Python, numerados na ordem de execução
├── dados/
│   ├── bruto/    arquivos baixados das fontes, sem alteração
│   └── tratado/  tabelas geradas pelos scripts
├── saidas/       mapa interativo (HTML) e gráficos (PNG)
├── requirements.txt
└── README.md
```

### Scripts

| Script | O que faz |
|---|---|
| `01_populacao.py` | Prepara a população por distrito (Censo 2022) |
| `02_ubs_por_distrito.py` | Conta as UBS públicas dentro de cada distrito |
| `03_cruzamento.py` | Cruza população e UBS, calcula o indicador e define as classes 0 a 8 |
| `04_mapa.py` | Gera o mapa interativo em `saidas/mapa_ubs_distrito.html` |
| `05_densidade.py` | Densidade demográfica e verificação dos outliers |
| `06_boxplot.py` | Boxplots (cercas de Tukey) para procurar outros outliers |
| `07_populacao_ubs.py` | Dispersão população × número de UBS e referência de habitantes por UBS |
| `08_poucas_ubs.py` | Lista os distritos com 0 ou 1 UBS |
| `09_inspeciona_renda.py` | Inspeciona o arquivo de renda do IBGE |
| `10_renda_ubs.py` | Correlação e quartis de renda × UBS; gráfico `renda_x_ubs.png` |
| `11_renda_alta.py` | Distritos de renda alta, com área, densidade e km² por UBS |

## 4. Como executar

Requisitos: Python 3 e Git. Os comandos abaixo são para macOS ou Linux.

```
git clone https://github.com/lizoo92/gs-desertos-saude.git
cd gs-desertos-saude
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Rode sempre **a partir da raiz do projeto**, pois os scripts usam caminhos relativos:

```
python codigo/01_populacao.py
python codigo/02_ubs_por_distrito.py
python codigo/03_cruzamento.py
python codigo/04_mapa.py
```

Os scripts `05` a `11` são exploratórios e podem ser rodados em qualquer ordem depois do `03`.
O mapa é salvo em `saidas/mapa_ubs_distrito.html` (abra no navegador).
O mapa de fundo é do OpenStreetMap, então é preciso estar com internet para ele aparecer.

## 5. Bibliotecas

Versões do `requirements.txt`:

| Biblioteca | Versão | Uso no projeto |
|---|---|---|
| pandas | 3.1.1 | tabelas, cruzamentos, quantis, correlação |
| geopandas | 1.2.0 | leitura dos `.gpkg`, área dos distritos, geometrias |
| shapely, pyogrio, pyproj | 2.2.0, 0.13.0, 3.8.0 | geometria, leitura de arquivos geográficos e projeções (dependências do geopandas) |
| folium | 0.20.0 | mapa interativo (Leaflet) |
| branca, Jinja2 | 0.8.2, 3.1.6 | elementos HTML/JS do mapa (legenda, ranking, rótulos por zoom) |
| matplotlib | 3.11.2 | boxplots e gráficos de dispersão |
| scipy | 1.18.1 | cálculo da correlação de Spearman no pandas |
| openpyxl | 3.1.5 | leitura do dicionário de dados do IBGE (`.xlsx`) |
| numpy | 2.5.4 | cálculos numéricos (por exemplo, cercas em log10) |

## 6. Fontes e bibliografia

### Dados de saúde (UBS e território)

- PREFEITURA DE SÃO PAULO. **GeoSampa**: Mapa Digital da Cidade de São Paulo.
  Camada *Distrito Municipal* (`geoportal_distrito_municipal_v2.gpkg`).
  Disponível em: https://geosampa.prefeitura.sp.gov.br. Acesso em: [preencher data].
- PREFEITURA DE SÃO PAULO. **GeoSampa**. Camada *Equipamento de Saúde: UBS / Posto de Saúde / Centro de Saúde*
  (`geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg`). Mesmo portal. Acesso em: [preencher data].
- PREFEITURA DE SÃO PAULO. **GeoSampa**. Camada *Abrangência das UBS*
  (`geoportal_equipamento_saude_abrangencia_ubs.gpkg`). Baixada, ainda não usada na análise.
- A camada de distritos registra atualização em 27/10/2026 (campo `dt_atualizacao`).

### Dados de população e renda

- IBGE. **Censo Demográfico 2022: Agregados por Setores Censitários**, tabelas agregadas por distritos:
  *básico* (`Agregados_por_distritos_basico_BR`) e *rendimento do responsável*
  (`Agregados_por_distritos_renda_responsavel_BR`). Arquivos datados de 20/05/2026.
  URL do download: [preencher a URL exata do FTP do IBGE]. Acesso em: [preencher data].
- IBGE. **Dicionário de dados: agregados por setores censitários** (`dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx`).
- IBGE. **Notas metodológicas** sobre o rendimento do responsável pelo domicílio (Censo 2022):
  https://biblioteca.ibge.gov.br/visualizacao/livros/liv102175.pdf e
  https://biblioteca.ibge.gov.br/visualizacao/livros/liv102277.pdf.

**Atenção sobre a renda:** a renda usada é a do **responsável pelo domicílio**, não a per capita.
Os campos `V06004` e `V06006` parecem ser a média e a mediana, mas **não estão definidos** no dicionário
baixado nem nas notas consultadas. Por isso, os testes usam os dois campos, e o resultado é o mesmo.

### Referências para faixas de renda (consultadas, não adotadas)

Os critérios de classe social divergem entre si e usam a renda do domicílio inteiro.
Por isso, o projeto descreve os cortes em salários mínimos.
Consultadas em 10/11/2026 (reportagens, sem fonte primária conferida):
- Tribuna de Minas, 2026: https://tribunademinas.com.br/colunas/maistendencias/?p=49404
- Istoé Dinheiro (critério FGV Social): https://istoedinheiro.com.br/quanto-renda-classe-social
- Tribuna de Minas, 2025 (critério Tendências): https://tribunademinas.com.br/colunas/maistendencias/?p=26881
- O Antagonista, valor do salário mínimo de 2026 (R$ 1.621), **a confirmar em fonte oficial**:
  https://oantagonista.com.br/ladooa/entretenimento/quanto-e-preciso-ganhar-para-entrar-na-classe-alta-em-2026/

### Método

- TUKEY, J. W. **Exploratory Data Analysis**. Addison-Wesley, 1977 (cercas de Tukey / boxplot).
- Referência de habitantes por UBS (18 mil sem ESF; 12 mil com ESF): Política Nacional de Atenção Básica,
  Portaria GM/MS nº 2.488/2011. **Verificar se continua em vigor antes de citar no relatório.**

## 7. Limitações

Resumo; o texto completo está no relatório do projeto.
- O indicador mede oferta **relativa por habitante**, não a necessidade de saúde, nem distância ou tempo de deslocamento.
- Considera **apenas UBS públicas**. Não inclui rede privada, AMA, hospitais ou outros equipamentos.
- O valor é do distrito, e não de cada bairro. A população flutuante não é contada.
- População do Censo 2022 combinada com camadas de 2025/2026.
- Efeito de borda: moradores podem usar UBS de distritos vizinhos (não testado).
- Poucas UBS por distrito (contagens pequenas): o indicador varia muito com uma UBS a mais ou a menos.
- A associação com renda é entre distritos, não entre pessoas (falácia ecológica), e a renda é a do responsável.

## 8. Ética de dados

- Todos os dados são públicos e agregados por distrito. Não há dados pessoais.
- A renda aparece como **contexto**, não como justificativa para a baixa oferta de UBS.
  O mapa mantém o indicador original, para não esconder distritos onde o serviço pode faltar.
