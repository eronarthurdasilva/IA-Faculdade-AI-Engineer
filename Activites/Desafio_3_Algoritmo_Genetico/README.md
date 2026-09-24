# Algoritmo Genético para o Problema do Caixeiro Viajante

Este projeto implementa um algoritmo genético para resolver o Problema do Caixeiro Viajante (TSP) com 11 cidades. A solução encontrada tem distância total de 122,773, o que está de acordo com o valor esperado para o desafio.

## Objetivo

O objetivo é encontrar a rota com menor custo que visita todas as cidades exatamente uma vez e retorna à cidade de origem.

## Dados do problema

As coordenadas das cidades são:

- 1: (0, 0)
- 2: (3, 27)
- 3: (14, 22)
- 4: (1, 13)
- 5: (20, 3)
- 6: (20, 16)
- 7: (28, 12)
- 8: (30, 31)
- 9: (11, 19)
- 10: (7, 3)
- 11: (10, 25)

A distância entre duas cidades é calculada com a fórmula da distância Euclidiana:

$$
 d(a, b) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2 }
$$

## Como o algoritmo foi elaborado

O algoritmo genético foi implementado em etapas:

1. Geração da população
   - Cada indivíduo representa uma rota, isto é, uma permutação das cidades.
   - A população é inicializada com rotas aleatórias.

2. Avaliação da aptidão
   - A função de fitness é baseada na inversa da distância total da rota.
   - Quanto menor a distância, melhor o fitness.

3. Seleção por torneio
   - São escolhidos alguns indivíduos aleatoriamente.
   - O melhor entre eles é selecionado para reprodução.

4. Crossover ordenado (Order Crossover)
   - Mantém parte da ordem de um pai e completa o restante com os genes do outro pai.
   - Isso preserva a validade da rota como permutação.

5. Mutação
   - A mutação é feita por troca de posições entre cidades.
   - Também foi incluída uma melhoria local por 2-opt em algumas situações.

6. Elitismo
   - Os melhores indivíduos da geração são mantidos para a próxima população.

7. Execução em múltiplas rodadas
   - O algoritmo é executado várias vezes com sementes diferentes.
   - Isso aumenta a chance de encontrar uma rota ótima ou muito próxima do ótimo.

## Resultado encontrado

A melhor rota encontrada foi:

```python
[4, 2, 11, 9, 3, 8, 6, 7, 5, 10, 1]
```

Com distância total:

```python
122.7730
```

Esse valor corresponde ao custo da rota incluindo o retorno à cidade inicial.

## Print do resultado final

```text
======================================================================
INICIANDO 20 RODADAS DO ALGORITMO GENÉTICO PARA O TSP
======================================================================
Rodada   1/20 | Distância:   122.7730 | Tempo:   9.43s | Memória (pico):  236.55 KB  <-- NOVO MELHOR
Caminho da rodada 1: [11, 2, 4, 1, 10, 5, 7, 6, 8, 3, 9]
Rodada   2/20 | Distância:   122.7730 | Tempo:   8.51s | Memória (pico):  241.73 KB  <-- NOVO MELHOR
Caminho da rodada 2: [4, 2, 11, 9, 3, 8, 6, 7, 5, 10, 1]
Rodada   3/20 | Distância:   122.7730 | Tempo:   7.87s | Memória (pico):  241.70 KB
Caminho da rodada 3: [6, 8, 3, 9, 11, 2, 4, 1, 10, 5, 7]
...
Rodada  20/20 | Distância:   122.7730 | Tempo:   5.62s | Memória (pico):  241.65 KB
Caminho da rodada 20: [9, 3, 8, 6, 7, 5, 10, 1, 4, 2, 11]
======================================================================
RESULTADO FINAL APÓS TODAS AS RODADAS
======================================================================
Melhor distância encontrada : 122.7730
Melhor rota encontrada      : [4, 2, 11, 9, 3, 8, 6, 7, 5, 10, 1]
Tempo total de execução     : 110.22 segundos
Tempo médio por rodada      : 5.51 s
Memória média por rodada    : 241.43 KB
Pico de memória (maior)     : 241.83 KB
======================================================================
```

## Conclusão

A execução do algoritmo genético se mostrou eficiente para o problema, alcançando a rota ótima esperada com baixa variação entre as rodadas. A metodologia combina diversidade de população, seleção competitiva, reprodução por crossover e refinamento por mutação para explorar boas soluções de forma robusta.

## Como executar

No terminal, dentro da pasta do projeto, execute:

```bash
python resolution.py
```

## Arquivos do projeto

- `resolution.py`: implementação do algoritmo genético
- `README.md`: documentação do projeto e resultados

