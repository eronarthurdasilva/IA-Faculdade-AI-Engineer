"""Sistemas fuzzy Mamdani para os quatro problemas do trabalho prático."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

Triangle = tuple[float, float, float]
FuzzySet = Mapping[str, Triangle]
Antecedent = tuple[str, str]
Rule = tuple[tuple[Antecedent, ...], str]
RESULTS_PDF = Path(__file__).with_name("resultados.pdf")


@dataclass(frozen=True)
class FuzzyInference:
    """Resultado defuzzificado e dados usados para desenhar o gráfico Mamdani."""

    value: float
    output_domain: tuple[float, float]
    output_sets: FuzzySet
    activations: Mapping[str, float]
    output_values: tuple[float, ...]
    aggregated_membership: tuple[float, ...]


def triangular_membership(value: float, points: Triangle) -> float:
    """Calcula a pertinência triangular, incluindo ombros esquerdo e direito."""
    left, peak, right = points
    if not left <= peak <= right:
        raise ValueError("Os pontos do conjunto devem obedecer a left <= peak <= right.")
    if value < left or value > right:
        return 0.0
    if value == peak:
        return 1.0
    if value < peak:
        return 1.0 if left == peak else (value - left) / (peak - left)
    return 1.0 if peak == right else (right - value) / (right - peak)


def validate_inputs(
    inputs: Mapping[str, float], domains: Mapping[str, tuple[float, float]]
) -> None:
    """Recusa valores fora dos universos definidos para cada variável."""
    for variable, value in inputs.items():
        if variable not in domains:
            raise ValueError(f"Variável de entrada desconhecida: {variable}.")
        lower, upper = domains[variable]
        if not lower <= value <= upper:
            raise ValueError(
                f"{variable} deve estar no intervalo [{lower:g}, {upper:g}]; "
                f"recebido: {value:g}."
            )


def infer_mamdani(
    inputs: Mapping[str, float],
    domains: Mapping[str, tuple[float, float]],
    input_sets: Mapping[str, FuzzySet],
    rules: Sequence[Rule],
    output_sets: FuzzySet,
    output_domain: tuple[float, float],
    step: float,
) -> FuzzyInference:
    """Aplica AND=min, agregação=max, implicação min e centroide discreto."""
    validate_inputs(inputs, domains)
    if step <= 0:
        raise ValueError("O passo de amostragem deve ser positivo.")

    # Fuzzificação: calcula uma vez o grau de cada termo para cada entrada.
    memberships = {
        variable: {
            label: triangular_membership(inputs[variable], triangle)
            for label, triangle in terms.items()
        }
        for variable, terms in input_sets.items()
    }

    # Cada regra combina seus antecedentes com o operador AND (mínimo).
    activations = {label: 0.0 for label in output_sets}
    for antecedents, consequent in rules:
        strength = min(
            memberships[variable][term] for variable, term in antecedents
        )
        activations[consequent] = max(activations[consequent], strength)

    # Amostra a saída, corta cada consequente pela força da regra e agrega por máximo.
    lower, upper = output_domain
    sample_count = int(round((upper - lower) / step))
    output_values = [lower + index * step for index in range(sample_count + 1)]
    aggregated = []
    for value in output_values:
        degree = max(
            min(activations[label], triangular_membership(value, triangle))
            for label, triangle in output_sets.items()
        )
        aggregated.append(degree)

    area = sum(aggregated)
    if area == 0:
        raise ValueError("Nenhuma regra foi ativada para os valores informados.")

    # Com amostras igualmente espaçadas, o passo cancela na razão do centroide.
    centroid = sum(
        value * degree for value, degree in zip(output_values, aggregated)
    ) / area
    return FuzzyInference(
        value=centroid,
        output_domain=output_domain,
        output_sets=output_sets,
        activations=activations,
        output_values=tuple(output_values),
        aggregated_membership=tuple(aggregated),
    )


def _evaluate_violet_vitality(water_ml: float, sun_minutes: float) -> FuzzyInference:
    """Calcula a vitalidade da violeta a partir da água e do tempo de sol."""
    domains = {"agua": (0.0, 65.0), "sol": (0.0, 95.0)}
    input_sets = {
        "agua": {
            "pequena": (0.0, 0.0, 25.0),
            "media": (20.0, 30.0, 45.0),
            "grande": (35.0, 65.0, 65.0),
        },
        "sol": {
            "pequeno": (0.0, 0.0, 30.0),
            "medio": (25.0, 50.0, 65.0),
            "grande": (60.0, 95.0, 95.0),
        },
    }
    output_sets = {
        "ruim": (0.0, 0.0, 0.2),
        "media": (0.1, 0.5, 0.9),
        "boa": (0.8, 1.0, 1.0),
    }

    # A tabela cruza as três categorias de sol com as três de água.
    table = {
        "pequeno": ("media", "boa", "ruim"),
        "medio": ("media", "boa", "ruim"),
        "grande": ("ruim", "media", "ruim"),
    }
    rules: list[Rule] = []
    water_terms = ("pequena", "media", "grande")
    for sun_term, consequents in table.items():
        for water_term, consequent in zip(water_terms, consequents):
            rules.append(((("sol", sun_term), ("agua", water_term)), consequent))

    return infer_mamdani(
        {"agua": water_ml, "sol": sun_minutes},
        domains,
        input_sets,
        rules,
        output_sets,
        (0.0, 1.0),
        0.001,
    )


def _evaluate_credit_risk(
    market_score: float, driver_score: float, engagement: float
) -> float:
    """Calcula o grau de risco de crédito usando os ratings do enunciado."""
    score_domain = (0.0, 1000.0)
    score_sets = {
        "rating_1": (800.0, 900.0, 1000.0),
        "rating_2": (700.0, 800.0, 900.0),
        "rating_3": (600.0, 700.0, 800.0),
        "rating_4": (400.0, 500.0, 600.0),
        "rating_5": (200.0, 300.0, 400.0),
        "rating_6": (0.0, 200.0, 300.0),
    }
    engagement_sets = {
        "baixo": (0.0, 0.0, 100.0),
        "medio": (0.0, 100.0, 200.0),
        "alto": (200.0, 1000.0, 5000.0),
    }
    risk_sets = {
        "risco_1": (900.0, 950.0, 1000.0),
        "risco_2": (800.0, 850.0, 900.0),
        "risco_3": (625.0, 750.0, 825.0),
        "risco_4": (375.0, 500.0, 625.0),
        "risco_5": (0.0, 250.0, 375.0),
    }

    # Expande cada grupo de ratings em regras AND para as duas entradas de score.
    rules: list[Rule] = []

    def add_rating_group(
        engagement_term: str,
        ratings: Iterable[str],
        consequent: str,
    ) -> None:
        for driver_rating in ratings:
            for market_rating in ratings:
                rules.append(
                    (
                        (
                            ("engajamento", engagement_term),
                            ("motorista", driver_rating),
                            ("mercado", market_rating),
                        ),
                        consequent,
                    )
                )

    add_rating_group("baixo", ("rating_6", "rating_5", "rating_4", "rating_3"), "risco_5")
    add_rating_group("baixo", ("rating_1", "rating_2"), "risco_4")
    add_rating_group("medio", ("rating_6", "rating_5", "rating_4"), "risco_5")
    add_rating_group("medio", ("rating_1", "rating_2", "rating_3"), "risco_3")
    add_rating_group("alto", ("rating_6",), "risco_4")
    add_rating_group("alto", ("rating_4", "rating_5"), "risco_3")
    add_rating_group("alto", ("rating_3",), "risco_2")
    add_rating_group("alto", ("rating_1", "rating_2"), "risco_1")

    input_sets = {
        "mercado": score_sets,
        "motorista": score_sets,
        "engajamento": engagement_sets,
    }
    return infer_mamdani(
        {
            "mercado": market_score,
            "motorista": driver_score,
            "engajamento": engagement,
        },
        {
            "mercado": score_domain,
            "motorista": score_domain,
            "engajamento": (0.0, 5000.0),
        },
        input_sets,
        rules,
        risk_sets,
        (0.0, 1000.0),
        1.0,
    )


def _evaluate_tip(food_quality: float, service_quality: float) -> FuzzyInference:
    """Calcula a gorjeta para as notas de comida e de serviço."""
    quality_sets = {
        "ruim": (0.0, 0.0, 5.0),
        "aceitavel": (0.0, 5.0, 10.0),
        "excelente": (5.0, 10.0, 10.0),
    }
    tip_sets = {
        "baixa": (0.0, 0.0, 12.5),
        "media": (0.0, 12.5, 25.0),
        "alta": (12.5, 25.0, 25.0),
    }
    rules: tuple[Rule, ...] = (
        # OR é o máximo das pertinências dos dois antecedentes.
        ((("comida", "ruim"),), "baixa"),
        ((("servico", "ruim"),), "baixa"),
        ((("servico", "aceitavel"),), "media"),
        ((("comida", "excelente"),), "alta"),
        ((("servico", "excelente"),), "alta"),
    )
    return infer_mamdani(
        {"comida": food_quality, "servico": service_quality},
        {"comida": (0.0, 10.0), "servico": (0.0, 10.0)},
        {"comida": quality_sets, "servico": quality_sets},
        rules,
        tip_sets,
        (0.0, 25.0),
        0.01,
    )


def _evaluate_insurance_premium(age: float, health: float) -> FuzzyInference:
    """Calcula o prêmio do seguro para idade e estado de saúde."""
    age_sets = {
        "muito_jovem": (10.0, 20.0, 30.0),
        "jovem": (20.0, 30.0, 45.0),
        "idade_media": (30.0, 45.0, 60.0),
        "maduro": (45.0, 60.0, 70.0),
        "idoso": (60.0, 70.0, 80.0),
    }
    health_sets = {
        "muito_pessimo": (0.0, 0.0, 0.25),
        "pessimo": (0.1, 0.25, 0.4),
        "medio": (0.25, 0.5, 0.75),
        "bom": (0.5, 0.75, 0.9),
        "muito_bom": (0.75, 1.0, 1.1),
    }
    premium_sets = {
        "muito_baixo": (0.0, 0.0, 20.0),
        "baixo": (0.0, 20.0, 33.0),
        "moderadamente_baixo": (20.0, 33.0, 50.0),
        "moderado": (33.0, 50.0, 67.0),
        "moderadamente_alto": (50.0, 67.0, 75.0),
        "alto": (67.0, 80.0, 90.0),
        "muito_alto": (80.0, 100.0, 100.0),
    }

    # Cada linha corresponde a uma categoria de saúde; as colunas são as idades.
    table = {
        "muito_pessimo": (
            "moderado",
            "moderadamente_alto",
            "moderadamente_alto",
            "alto",
            "muito_alto",
        ),
        "pessimo": (
            "moderadamente_baixo",
            "moderado",
            "moderadamente_alto",
            "moderadamente_alto",
            "alto",
        ),
        "medio": (
            "moderadamente_baixo",
            "moderadamente_baixo",
            "moderado",
            "moderadamente_alto",
            "moderadamente_alto",
        ),
        "bom": (
            "baixo",
            "moderadamente_baixo",
            "moderadamente_baixo",
            "moderado",
            "moderadamente_alto",
        ),
        "muito_bom": (
            "muito_baixo",
            "baixo",
            "moderadamente_baixo",
            "moderadamente_baixo",
            "moderado",
        ),
    }
    age_terms = ("muito_jovem", "jovem", "idade_media", "maduro", "idoso")
    rules: list[Rule] = []
    for health_term, consequents in table.items():
        for age_term, consequent in zip(age_terms, consequents):
            rules.append(
                ((("saude", health_term), ("idade", age_term)), consequent)
            )

    return infer_mamdani(
        {"idade": age, "saude": health},
        {"idade": (20.0, 70.0), "saude": (0.0, 1.0)},
        {"idade": age_sets, "saude": health_sets},
        rules,
        premium_sets,
        (0.0, 100.0),
        0.05,
    )


def calculate_violet_vitality(water_ml: float, sun_minutes: float) -> float:
    """Calcula a vitalidade da violeta a partir da água e do tempo de sol."""
    return _evaluate_violet_vitality(water_ml, sun_minutes).value


def calculate_credit_risk(
    market_score: float, driver_score: float, engagement: float
) -> float:
    """Calcula o grau de risco de crédito usando os ratings do enunciado."""
    return _evaluate_credit_risk(market_score, driver_score, engagement).value


def calculate_tip(food_quality: float, service_quality: float) -> float:
    """Calcula a gorjeta para as notas de comida e de serviço."""
    return _evaluate_tip(food_quality, service_quality).value


def calculate_insurance_premium(age: float, health: float) -> float:
    """Calcula o prêmio do seguro para idade e estado de saúde."""
    return _evaluate_insurance_premium(age, health).value


def generate_results_pdf(
    reports: Sequence[tuple[str, Mapping[str, float], FuzzyInference]],
    output_path: Path = RESULTS_PDF,
) -> Path:
    """Gera um PDF com uma página e um gráfico fuzzy para cada cálculo."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except ImportError as error:
        raise RuntimeError(
            "A geração do PDF requer Matplotlib. Instale com: "
            "py -m pip install -r requirements.txt"
        ) from error

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(output_path) as pdf:
        for title, inputs, inference in reports:
            figure, axis = plt.subplots(figsize=(10, 7))
            x_values = inference.output_values
            aggregated = inference.aggregated_membership
            axis.fill_between(
                x_values,
                aggregated,
                color="#78a6d1",
                alpha=0.55,
                label="Saída fuzzy agregada",
            )
            axis.plot(x_values, aggregated, color="#286090", linewidth=1.5)

            # Exibe os conjuntos de saída cortados pelas regras para mostrar
            # como a agregação e o centroide foram obtidos.
            palette = plt.get_cmap("tab10")
            for index, (label, triangle) in enumerate(inference.output_sets.items()):
                activation = inference.activations[label]
                if activation <= 0:
                    continue
                membership = [
                    min(activation, triangular_membership(value, triangle))
                    for value in x_values
                ]
                axis.plot(
                    x_values,
                    membership,
                    linestyle="--",
                    linewidth=1,
                    color=palette(index),
                    label=f"{label.replace('_', ' ').title()} (ativação {activation:.2f})",
                )

            axis.axvline(
                inference.value,
                color="#c0392b",
                linewidth=2,
                label=f"Centroide = {inference.value:.3f}",
            )
            axis.set(
                xlim=inference.output_domain,
                ylim=(0, 1.05),
                xlabel="Valor de saída",
                ylabel="Grau de pertinência",
                title="Conjunto fuzzy de saída e defuzzificação",
            )
            axis.grid(True, alpha=0.25)
            axis.legend(loc="best", fontsize="small")
            figure.suptitle(title, fontsize=15, fontweight="bold")

            input_text = "\n".join(
                f"{name}: {value:g}" for name, value in inputs.items()
            )
            figure.text(
                0.1,
                0.84,
                f"Entradas utilizadas:\n{input_text}\n\n"
                f"Resposta defuzzificada: {inference.value:.3f}",
                va="top",
                fontsize=11,
            )
            figure.subplots_adjust(top=0.66, bottom=0.12, left=0.12, right=0.95)
            pdf.savefig(figure)
            plt.close(figure)

    return output_path


