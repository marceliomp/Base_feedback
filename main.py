"""Command line entry-point for generating Alvo BR performance reviews."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Type

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
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Inicia um servidor HTTP simples para visualizar o resultado.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para o modo --serve (padrão: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para o modo --serve (padrão: 8000).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.input.open("r", encoding="utf-8") as fh:
        data: Any = json.load(fh)

    evaluations = generate_evaluations(data)

    payload = json.dumps({"avaliacoes": evaluations}, ensure_ascii=False, indent=2)

    if args.output:
        dump_to_file(evaluations, str(args.output))
    if args.serve:
        _serve_payload(payload, host=args.host, port=args.port)
    if not args.output and not args.serve:
        print(payload)


def _serve_payload(payload: str, *, host: str, port: int) -> None:
    handler_class: Type[BaseHTTPRequestHandler] = _build_handler(payload)
    server = HTTPServer((host, port), handler_class)
    try:
        print(f"Servidor disponível em http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server.server_close()


def _build_handler(payload: str) -> Type[BaseHTTPRequestHandler]:
    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - método exigido pelo protocolo HTTP
            if self.path not in ("/", "/avaliacoes"):
                self.send_error(404, "Not Found")
                return

            body = payload.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:  # noqa: A003 - assinatura fixa
            return

    return _Handler


if __name__ == "__main__":
    main()
