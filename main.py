"""Command line entry-point for generating Alvo BR performance reviews."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional, Tuple

from alvo_eval import dump_to_file, generate_evaluations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gera avaliações 360° orientadas a valores a partir de um arquivo JSON ou "
            "oferece um endpoint HTTP simples para cálculo sob demanda."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
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
        help="Executa um servidor HTTP simples que processa requisições POST /avaliacoes.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host de binding para o modo servidor (padrão: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para o modo servidor (padrão: 8000).",
    )
    return parser.parse_args()


class _EvaluationRequestHandler(BaseHTTPRequestHandler):
    server_version = "alvo-eval/1.0"

    def _send_response(
        self,
        status: int,
        payload: Any,
        content_type: str = "application/json; charset=utf-8",
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Tuple[Optional[Any], Optional[str]]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None, "Content-Length inválido"

        body = self.rfile.read(content_length)
        if not body:
            return None, "Corpo da requisição vazio"

        try:
            return json.loads(body.decode("utf-8")), None
        except json.JSONDecodeError as exc:
            return None, f"JSON inválido: {exc}"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path in {"/", "/health", "/healthz"}:
            self._send_response(
                200,
                {
                    "status": "ok",
                    "message": "Alvo BR avaliação 360° ativo",
                },
            )
            return
        self._send_response(404, {"detail": "Rota não encontrada"})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/avaliacoes":
            self._send_response(404, {"detail": "Rota não encontrada"})
            return

        payload, error = self._read_json()
        if error is not None:
            self._send_response(400, {"detail": error})
            return

        evaluations = generate_evaluations(payload or {})
        self._send_response(200, {"avaliacoes": evaluations})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - signature fixed
        # Reduce noise in stdout/stderr by silencing default logging.
        return


def run_server(host: str, port: int) -> None:
    httpd = ThreadingHTTPServer((host, port), _EvaluationRequestHandler)
    print(f"Servidor iniciado em http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        httpd.server_close()


def main() -> None:
    args = parse_args()

    if args.serve:
        run_server(args.host, args.port)
        return

    if args.input is None:
        raise SystemExit(
            "Informe o caminho de entrada ou utilize --serve para iniciar o servidor."
        )

    with args.input.open("r", encoding="utf-8") as fh:
        data: Any = json.load(fh)

    evaluations = generate_evaluations(data)

    if args.output:
        dump_to_file(evaluations, str(args.output))
    else:
        print(json.dumps({"avaliacoes": evaluations}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