def read_number(prompt: str, lower: float, upper: float) -> float:
    """Lê um número no intervalo permitido, aceitando vírgula decimal."""
    while True:
        raw_value = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw_value)
        except ValueError:
            print("Informe um número válido.")
            continue
        if lower <= value <= upper:
            return value
        print(f"O valor deve estar entre {lower:g} e {upper:g}.")


def run_interactive() -> None:
    """Calcula a saída fuzzy para entradas escolhidas pelo usuário."""
    while True:
        print(
            "\nEscolha o sistema fuzzy:"
            "\n  A - Vitalidade da violeta"
            "\n  B - Risco de crédito"
            "\n  C - Gorjeta"
            "\n  D - Prêmio do seguro"
            "\n  Q - Sair"
        )
        choice = input("Opção: ").strip().lower()
        if choice == "q":
            return

        try:
            if choice == "a":
                water = read_number("Água (0 a 65 ml): ", 0.0, 65.0)
                sun = read_number("Exposição ao sol (0 a 95 min): ", 0.0, 95.0)
                inference = _evaluate_violet_vitality(water, sun)
                result = inference.value
                print(f"Vitalidade calculada: {result:.3f} / 1")
                inputs = {"Água (ml)": water, "Sol (min)": sun}
                title = "A) Vitalidade da violeta"
            elif choice == "b":
                market = read_number("Score de mercado (0 a 1000): ", 0.0, 1000.0)
                driver = read_number("Score do motorista (0 a 1000): ", 0.0, 1000.0)
                engagement = read_number("Engajamento (0 a 5000): ", 0.0, 5000.0)
                inference = _evaluate_credit_risk(market, driver, engagement)
                result = inference.value
                print(f"Grau de risco calculado: {result:.2f} / 1000")
                inputs = {
                    "Score de mercado": market,
                    "Score do motorista": driver,
                    "Engajamento": engagement,
                }
                title = "B) Política de crédito"
            elif choice == "c":
                food = read_number("Qualidade da comida (0 a 10): ", 0.0, 10.0)
                service = read_number("Qualidade do serviço (0 a 10): ", 0.0, 10.0)
                inference = _evaluate_tip(food, service)
                result = inference.value
                print(f"Gorjeta calculada: {result:.2f} / 25")
                inputs = {"Qualidade da comida": food, "Qualidade do serviço": service}
                title = "C) Gorjeta"
            elif choice == "d":
                age = read_number("Idade (20 a 70 anos): ", 20.0, 70.0)
                health = read_number("Estado de saúde (0 a 1): ", 0.0, 1.0)
                inference = _evaluate_insurance_premium(age, health)
                result = inference.value
                print(f"Prêmio calculado: {result:.2f} / 100")
                inputs = {"Idade (anos)": age, "Estado de saúde": health}
                title = "D) Prêmio do seguro"
            else:
                print("Opção inválida. Escolha A, B, C, D ou Q.")
                continue

            output_path = generate_results_pdf(
                [(title, inputs, inference)], RESULTS_PDF
            )
            print(f"Relatório e gráfico salvos em: {output_path}")
        except ValueError as error:
            # Mantém visíveis problemas de inferência sem encerrar o menu.
            print(f"Não foi possível calcular: {error}")


