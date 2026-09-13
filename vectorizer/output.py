"""Salva conteúdo em arquivo Markdown."""

from pathlib import Path

from vectorizer.config import DOCS_DIR


def save_md(filepath: Path, content: str) -> bool:
    """Salva conteúdo em arquivo Markdown."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Salvo: {filepath}")
        return True
    except Exception as e:
        print(f"Erro ao salvar {filepath}: {e}")
        return False
