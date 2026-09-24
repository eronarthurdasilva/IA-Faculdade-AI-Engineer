"""Treina, avalia e documenta a classificacao de predisposicao a hipertensao."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import keras
import tensorflow as tf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
FEATURES = [
    "Idade", "Sexo", "Tipo Sanguinio", "Fator RH", "Colesterol", "HDL",
    "Triglicerídeos", "Creatinina", "Peso (Kg)", "Altura (cm)", "Glicemia",
    "Gamma GT", "Sódio/Potássio",
]
CATEGORICAL = ["Sexo", "Tipo Sanguinio", "Fator RH"]
NUMERIC = [feature for feature in FEATURES if feature not in CATEGORICAL]
TARGET = "Classe A+ até F-"


def set_seed() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)


def load_data(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(path, sheet_name=0, header=None)
    train = raw.iloc[2:, :14].copy()
    train.columns = raw.iloc[1, :14].tolist()
    train = train.dropna(subset=["Idade", TARGET])
    test = raw.iloc[2:, 15:29].copy()
    test.columns = raw.iloc[1, 15:29].tolist()
    test = test.dropna(subset=["Idade"])
    return train, test


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ]
    )


def build_model(input_size: int, class_count: int) -> keras.Model:
    model = keras.Sequential([
        keras.layers.Input(shape=(input_size,), name="atributos_entrada"),
        keras.layers.Dense(64, activation="relu", name="oculta_1"),
        keras.layers.Dropout(0.20, name="regularizacao"),
        keras.layers.Dense(32, activation="relu", name="oculta_2"),
        keras.layers.Dense(class_count, activation="softmax", name="saida"),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Light Shading Accent 1"
    for cell, header in zip(table.rows[0].cells, headers):
        cell.text = header
    for row in rows:
        for cell, value in zip(table.add_row().cells, row):
            cell.text = str(value)


def write_report(path: Path, data: dict, confusion_path: Path, history_path: Path) -> None:
    document = Document()
    title = document.add_heading("Classificação de Predisposição para Hipertensão", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph("Trabalho prático de Redes Neurais e Deep Learning")
    document.add_heading("1. Dados e objetivo", level=1)
    document.add_paragraph(
        f"A planilha contém {data['train_rows']} exemplos de treinamento e "
        f"{data['test_rows']} exemplos para classificação. O objetivo é prever uma "
        f"das classes {', '.join(data['classes'])} usando {len(FEATURES)} atributos."
    )
    document.add_paragraph(
        "Os atributos categóricos foram transformados por one-hot encoding e os "
        "numéricos foram padronizados com média 0 e desvio padrão 1. A divisão "
        "de treino e validação foi estratificada, com 20% para validação."
    )
    document.add_heading("2. Topologia e treinamento", level=1)
    document.add_paragraph(
        "Rede feed-forward (MLP), supervisionada, com uma camada de entrada, "
        "duas camadas ocultas e uma camada de saída. As camadas ocultas usam ReLU, "
        "a saída usa softmax e há dropout de 20% entre as camadas ocultas. "
        "O otimizador é Adam (taxa de aprendizagem 0,001), a função de perda é "
        "entropia cruzada categórica esparsa e foram executadas "
        f"{data['epochs']} épocas com lote de {data['batch_size']}."
    )
    add_table(document, ["Camada", "Neurônios", "Ativação"], [
        ["Entrada", data["input_size"], "linear"],
        ["Oculta 1", 64, "ReLU"],
        ["Oculta 2", 32, "ReLU"],
        ["Saída", len(data["classes"]), "softmax"],
    ])
    document.add_heading("3. Resultados", level=1)
    document.add_paragraph(
        f"Acurácia na validação: {data['validation_accuracy']:.4f}. "
        f"Perda na validação: {data['validation_loss']:.4f}."
    )
    document.add_picture(str(history_path), width=Inches(6.2))
    document.add_picture(str(confusion_path), width=Inches(6.2))
    document.add_heading("4. Pesos (Wij) e bias (bi)", level=1)
    document.add_paragraph(
        "Os valores completos dos pesos e bias aprendidos estão no arquivo "
        "weights.txt gerado junto deste relatório. A tabela abaixo resume as "
        "dimensões de cada conjunto de parâmetros."
    )
    add_table(document, ["Camada", "Dimensão dos pesos", "Dimensão do bias"], data["weight_shapes"])
    document.add_heading("5. Predições dos dados de teste", level=1)
    add_table(document, ["Registro", "Classe prevista", "Confiança"], data["predictions"])
    document.add_heading("6. Conclusão", level=1)
    document.add_paragraph(
        "O programa implementa o fluxo completo solicitado: leitura dos dados, "
        "preparação, treinamento de uma rede neural profunda, avaliação, geração "
        "das classes dos testes e registro dos parâmetros aprendidos. As predições "
        "devem ser interpretadas como predisposição estimada pelo modelo, não como "
        "diagnóstico médico."
    )
    document.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("doc/Hipertensão26.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("resultados"))
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    set_seed()
    args.output.mkdir(parents=True, exist_ok=True)

    train, test = load_data(args.data)
    labels = sorted(train[TARGET].unique())
    label_to_id = {label: index for index, label in enumerate(labels)}
    x_train, x_valid, y_train, y_valid = train_test_split(
        train[FEATURES], train[TARGET].map(label_to_id),
        test_size=0.2, random_state=SEED, stratify=train[TARGET],
    )
    preprocessor = build_preprocessor()
    x_train_encoded = preprocessor.fit_transform(x_train).astype("float32")
    x_valid_encoded = preprocessor.transform(x_valid).astype("float32")
    x_test_encoded = preprocessor.transform(test[FEATURES]).astype("float32")
    model = build_model(x_train_encoded.shape[1], len(labels))
    history = model.fit(
        x_train_encoded, y_train.to_numpy(), validation_data=(x_valid_encoded, y_valid.to_numpy()),
        epochs=args.epochs, batch_size=args.batch_size, verbose=0,
        callbacks=[keras.callbacks.EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True)],
    )
    validation_loss, validation_accuracy = model.evaluate(x_valid_encoded, y_valid.to_numpy(), verbose=0)
    probabilities = model.predict(x_test_encoded, verbose=0)
    predicted_ids = probabilities.argmax(axis=1)
    predictions = pd.DataFrame({
        "registro": np.arange(1, len(test) + 1),
        "classe_prevista": [labels[index] for index in predicted_ids],
        "confianca": probabilities.max(axis=1),
    })
    predictions.to_csv(args.output / "predicoes.csv", index=False)
    model.save(args.output / "modelo.keras")
    with (args.output / "weights.txt").open("w", encoding="utf-8") as file:
        for layer in model.layers:
            weights = layer.get_weights()
            if weights:
                file.write(f"[{layer.name}]\n")
                file.write(f"weights shape: {weights[0].shape}\n{weights[0]}\n")
                file.write(f"bias shape: {weights[1].shape}\n{weights[1]}\n\n")

    plt.figure(figsize=(8, 4))
    plt.plot(history.history["loss"], label="treino")
    plt.plot(history.history["val_loss"], label="validacao")
    plt.xlabel("Epoca"); plt.ylabel("Perda"); plt.legend(); plt.tight_layout()
    history_path = args.output / "historico.png"
    plt.savefig(history_path, dpi=150); plt.close()
    valid_pred = model.predict(x_valid_encoded, verbose=0).argmax(axis=1)
    matrix = confusion_matrix(y_valid, valid_pred, labels=range(len(labels)))
    plt.figure(figsize=(7, 6)); plt.imshow(matrix, cmap="Blues"); plt.colorbar()
    plt.xticks(range(len(labels)), labels); plt.yticks(range(len(labels)), labels)
    plt.xlabel("Predita"); plt.ylabel("Real"); plt.title("Matriz de confusao")
    for row in range(len(labels)):
        for column in range(len(labels)):
            plt.text(column, row, matrix[row, column], ha="center", va="center")
    plt.tight_layout(); confusion_path = args.output / "matriz_confusao.png"
    plt.savefig(confusion_path, dpi=150); plt.close()
    report = classification_report(y_valid, valid_pred, target_names=labels, output_dict=True, zero_division=0)
    metrics = {
        "train_rows": len(train), "test_rows": len(test), "classes": labels,
        "input_size": int(x_train_encoded.shape[1]), "epochs": len(history.history["loss"]),
        "batch_size": args.batch_size, "validation_loss": float(validation_loss),
        "validation_accuracy": float(validation_accuracy), "classification_report": report,
        "weight_shapes": [[layer.name, str(layer.get_weights()[0].shape), str(layer.get_weights()[1].shape)]
                          for layer in model.layers if layer.get_weights()],
        "predictions": [[int(row.registro), row.classe_prevista, f"{row.confianca:.4f}"]
                        for row in predictions.itertuples()],
    }
    (args.output / "metricas.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(args.output / "relatorio.docx", metrics, confusion_path, history_path)
    print(json.dumps({"validation_accuracy": metrics["validation_accuracy"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()