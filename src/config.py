"""
Configurações da aplicação e conexão com o modelo de linguagem (LLM).
Configurado para o Gemma 4 rodando no llama-server local com respostas concisas.
"""

import os

# Configurações do Llama-Server (Gemma 4 Local)
LLAMA_SERVER_HOST = os.getenv("LLAMA_SERVER_HOST", "http://localhost:8080")
LLAMA_CHAT_ENDPOINT = f"{LLAMA_SERVER_HOST}/v1/chat/completions"
LLAMA_MODELS_ENDPOINT = f"{LLAMA_SERVER_HOST}/v1/models"

# Modelo padrão carregado no llama-server
DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL", "/models/gemma-4-12b-it-UD-Q4_K_XL.gguf")

# Parâmetros de inferência focados em respostas curtas e dinâmicas
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "10240"))
TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT", "180"))
