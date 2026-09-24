# Terceiro trabalho pratico: Redes Neurais

O programa `classificar_motores.py` usa o arquivo `doc/Motores.xlsx`.

## Preparar o ambiente (Windows)

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O comando `pip install -r requirements.txt` executado fora do ambiente virtual pode usar o Python 3.14 instalado no sistema. O TensorFlow deste projeto deve ser instalado com Python 3.11.

## Executar

```bash
python classificar_motores.py --arquivo doc/Motores.xlsx
```

O programa treina com as 200 linhas rotuladas, separa 20% para validacao estratificada e classifica as 10 linhas da tabela de teste. Os resultados sao gravados na pasta `resultados/`:

- `classificacoes_motores.xlsx`: previsao e confianca de cada linha de teste;
- `modelo_motores.keras`: modelo TensorFlow salvo;
- `pesos_e_bias.txt`: pesos `Wij` e bias `bi` de cada camada treinavel;
- `historico_treinamento.csv`: historico de acuracia e perda.

## Topologia e treinamento

- Rede densa supervisionada, com retropropagacao do erro;
- 7 entradas, uma para cada medida da planilha;
- duas camadas ocultas com 16 e 8 neuronios, ativacao ReLU;
- camada de saida com 3 neuronios, ativacao softmax;
- normalizacao `StandardScaler` ajustada somente nos dados de treinamento;
- otimizador Adam, taxa de aprendizado 0,001, lote de 16;
- parada antecipada baseada na acuracia de validacao.

A acuracia final deve ser conferida na execucao, pois o resultado depende do ambiente e da amostra de validacao. A exigencia de 95% deve ser demonstrada pela metrica obtida, e nao presumida pelo codigo.