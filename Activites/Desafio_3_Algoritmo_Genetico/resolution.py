"""
Algoritmo Genético para o Problema do Caixeiro Viajante (TSP)
PUC Minas - Inteligência Artificial - Exercício 03 - Desafio

Objetivo: encontrar o menor caminho que passa por todas as 11 cidades
e volta à cidade de origem. Resposta esperada pelo enunciado: 122,773

O script roda VÁRIAS execuções (rodadas) do algoritmo genético,
cada uma com sua própria população/seed, e ao final reporta:
- a melhor rota encontrada em cada rodada
- distância da melhor rota da rodada
- tempo de execução da rodada
- pico de memória usada pela rodada (via tracemalloc)
- ao final, o melhor resultado global entre todas as rodadas
"""

import random
import time
import tracemalloc
import math

# ------------------------------------------------------------------
# 1. Dados do problema
# ------------------------------------------------------------------
CIDADES = {
    1: (0, 0),
    2: (3, 27),
    3: (14, 22),
    4: (1, 13),
    5: (20, 3),
    6: (20, 16),
    7: (28, 12),
    8: (30, 31),
    9: (11, 19),
    10: (7, 3),
    11: (10, 25),
}

IDS_CIDADES = list(CIDADES.keys())
N_CIDADES = len(IDS_CIDADES)

# ------------------------------------------------------------------
# 2. Funções auxiliares
# ------------------------------------------------------------------
def distancia(c1, c2):
    x1, y1 = CIDADES[c1]
    x2, y2 = CIDADES[c2]
    return math.hypot(x2 - x1, y2 - y1)

# Pré-calcula a matriz de distâncias para não recalcular toda hora
MATRIZ_DIST = {
    (a, b): distancia(a, b)
    for a in IDS_CIDADES
    for b in IDS_CIDADES
}

def distancia_rota(rota):
    """Distância total da rota, incluindo volta à cidade inicial."""
    total = 0.0
    for i in range(len(rota)):
        cidade_atual = rota[i]
        proxima_cidade = rota[(i + 1) % len(rota)]
        total += MATRIZ_DIST[(cidade_atual, proxima_cidade)]
    return total

def cria_individuo():
    """Um indivíduo é uma permutação aleatória das cidades."""
    individuo = IDS_CIDADES[:]
    random.shuffle(individuo)
    return individuo

def cria_populacao(tamanho):
    return [cria_individuo() for _ in range(tamanho)]

def fitness(individuo):
    """Quanto menor a distância, maior o fitness (invertido)."""
    return 1.0 / distancia_rota(individuo)

def selecao_torneio(populacao, fitnesses, k=3):
    """Seleciona um indivíduo via torneio de tamanho k."""
    participantes = random.sample(range(len(populacao)), k)
    melhor = max(participantes, key=lambda i: fitnesses[i])
    return populacao[melhor]

def crossover_ordenado(pai1, pai2):
    """Order Crossover (OX) - preserva a validade da permutação."""
    tamanho = len(pai1)
    inicio, fim = sorted(random.sample(range(tamanho), 2))

    filho = [None] * tamanho
    filho[inicio:fim] = pai1[inicio:fim]

    genes_restantes = [g for g in pai2 if g not in filho[inicio:fim]]

    pos = 0
    for i in range(tamanho):
        if filho[i] is None:
            filho[i] = genes_restantes[pos]
            pos += 1

    return filho

def mutacao_swap(individuo, taxa_mutacao):
    """Troca duas cidades de posição com certa probabilidade."""
    individuo = individuo[:]
    for i in range(len(individuo)):
        if random.random() < taxa_mutacao:
            j = random.randrange(len(individuo))
            individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo

def mutacao_2opt_local(individuo):
    """Busca local 2-opt leve, aplicada ocasionalmente para refinar."""
    melhor = individuo[:]
    melhor_dist = distancia_rota(melhor)
    tamanho = len(individuo)

    i, j = sorted(random.sample(range(tamanho), 2))
    if j - i < 2:
        return melhor

    novo = melhor[:i] + melhor[i:j][::-1] + melhor[j:]
    nova_dist = distancia_rota(novo)

    if nova_dist < melhor_dist:
        return novo
    return melhor

