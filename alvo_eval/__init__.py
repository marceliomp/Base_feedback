"""Public package interface for the Alvo BR evaluation toolkit."""

from .evaluator import dump_to_file, generate_evaluations, process_file

__all__ = [
    "dump_to_file",
    "generate_evaluations",
    "process_file",
]