def main(argv: Sequence[str] | None = None) -> None:
    """Executa os exemplos do enunciado ou abre o modo interativo."""
    parser = argparse.ArgumentParser(
        description="Calcula respostas com sistemas de inferência fuzzy Mamdani."
    )
    parser.add_argument(
        "--interativo",
        action="store_true",
        help="permite informar entradas próprias para cada sistema fuzzy",
    )
    args = parser.parse_args(argv)

    if args.interativo:
        run_interactive()
        return

    print("Trabalho prático - sistemas de inferência fuzzy Mamdani\n")

    vitality = _evaluate_violet_vitality(45.0, 50.0)
    reference_vitality = calculate_violet_vitality(40.0, 60.0)
    print(f"A) Vitalidade da violeta (45 ml, 50 min): {vitality.value:.3f} / 1")
    print(
        "   Conferência com o exemplo do enunciado (40 ml, 60 min): "
        f"{reference_vitality:.3f} / 1 (referência: 0.625)"
    )

    risk = _evaluate_credit_risk(market_score=2.0, driver_score=230.0, engagement=90.0)
    print(f"B) Risco de crédito (mercado 2, motorista 230, engajamento 90): {risk.value:.2f} / 1000")

    tip = _evaluate_tip(food_quality=6.5, service_quality=9.8)
    print(f"C) Gorjeta (comida 6.5, serviço 9.8): {tip.value:.2f} / 25")

    premium = _evaluate_insurance_premium(age=32.0, health=0.7)
    print(f"D) Prêmio do seguro (32 anos, saúde 0.7): {premium.value:.2f} / 100")

    output_path = generate_results_pdf(
        [
            (
                "A) Vitalidade da violeta",
                {"Água (ml)": 45.0, "Sol (min)": 50.0},
                vitality,
            ),
            (
                "B) Política de crédito",
                {
                    "Score de mercado": 2.0,
                    "Score do motorista": 230.0,
                    "Engajamento": 90.0,
                },
                risk,
            ),
            (
                "C) Gorjeta",
                {"Qualidade da comida": 6.5, "Qualidade do serviço": 9.8},
                tip,
            ),
            (
                "D) Prêmio do seguro",
                {"Idade (anos)": 32.0, "Estado de saúde": 0.7},
                premium,
            ),
        ],
        RESULTS_PDF,
    )
    print(f"\nRelatório e gráficos salvos em: {output_path}")


if __name__ == "__main__":
    main()
