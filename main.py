#!/usr/bin/env python3
"""Principal função do script: processa arquivos de entrada e gera documentação Markdown."""

import sys
import logging
from pathlib import Path

from vectorizer.config import INPUT_DIR, DOCS_DIR, API_KEY
from vectorizer.io import read_file
from vectorizer.text import process_text
from vectorizer.api import process_document_via_api
from vectorizer.output import save_md


def ensure_dirs():
    """Cria diretórios necessários."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Diretórios garantidos: %s, %s", INPUT_DIR, DOCS_DIR)


def main():
    """Principal função do script."""
    ensure_dirs()

    if not API_KEY:
        logging.warning("OPENAI_API_KEY não definido. Execução em modo teste.")

    # Listar arquivos no diretório de entrada
    if INPUT_DIR.exists():
        files = list(INPUT_DIR.glob("*"))
        logging.info("Arquivos encontrados em %s:", INPUT_DIR)
        for f in files:
            logging.info("  - %s", f.name)

        # Processar cada arquivo
        for filepath in files:
            if filepath.is_file():
                result = process_document_via_api(filepath, API_KEY)
                if result:
                    logging.info("Processado: %s", result)
                    # Salvar o conteúdo otimizado em arquivo Markdown no diretório docs
                    md_path = DOCS_DIR / f"{filepath.name}.md"
                    save_md(md_path, result)
                    logging.info("Salvo: %s", md_path)
    else:
        logging.error("Diretório de entrada %s não encontrado.", INPUT_DIR)
        sys.exit(1)


if __name__ == "__main__":
    main()
