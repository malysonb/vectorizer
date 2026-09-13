"""Argumentos de entrada e saída."""

import argparse
from pathlib import Path

from vectorizer.config import INPUT_DIR, DOCS_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Processar arquivos de entrada e gerar documentação Markdown otimizada para vetorial."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=INPUT_DIR,
        help=f"Diretório de entrada de arquivos (padrão: {INPUT_DIR})"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DOCS_DIR,
        help=f"Diretório de saída para arquivos Markdown (padrão: {DOCS_DIR})"
    )
    return parser


def parse_args() -> argparse.Namespace:
    return build_parser().parse_args()
