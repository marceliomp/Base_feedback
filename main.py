"""Command line entry-point for generating Alvo BR performance reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from alvo_eval import dump_to_file, generate_evaluations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gera avaliações 360° orientadas a valores a partir de um arquivo JSON."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Caminho do arquivo JSON com as avaliações brutas.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Caminho do arquivo de saída. Se omitido, imprime no stdout.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.input.open("r", encoding="utf-8") as fh:
        data: Any = json.load(fh)

    evaluations = generate_evaluations(data)

    if args.output:
        dump_to_file(evaluations, str(args.output))
    else:
        print(json.dumps({"avaliacoes": evaluations}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
