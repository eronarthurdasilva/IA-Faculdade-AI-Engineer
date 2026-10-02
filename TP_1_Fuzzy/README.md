# Trabalho prático — Lógica Fuzzy

Implementação em Python dos quatro sistemas fuzzy propostos em [`doc/Segundo Trabalho Prático sobre Lógica Fuzzy 26.pdf`](doc/Segundo%20Trabalho%20Pr%C3%A1tico%20sobre%20L%C3%B3gica%20Fuzzy%2026.pdf).

## Como executar

É necessário ter Python 3.10 ou superior instalado. No terminal, entre na pasta `TP_1_Fuzzy` e instale a biblioteca necessária para gerar o gráfico e o PDF:

```powershell
py -m pip install -r requirements.txt
```

Execute os quatro exemplos fixos do enunciado:

```powershell
py main.py
```

O programa mostra as respostas no terminal e cria `resultados.pdf` nesta pasta, com uma página e um gráfico da saída fuzzy para cada exercício. Cada gráfico mostra os consequentes ativados, a saída fuzzy agregada e o centroide. Para executar os testes:

```powershell
py -m unittest -v
```

Para informar valores próprios e obter a resposta calculada pelo sistema fuzzy, inicie o modo interativo:

```powershell
py main.py --interativo
```

Escolha A, B, C ou D e digite as entradas quando solicitadas. O programa aceita ponto ou vírgula decimal, valida os valores dentro dos universos das variáveis e calcula a saída com as regras do exercício. A cada cálculo, atualiza `resultados.pdf` com as entradas e o gráfico daquele resultado. Digite `Q` para sair. Sem `--interativo`, são calculados diretamente os exemplos fixos do documento e o PDF inclui os quatro.

## Estratégia fuzzy aplicada

Os quatro exercícios são sistemas de inferência **Mamdani** com fuzzificação por conjuntos triangulares, regras linguísticas e defuzzificação pelo **centroide**:

1. Cada entrada é convertida em graus de pertinência entre 0 e 1.
2. O operador **AND** combina antecedentes pelo mínimo; o **OR** combina graus pelo máximo.
3. A implicação corta o conjunto consequente pelo grau de ativação da regra (mínimo), e as saídas das regras são agregadas pelo máximo.
4. A saída fuzzy agregada é amostrada dentro do universo correspondente e convertida em um valor numérico pelo centroide.

As funções triangulares também representam conjuntos de ombro esquerdo ou direito quando dois vértices coincidem. Os passos numéricos de saída são 0,001 para vitalidade, 1 para risco, 0,01 para gorjeta e 0,05 para prêmio.

O centroide fornece o valor final da saída para as entradas informadas. O modelo não procura uma combinação ótima de entradas; ele aplica as regras fuzzy do documento a cada combinação recebida e defuzzifica a resposta.

## Modelos implementados

### A) Vitalidade das violetas

- Entradas: água `[0, 65]` ml e sol `[0, 95]` minutos.
- Água: pequena `(0, 0, 25)`, média `(20, 30, 45)`, grande `(35, 65, 65)`.
- Sol: pequeno `(0, 0, 30)`, médio `(25, 50, 65)`, grande `(60, 95, 95)`.
- Saída: ruim `(0, 0, 0.2)`, média `(0.1, 0.5, 0.9)`, boa `(0.8, 1, 1)`.
- A base de regras é a tabela 3 × 3 exibida no PDF. A saída solicitada usa 45 ml e 50 minutos.
- O código também calcula o caso de conferência do enunciado (40 ml e 60 minutos), cujo resultado esperado é aproximadamente `0.625`.

### B) Política de crédito

- Entradas: score de mercado e score do motorista `[0, 1000]`; engajamento `[0, 5000]`.
- Os seis ratings dos dois scores usam os triângulos: Rating 1 `(800, 900, 1000)`, Rating 2 `(700, 800, 900)`, Rating 3 `(600, 700, 800)`, Rating 4 `(400, 500, 600)`, Rating 5 `(200, 300, 400)` e Rating 6 `(0, 200, 300)`.
- Engajamento: baixo `(0, 0, 100)`, médio `(0, 100, 200)`, alto `(200, 1000, 5000)`.
- A saída risco `[0, 1000]` usa os cinco conjuntos da figura e as oito regras listadas no PDF. O enunciado não enumera pares entre as duas entradas de score; para codificar essas regras, cada grupo citado é expandido em combinações AND entre ratings do motorista e do mercado do mesmo grupo.
- O valor `score_mercado = 2` foi interpretado literalmente como valor numérico no universo `[0, 1000]`, conforme escolha confirmada para esta implementação; não como a categoria linguística Rating 2.

### C) Gorjeta

- Qualidade da comida e do serviço: `[0, 10]`, com termos ruim, aceitável e excelente/incrível.
- Gorjeta: `[0, 25]`, com termos baixa, média e alta.
- As três regras são as do PDF: comida ruim **OU** serviço ruim implica gorjeta baixa; serviço aceitável implica média; comida excelente **OU** serviço incrível implica alta.
- Entradas solicitadas: comida `6.5` e serviço `9.8`.

### D) Prêmio do seguro

- Idade: `[20, 70]`, com os termos muito jovem, jovem, idade média, maduro e idoso.
- Saúde: `[0, 1]`, com os termos muito péssimo, péssimo, médio, bom e muito bom.
- Prêmio: `[0, 100]`, com os sete termos mostrados no gráfico.
- A base de regras 5 × 5 foi transcrita da tabela do PDF, cruzando cada categoria de saúde e idade.
- Entradas solicitadas: idade `32` anos e saúde `0.7`.

Os vértices dos conjuntos foram lidos dos gráficos do enunciado; onde o PDF não imprime os pontos numericamente, foram estimados pela posição dos triângulos em relação aos eixos.
