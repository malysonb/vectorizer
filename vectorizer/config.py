"""Configurações de configuração do vectorizer."""

from pathlib import Path

INPUT_DIR = Path("input_files")
DOCS_DIR = Path("docs")
API_KEY = __import__("os").environ.get("OPENAI_API_KEY", "")
