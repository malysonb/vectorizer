"""Processamento do texto para otimização vetorial."""

from vectorizer.config import INPUT_DIR, DOCS_DIR


def process_text(text: str) -> str:
    """Processamento do texto para otimização vetorial.

    Implementação básica: normalização de caracteres e remoção de
    espaços em branco excessivos.
    """
    if not text:
        return ""

    # Normalização de caracteres
    text = text.replace("\u200b", "")  # suíno
    text = text.replace("\u00ad", "")  # hifenado

    # Remoção de espaços em branco excessivos
    text = " ".join(text.split())
    return text
