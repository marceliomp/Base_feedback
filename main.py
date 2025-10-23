"""Command line entry-point for generating Alvo BR performance reviews."""

from __future__ import annotations

import argparse
import json
import sys
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
        type=str,
        help=(
            "Caminho do arquivo JSON com as avaliações brutas ou '-' para ler do stdin."
        ),
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
    if args.input == "-":
        data: Any = json.load(sys.stdin)
    else:
        input_path = Path(args.input)
        with input_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

    evaluations = generate_evaluations(data)

    if args.output:
        saved_path = dump_to_file(evaluations, args.output)
        print(f"Arquivo salvo em {saved_path.resolve()}")
    else:
        print(json.dumps({"avaliacoes": evaluations}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
