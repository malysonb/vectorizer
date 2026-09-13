#!/usr/bin/env python3
"""
Script de processamento de arquivos para otimização vetorial.

Funções principais:
- Leitura de arquivos do diretório de entrada.
- Processamento do texto para otimização vetorial.
- Salvação de documentação em arquivos Markdown (.md) no diretório `docs`.

A API OpenAI-compatible (llama-server) é integrada via chaves de API.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Importações do módulo pymupdf para leitura de PDFs
try:
    import fitz  # type: ignore
except ImportError:
    print("Erro: pymupdf não disponível. Instale com: pip install pymupdf")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# === Configurações ===
INPUT_DIR = Path("input_files")
DOCS_DIR = Path("docs")
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# === Argumentos ===
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
args = parser.parse_args()

INPUT_DIR = args.input_dir
DOCS_DIR = args.output_dir

PROMPT = f"""
Converta o texto abaixo em Markdown otimizado para busca semântica e banco vetorial.

Objetivo:
Criar um documento adequado para RAG, facilitando que buscas encontrem
trechos relevantes mesmo quando a consulta usar palavras diferentes das
presentes no texto original.

Regras:
- Preserve todas as informações técnicas e fatos importantes.
- Não invente, interprete ou complete informações ausentes.
- Remova apenas conteúdo sem valor semântico, como cabeçalhos repetitivos,
  números de página, rodapés, índices, menus, quebras de linha artificiais
  e elementos de navegação.
- Organize o conteúdo em seções hierárquicas usando Markdown.
- Dê títulos descritivos às seções.
- Separe assuntos diferentes em seções independentes.
- Mantenha termos técnicos, nomes de classes, métodos, tabelas, campos,
  endpoints, códigos, mensagens de erro e identificadores exatamente como
  aparecem no texto.
- Preserve exemplos e relações de causa e efeito.
- Transforme listas e tabelas mal formatadas em Markdown quando isso melhorar
  a compreensão.
- Evite introduções, conclusões ou comentários sobre o próprio processamento.
- Não resuma excessivamente o conteúdo.
- Não repita informações apenas para aumentar a quantidade de texto.
- O resultado deve ser somente Markdown válido.

Prioridade:
1. Fidelidade ao conteúdo original.
2. Clareza e organização semântica.
3. Facilidade de recuperação por embeddings.
4. Remoção de ruído.

"""

# === Funções ===

def connect_to_llama_server(host: str = "127.0.0.1", port: int = 9000) -> bool:
    """Conecta ao server llama-server (OpenAI-compatible) na porta especificada.

    O server espera requisições HTTP POST para a rota /v1/chat/completions
    (ou /v1/completions) com o cabeçalho Content-Type: application/json.

    Arquivo de conexão:
        POST /v1/chat/completions
        {
            "model": "llama-3.1",
            "messages": [{"role": "user", "content": "..."}],
            "temperature": 0.0,
            "max_tokens": 4096
        }
    """
    import urllib.request
    import json

    url = f"http://{host}:{port}/v1/chat/completions"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({
                "model": "llama-3.1",
                "messages": [{"role": "user", "content": "test"}],
                "temperature": 0.0,
                "max_tokens": 4096
            }).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        log.info("Conexão com llama-server OK: %s", result.get("choices", [{}])[0].get("message", {}).get("content", "")[:100])
        return True
    except Exception as e:
        log.error("Erro ao conectar ao llama-server: %s", e)
        return False


def process_document_via_api(filepath: Path, api_key: str = "") -> str:
    """Processa um documento PDF ou texto através da API llama-server e retorna o conteúdo
    otimizado em Markdown para o banco de dados vetorial.

    O fluxo:
        1. Leitura do arquivo (texto ou PDF)
        2. Normalização do texto (remoção de suíno, hifenado, compactação)
        3. Envio ao llama-server via POST /v1/chat/completions com o texto como prompt
        4. Retorno do conteúdo otimizado formatado como Markdown
    """
    # Tentar leitura de texto primeiro, depois PDF
    text = read_text(filepath)
    if not text:
        text = read_pdf(filepath)
    if not text:
        return ""
    processed = process_text(text)

    # Chamar a API para otimização vetorial
    if connect_to_llama_server():
        import urllib.request
        import json
        prompt = f"{PROMPT}Texto original:\n\n{processed}"
        url = f"http://{os.environ.get('LLAMA_HOST', '127.0.0.1')}:{os.environ.get('LLAMA_PORT', '9000')}/v1/chat/completions"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps({
                    "model": "llama-3.1",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 4096
                }).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=250) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            log.info("API llama-server chamada para processamento do documento: %s", filepath.name)
            return f"# Documento: {filepath.name}\n\n{content}"
        except Exception as e:
            log.error("Erro ao processar documento via API: %s", e)
            return f"# Documento: {filepath.name}\n\n{processed}"
    else:
        log.warning("API não disponível, processando manualmente.")
        return f"# Documento: {filepath.name}\n\n{processed}"


def ensure_dirs():
    """Cria diretórios necessários."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Diretórios garantidos: %s, %s", INPUT_DIR, DOCS_DIR)


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
        log.error("Erro ao ler %s: %s", filepath, e)
        return ""

def read_text(filepath: Path) -> str:
    """Leitura de um arquivo de texto."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        log.error("Erro ao ler %s: %s", filepath, e)
        return ""


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


def save_md(filepath: Path, content: str) -> bool:
    """Salva conteúdo em arquivo Markdown."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        log.info("Salvo: %s", filepath)
        return True
    except Exception as e:
        log.error("Erro ao salvar %s: %s", filepath, e)
        return False


def process_file(filepath: Path) -> str:
    """Processa um arquivo individual: lê, otimiza e salva."""
    text = read_text(filepath)
    if not text:
        text = read_pdf(filepath)
    if not text:
        return ""
    processed = process_text(text)
    # Salvar como arquivo Markdown no diretório docs
    md_path = DOCS_DIR / f"{filepath.name}.md"
    return save_md(md_path, processed)


def main():
    """Principal função do script."""
    ensure_dirs()

    if not API_KEY:
        log.warning("OPENAI_API_KEY não definido. Execução em modo teste.")

    # Listar arquivos no diretório de entrada
    if INPUT_DIR.exists():
        files = list(INPUT_DIR.glob("*"))
        log.info("Arquivos encontrados em %s:", INPUT_DIR)
        for f in files:
            log.info("  - %s", f.name)

        # Processar cada arquivo
        for filepath in files:
            if filepath.is_file():
                result = process_document_via_api(filepath, API_KEY)
                if result:
                    log.info("Processado: %s", result)
                    # Salvar o conteúdo otimizado em arquivo Markdown no diretório docs
                    md_path = DOCS_DIR / f"{filepath.name}.md"
                    save_md(md_path, result)
                    log.info("Salvo: %s", md_path)
    else:
        log.error("Diretório de entrada %s não encontrado.", INPUT_DIR)
        sys.exit(1)


if __name__ == "__main__":
    main()
