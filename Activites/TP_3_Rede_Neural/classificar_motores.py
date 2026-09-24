"""Treina uma rede neural TensorFlow para classificar os motores.

Uso:
    python classificar_motores.py --arquivo doc/Motores.xlsx
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


SEED = 42
TARGET_COLUMN = "Tipo de rotor"
FEATURES = [
    "Diametro",
    "Raio B1",
    "Espessura",
    "Bitola F1",
    "Comprimento C4",
    "Lagura L2",
    "Altura D6",
]


def configurar_reprodutibilidade() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)


def ler_planilha(caminho: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê o bloco de treinamento A:H e o bloco de teste K:R."""
    treinamento = pd.read_excel(caminho, sheet_name=0, header=2, usecols="A:H")
    teste = pd.read_excel(caminho, sheet_name=0, header=2, usecols="K:R")

    treinamento.columns = FEATURES + [TARGET_COLUMN]
    teste.columns = FEATURES + [TARGET_COLUMN]
    treinamento = treinamento.dropna(subset=FEATURES + [TARGET_COLUMN])
    teste = teste.dropna(subset=FEATURES)

    for coluna in FEATURES:
        treinamento[coluna] = pd.to_numeric(treinamento[coluna], errors="raise")
        teste[coluna] = pd.to_numeric(teste[coluna], errors="raise")
    treinamento[TARGET_COLUMN] = pd.to_numeric(
        treinamento[TARGET_COLUMN], errors="raise"
    ).astype(int)
    return treinamento, teste


def criar_modelo(numero_atributos: int) -> tf.keras.Model:
    """Topologia: 7 entradas -> 16 -> 8 -> 3 saídas softmax."""
    modelo = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(numero_atributos,), name="entradas"),
            tf.keras.layers.Dense(16, activation="relu", name="oculta_1"),
            tf.keras.layers.Dense(8, activation="relu", name="oculta_2"),
            tf.keras.layers.Dense(3, activation="softmax", name="saida"),
        ],
        name="classificador_motores",
    )
    modelo.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return modelo


def salvar_pesos(modelo: tf.keras.Model, destino: Path) -> None:
    with destino.open("w", encoding="utf-8") as arquivo:
        for camada in modelo.layers:
            pesos = camada.get_weights()
            if len(pesos) != 2:
                continue
            matriz, bias = pesos
            arquivo.write(f"[{camada.name}]\n")
            arquivo.write(f"W (pesos Wij) =\n{matriz}\n")
            arquivo.write(f"b (bias bi) =\n{bias}\n\n")


def executar(caminho: Path, epocas: int, pasta_saida: Path) -> None:
    configurar_reprodutibilidade()
    treinamento, teste = ler_planilha(caminho)

    entradas = treinamento[FEATURES].to_numpy(dtype=np.float32)
    classes = treinamento[TARGET_COLUMN].to_numpy(dtype=np.int64) - 1
    x_treino, x_validacao, y_treino, y_validacao = train_test_split(
        entradas,
        classes,
        test_size=0.2,
        random_state=SEED,
        stratify=classes,
    )

    normalizador = StandardScaler()
    x_treino = normalizador.fit_transform(x_treino).astype(np.float32)
    x_validacao = normalizador.transform(x_validacao).astype(np.float32)

    modelo = criar_modelo(len(FEATURES))
    parada = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=40, restore_best_weights=True
    )
    historico = modelo.fit(
        x_treino,
        y_treino,
        validation_data=(x_validacao, y_validacao),
        epochs=epocas,
        batch_size=16,
        callbacks=[parada],
        verbose=1,
    )

    perda, acuracia = modelo.evaluate(x_validacao, y_validacao, verbose=0)
    previsoes_validacao = np.argmax(modelo.predict(x_validacao, verbose=0), axis=1)
    print(f"Acuracia da validacao: {acuracia:.2%} | perda: {perda:.4f}")
    print("Matriz de confusao (classes 1, 2, 3):")
    print(confusion_matrix(y_validacao + 1, previsoes_validacao + 1, labels=[1, 2, 3]))
    print(classification_report(y_validacao + 1, previsoes_validacao + 1, labels=[1, 2, 3]))

    x_teste = normalizador.transform(teste[FEATURES]).astype(np.float32)
    probabilidades = modelo.predict(x_teste, verbose=0)
    classes_teste = np.argmax(probabilidades, axis=1) + 1
    resultado = teste[FEATURES].copy()
    resultado["Tipo de rotor previsto"] = classes_teste
    resultado["Confianca"] = probabilidades.max(axis=1)

    pasta_saida.mkdir(parents=True, exist_ok=True)
    resultado.to_excel(pasta_saida / "classificacoes_motores.xlsx", index=False)
    modelo.save(pasta_saida / "modelo_motores.keras")
    salvar_pesos(modelo, pasta_saida / "pesos_e_bias.txt")
    pd.DataFrame(historico.history).to_csv(
        pasta_saida / "historico_treinamento.csv", index=False
    )

    print("\nClassificacoes da tabela de teste:")
    print(resultado[["Tipo de rotor previsto", "Confianca"]].to_string(index=False))
    print(f"\nArquivos salvos em: {pasta_saida.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arquivo", type=Path, default=Path("doc/Motores.xlsx"))
    parser.add_argument("--epocas", type=int, default=500)
    parser.add_argument("--saida", type=Path, default=Path("resultados"))
    args = parser.parse_args()
    executar(args.arquivo, args.epocas, args.saida)


if __name__ == "__main__":
    main()