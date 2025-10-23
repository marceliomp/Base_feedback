"""Core evaluation logic for the Alvo BR 360° review generator."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .constants import (
    CATEGORY_WEIGHTS,
    PERFORMANCE_THRESHOLDS,
    POTENTIAL_THRESHOLDS,
    SUBCRITERIA_BY_CATEGORY,
)


def _safe_mean(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return mean(values)


@dataclass
class EvaluationRecord:
    """Wrapper responsible for computing scores and alerts for one collaborator."""

    payload: Dict[str, Any]
    weights: Dict[str, float] = field(default_factory=lambda: deepcopy(CATEGORY_WEIGHTS))

    def compute(self) -> Dict[str, Any]:
        """Return a dict ready to be serialised with computed fields filled in."""

        record = deepcopy(self.payload)
        record.setdefault("pesos", deepcopy(self.weights))

        category_results = self._category_results()
        record["score_final"] = round(category_results.score_final, 2)
        record.setdefault("classificacao", {})

        performance = self._classify_performance()
        potential = self._classify_potential()

        record["classificacao"].update(
            {
                "performance": performance,
                "potencial": potential,
                "nove_box": f"{self._nine_box_perf(performance)} / {self._nine_box_pot(potential)}",
            }
        )

        alerts = set(record.get("alertas", []))
        alerts.update(category_results.alerts)
        record["alertas"] = sorted(alerts)
        return record

    # ---------------------------------------------------------------------
    # Private helpers

    def _category_results(self) -> "CategoryResults":
        category_scores: Dict[str, float] = {}
        missing_data = False

        for category, weight in self.weights.items():
            sub_scores, sub_missing = self._extract_subscores(category)
            if sub_scores:
                avg = _safe_mean(sub_scores)
                if avg is not None:
                    category_scores[category] = avg
            if sub_missing:
                missing_data = True

        score_final = 0.0
        for category, avg in category_scores.items():
            weight = self.weights.get(category, 0.0)
            score_final += avg * weight

        alerts = []
        if missing_data:
            alerts.append("dados_insuficientes")

        return CategoryResults(score_final=score_final, alerts=alerts)

    def _extract_subscores(self, category: str) -> Tuple[List[float], bool]:
        notas = self.payload.get("notas", {}).get(category, {})
        missing_data = False
        sub_scores: List[float] = []

        for sub in SUBCRITERIA_BY_CATEGORY.get(category, ()):  # type: ignore[arg-type]
            sub_entry = notas.get(sub)
            nota = None
            if isinstance(sub_entry, dict):
                nota = sub_entry.get("nota")
            elif isinstance(sub_entry, (int, float)):
                nota = sub_entry
            if isinstance(nota, (int, float)):
                sub_scores.append(float(nota))
            else:
                missing_data = True

        return sub_scores, missing_data

    def _classify_performance(self) -> str:
        notas_entrega = self.payload.get("notas", {}).get("entrega_resultados", {})
        atingimento = None
        atingimento_entry = notas_entrega.get("atingimento_metas")
        if isinstance(atingimento_entry, dict):
            atingimento = atingimento_entry.get("nota")
        elif isinstance(atingimento_entry, (int, float)):
            atingimento = atingimento_entry

        if not isinstance(atingimento, (int, float)):
            return "dados_insuficientes"

        if atingimento >= PERFORMANCE_THRESHOLDS["Alta"]:
            return "Alta"
        if atingimento >= PERFORMANCE_THRESHOLDS["Ok"]:
            return "Ok"
        return "Baixa"

    def _classify_potential(self) -> str:
        relevant_categories = (
            "valores_cultura",
            "habilidades_comportamentais",
            "evolucao_aprendizagem",
        )
        scores = []
        for category in relevant_categories:
            sub_scores, _ = self._extract_subscores(category)
            avg = _safe_mean(sub_scores)
            if avg is not None:
                scores.append(avg)
        if not scores:
            return "dados_insuficientes"

        potential_score = mean(scores)
        if potential_score >= POTENTIAL_THRESHOLDS["Alto"]:
            return "Alto"
        if potential_score >= POTENTIAL_THRESHOLDS["Medio"]:
            return "Medio"
        return "Baixo"

    @staticmethod
    def _nine_box_perf(performance: str) -> str:
        mapping = {
            "Alta": "Alta Perf",
            "Ok": "Ok Perf",
            "Baixa": "Baixa Perf",
        }
        return mapping.get(performance, "Perf Indefinida")

    @staticmethod
    def _nine_box_pot(potential: str) -> str:
        mapping = {
            "Alto": "Alto Potencial",
            "Medio": "Médio Potencial",
            "Baixo": "Baixo Potencial",
        }
        return mapping.get(potential, "Potencial Indefinido")


@dataclass
class CategoryResults:
    score_final: float
    alerts: List[str] = field(default_factory=list)


def generate_evaluations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate the final evaluation payload from an input dictionary.

    Parameters
    ----------
    data:
        Dictionary expected to contain an ``"avaliacoes"`` key with the raw
        evaluations.
    """

    raw_evaluations = data.get("avaliacoes", [])
    results: List[Dict[str, Any]] = []
    for payload in raw_evaluations:
        evaluator = EvaluationRecord(payload)
        results.append(evaluator.compute())
    return results


def process_file(input_path: str) -> List[Dict[str, Any]]:
    """Load JSON from ``input_path`` and return computed evaluations."""

    with open(input_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return generate_evaluations(data)


def dump_to_file(
    evaluations: List[Dict[str, Any]], output_path: str | Path
) -> Path:
    """Write the evaluations list to ``output_path`` as JSON and return the path."""

    path = Path(output_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as fh:
        json.dump({"avaliacoes": evaluations}, fh, ensure_ascii=False, indent=2)

    return path
