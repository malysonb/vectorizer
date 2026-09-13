"""Integração com a API llama-server (OpenAI-compatible)."""

import json
import os
import urllib.request

from vectorizer.config import API_KEY


PROMPT = """
Converte o texto abaixo em Markdown otimizado para busca semântica e banco vetorial.

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


def connect_to_llama_server(host: str = "127.0.0.1", port: int = 9000) -> bool:
    """Conecta ao server llama-server (OpenAI-compatible) na porta especificada.

    O server espera requisições HTTP POST para a rota /v1/chat/completions
    (ou /v1/completions) com o cabeçalho Content-Type: application/json.
    """
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
        print(f"Conexão com llama-server OK: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}")
        return True
    except Exception as e:
        print(f"Erro ao conectar ao llama-server: {e}")
        return False


def process_document_via_api(filepath, api_key: str = "") -> str:
    """Processa um documento através da API llama-server e retorna o conteúdo
    otimizado em Markdown para o banco de dados vetorial.

    O fluxo:
        1. Leitura do arquivo (texto ou PDF)
        2. Normalização do texto (remoção de suíno, hifenado, compactação)
        3. Envio ao llama-server via POST /v1/chat/completions com o texto como prompt
        4. Retorno do conteúdo otimizado formatado como Markdown
    """
    from vectorizer.io import read_file
    from vectorizer.text import process_text

    text = read_file(filepath)
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
            print(f"API llama-server chamada para processamento do documento: {filepath.name}")
            return f"# Documento: {filepath.name}\n\n{content}"
        except Exception as e:
            print(f"Erro ao processar documento via API: {e}")
            return f"# Documento: {filepath.name}\n\n{processed}"
    else:
        print("API não disponível, processando manualmente.")
        return f"# Documento: {filepath.name}\n\n{processed}"
