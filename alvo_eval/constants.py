"""Constant definitions for the Alvo BR evaluation calculator."""

from __future__ import annotations

CATEGORY_WEIGHTS = {
    "valores_cultura": 0.20,
    "entrega_resultados": 0.25,
    "habilidades_tecnicas": 0.15,
    "habilidades_comportamentais": 0.15,
    "pontualidade_confiabilidade": 0.10,
    "ownership_comercial": 0.10,
    "evolucao_aprendizagem": 0.05,
}

SUBCRITERIA_BY_CATEGORY = {
    "valores_cultura": (
        "postura_de_dono",
        "fome_de_crescer",
        "disciplina_para_entregar",
        "transparencia_de_dados",
    ),
    "entrega_resultados": (
        "atingimento_metas",
        "qualidade_entregas",
    ),
    "habilidades_tecnicas": (
        "dominio_ferramentas",
        "conhecimento_produto",
    ),
    "habilidades_comportamentais": (
        "comunicacao",
        "colaboracao",
    ),
    "pontualidade_confiabilidade": (
        "pontualidade",
        "assiduidade",
    ),
    "ownership_comercial": (
        "prospeccao_followup",
        "organizacao_crm",
    ),
    "evolucao_aprendizagem": (
        "melhoria_continua",
    ),
}

PERFORMANCE_THRESHOLDS = {
    "Alta": 8.0,
    "Ok": 6.0,
}

POTENTIAL_THRESHOLDS = {
    "Alto": 8.0,
    "Medio": 6.0,
}
