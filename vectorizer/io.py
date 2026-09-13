"""Leitura de arquivos (texto e PDF)."""

from pathlib import Path

import fitz  # type: ignore

from vectorizer.config import INPUT_DIR, DOCS_DIR


def read_text(filepath: Path) -> str:
    """Leitura de um arquivo de texto."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return ""


def read_pdf(filepath: Path) -> str:
    """Leitura de um arquivo PDF usando pymupdf."""
    try:
        doc = fitz.open(str(filepath))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return ""


def read_file(filepath: Path) -> str:
    """Leitura de um arquivo: texto primeiro, depois PDF."""
    text = read_text(filepath)
    if not text:
        text = read_pdf(filepath)
    return text