# ------------------------------------------------------------------
# 3. Algoritmo Genético (uma rodada completa)
# ------------------------------------------------------------------
def algoritmo_genetico(
    tamanho_populacao=150,
    geracoes=500,
    taxa_mutacao=0.02,
    elitismo=5,
    usar_2opt=True,
    seed=None,
    retorna_historico=False,
):
    if seed is not None:
        random.seed(seed)

    populacao = cria_populacao(tamanho_populacao)
    melhor_individuo_global = None
    melhor_distancia_global = float("inf")
    historico_geracoes = []

    for geracao in range(geracoes):
        fitnesses = [fitness(ind) for ind in populacao]

        # Guarda o melhor da geração
        idx_melhor = max(range(len(populacao)), key=lambda i: fitnesses[i])
        melhor_rota_geracao = populacao[idx_melhor][:]
        dist_melhor_geracao = distancia_rota(melhor_rota_geracao)
        historico_geracoes.append({
            "geracao": geracao + 1,
            "rota": melhor_rota_geracao,
            "distancia": dist_melhor_geracao,
        })

        if dist_melhor_geracao < melhor_distancia_global:
            melhor_distancia_global = dist_melhor_geracao
            melhor_individuo_global = melhor_rota_geracao[:]

        # Elitismo: mantém os N melhores sem alteração
        ordenados = sorted(
            range(len(populacao)), key=lambda i: fitnesses[i], reverse=True
        )
        nova_populacao = [populacao[i][:] for i in ordenados[:elitismo]]

        # Preenche o resto da população via seleção + crossover + mutação
        while len(nova_populacao) < tamanho_populacao:
            pai1 = selecao_torneio(populacao, fitnesses)
            pai2 = selecao_torneio(populacao, fitnesses)
            filho = crossover_ordenado(pai1, pai2)
            filho = mutacao_swap(filho, taxa_mutacao)

            if usar_2opt and random.random() < 0.1:
                filho = mutacao_2opt_local(filho)

            nova_populacao.append(filho)

        populacao = nova_populacao

    if retorna_historico:
        return melhor_individuo_global, melhor_distancia_global, historico_geracoes
    return melhor_individuo_global, melhor_distancia_global

# ------------------------------------------------------------------
# 4. Execução de MÚLTIPLAS rodadas, com tempo e memória de cada uma
# ------------------------------------------------------------------
def formata_bytes(n_bytes):
    for unidade in ["B", "KB", "MB", "GB"]:
        if n_bytes < 1024:
            return f"{n_bytes:.2f} {unidade}"
        n_bytes /= 1024
    return f"{n_bytes:.2f} TB"

def executa_multiplas_rodadas(
    n_rodadas=20,
    tamanho_populacao=150,
    geracoes=500,
    taxa_mutacao=0.02,
    elitismo=5,
    mostrar_historico_geracoes=False,
):
    print("=" * 70)
    print(f"INICIANDO {n_rodadas} RODADAS DO ALGORITMO GENÉTICO PARA O TSP")
    print("=" * 70)

    melhor_rota_absoluta = None
    melhor_distancia_absoluta = float("inf")
    resultados = []

    tempo_inicio_total = time.perf_counter()

    for rodada in range(1, n_rodadas + 1):
        tracemalloc.start()
        tempo_inicio = time.perf_counter()

        rota, dist, historico_geracoes = algoritmo_genetico(
            tamanho_populacao=tamanho_populacao,
            geracoes=geracoes,
            taxa_mutacao=taxa_mutacao,
            elitismo=elitismo,
            seed=rodada,
            retorna_historico=True,
        )

        tempo_fim = time.perf_counter()
        memoria_atual, memoria_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tempo_execucao = tempo_fim - tempo_inicio

        resultados.append({
            "rodada": rodada,
            "distancia": dist,
            "rota": rota,
            "tempo": tempo_execucao,
            "memoria_pico": memoria_pico,
            "historico_geracoes": historico_geracoes,
        })

        marcador = ""
        if dist < melhor_distancia_absoluta:
            melhor_distancia_absoluta = dist
            melhor_rota_absoluta = rota
            marcador = "  <-- NOVO MELHOR"

        print(
            f"Rodada {rodada:>3}/{n_rodadas} | "
            f"Distância: {dist:10.4f} | "
            f"Tempo: {tempo_execucao:6.2f}s | "
            f"Memória (pico): {formata_bytes(memoria_pico):>10}"
            f"{marcador}"
        )
        print(f"Caminho da rodada {rodada}: {rota}")

        if mostrar_historico_geracoes:
            print(f"Histórico de melhores caminhos por geração na rodada {rodada}:")
            for item in historico_geracoes:
                print(
                    f"  Geração {item['geracao']:>3} | "
                    f"Distância: {item['distancia']:10.4f} | "
                    f"Rota: {item['rota']}"
                )

    tempo_fim_total = time.perf_counter()
    tempo_total = tempo_fim_total - tempo_inicio_total

    print("=" * 70)
    print("RESULTADO FINAL APÓS TODAS AS RODADAS")
    print("=" * 70)
    print(f"Melhor distância encontrada : {melhor_distancia_absoluta:.4f}")
    print(f"Melhor rota encontrada      : {melhor_rota_absoluta}")
    print(f"Tempo total de execução     : {tempo_total:.2f} segundos")

    tempos = [r["tempo"] for r in resultados]
    memorias = [r["memoria_pico"] for r in resultados]

    print(f"Tempo médio por rodada      : {sum(tempos)/len(tempos):.2f} s")
    print(f"Memória média por rodada    : {formata_bytes(sum(memorias)/len(memorias))}")
    print(f"Pico de memória (maior)     : {formata_bytes(max(memorias))}")
    print("=" * 70)

    return melhor_rota_absoluta, melhor_distancia_absoluta, resultados


if __name__ == "__main__":
    # Parâmetros ajustáveis:
    # n_rodadas: quantas execuções independentes do GA serão feitas
    # geracoes: quantas gerações cada execução evolui
    # tamanho_populacao: quantos indivíduos por geração
    executa_multiplas_rodadas(
        n_rodadas=20,
        tamanho_populacao=150,
        geracoes=500,
        taxa_mutacao=0.02,
        elitismo=5,
        mostrar_historico_geracoes=False,
    )