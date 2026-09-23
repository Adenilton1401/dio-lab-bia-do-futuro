# Aplicação da Agente Lis 💳

Esta pasta contém o protótipo funcional da **Lis**, especialista consultiva em cartões de crédito e finanças pessoais (Bootcamp Bradesco / DIO).

A aplicação foi desenvolvida utilizando exclusivamente a **Biblioteca Padrão do Python**, sem dependências externas de terceiros, garantindo execução instantânea em qualquer ambiente.

---

## Estrutura dos Arquivos

```
src/
├── app.py              # Servidor e Aplicação Web Interativa (Python nativo)
├── agente.py           # Orquestrador da Lis (Prompt Caching, telemetria e guardrails)
├── config.py           # Configurações do LLM (Gemma 4 via llama-server no Docker)
├── data_loader.py      # Processador de dados (médias mensais e métricas financeiras)
├── rag.py              # SimpleRAG: Motor de recuperação semântica nativo (TF-IDF)
└── requirements.txt    # Arquivo de dependências (informativo - sem necessidade de pip)
```

---

## Como Executar a Aplicação

Basta executar diretamente no seu terminal com Python:

```bash
python src/app.py
```

Em seguida, abra seu navegador no endereço:
👉 **`http://localhost:8501`**

---

## Teste Rápido no Terminal (CLI)
Para validar o raciocínio e a resposta da Lis diretamente pelo console:
```bash
python src/agente.py
```
