# Vectorizer

Script Python que processa arquivos de entrada, otimiza o texto para busca semântica e salva a documentação em arquivos Markdown (.md) no diretório `docs`.

## Objetivo

Criar um script Python que interage com uma API compatível com OpenAI (llama-server), lê arquivos de um diretório, processa o texto para otimização vetorial e salva a documentação em arquivos Markdown (.md) no diretório `docs`.

## Funcionalidades

- Leitura de arquivos de texto (.txt, .java) e PDF.
- Normalização de caracteres (suíno, hifenado) e remoção de espaços em branco excessivos.
- Processamento do texto para otimização vetorial via prompt personalizado.
- Chamada à API llama-server (OpenAI-compatible) para interpretação e otimização.
- Salvação de documentação em arquivos Markdown no diretório `docs`.
- Suporte a argumentos de diretório de entrada e saída via `--input-dir` e `--output-dir`.

## Requisitos

- Python 3
- `pymupdf` (para leitura de PDF)
- `llama-server` (OpenAI-compatible) na porta 9000
- Chave de API OpenAI (opcional, no ambiente `OPENAI_API_KEY`)

## Instalação

```bash
pip install pymupdf
```

## Uso

```bash
python vectorizer.py
```

Opções:

- `--input-dir <diretório>` — Diretório de entrada de arquivos (padrão: `input_files`)
- `--output-dir <diretório>` — Diretório de saída para arquivos Markdown (padrão: `docs`)

## Configuração

- **API llama-server**: local em `127.0.0.1:9000` (opcional, via `LLAMA_HOST` e `LLAMA_PORT` ambientes)
- **Chave de API**: definida no ambiente `OPENAI_API_KEY`

## Formatos de arquivo suportados

- `.txt` — arquivos de texto
- `.java` — arquivos de código
- `.pdf` — arquivos PDF (via pymupdf)

## Processamento

O script processa cada arquivo no diretório de entrada:

1. Leitura do arquivo (texto primeiro, depois PDF).
2. Normalização do texto.
3. Envio ao llama-server via POST `/v1/chat/completions` com o texto como prompt.
4. Retorno do conteúdo otimizado formatado como Markdown.
5. Salvação em arquivo Markdown no diretório `docs`.

## Saída

Arquivos Markdown gerados no diretório `docs` com o nome do arquivo original, suffixo `.md`.

## Teste

```bash
python vectorizer.py
```

Verifique a saída nos arquivos do diretório `docs`.
