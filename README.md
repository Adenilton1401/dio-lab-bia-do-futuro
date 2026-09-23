# 🤖 Lis 💳: Agente Financeira Inteligente com IA Generativa

> **Bootcamp Bradesco / DIO - Desafio de Projeto: Agente Financeiro Inteligente**  
> Desenvolvido com foco em consultoria de cartões de crédito, consumo consciente, otimização de gastos, eliminação de tarifas e inteligência em finanças pessoais.

---

## 🎯 Sobre o Projeto

A **Lis** é uma agente financeira de IA generativa consultiva e proativa do ecossistema Bradesco. Em vez de agir como vendedora de metas bancárias ou chatbot reativo de menu fixo, a Lis analisa o comportamento financeiro real do cliente por meio de seus extratos e preferências.

Ela identifica oportunidades de **troca consciente de pagamentos no débito por crédito**, permitindo que o cliente alcance **100% de isenção de anuidade**, acumule pontos ou cashback e ative seguros internacionais de viagem (**AIG Seguros / Bradesco American Express**) sem comprometer seu orçamento.

---

## 🏗️ Estrutura do Repositório

```
dio-lab-bia-do-futuro/
│
├── 📄 README.md                        # Visão geral e documentação consolidada
├── 📄 tests_rag.py                     # Suíte de testes automatizados do RAG e Agente
│
├── 📁 data/                            # Base de conhecimento com dados mockados
│   ├── cartoes_credito.json            # Catálogo oficial de cartões e apólice AIG/Amex
│   ├── perfil_cliente.json             # Perfil do cliente (João Silva: R$ 8k renda, Classic atual)
│   ├── transacoes.csv                  # 146 transações exclusivas de 2026 (Jan a Set) categorizadas
│   └── historico_atendimento.csv       # Histórico de chamados prévios (anuidade, milhas, seguros)
│
├── 📁 docs/                            # Documentação técnica e metodológica
│   ├── 01-documentacao-agente.md       # Persona, arquitetura e guardrails anti-alucinação
│   ├── 02-base-conhecimento.md         # Modelagem dos dados e estratégia de RAG
│   ├── 03-prompts.md                   # System Prompt, Few-Shot e tratamento de Edge Cases
│   ├── 04-metricas.md                  # Matriz de avaliação, testes estruturados e qualidade
│   └── 05-pitch.md                     # Roteiro cronometrado de Pitch (3 minutos)
│
├── 📁 src/                             # Aplicação e protótipo funcional
│   ├── app.py                          # Aplicação Web Interativa (Python nativo)
│   ├── agente.py                       # Orquestrador da Lis, telemetria e Prompt Caching
│   ├── rag.py                          # SimpleRAG: Motor semântico TF-IDF nativo
│   ├── config.py                       # Configurações do LLM (Gemma 4 via Docker)
│   ├── data_loader.py                  # Processamento dos datasets e médias mensais
│   ├── requirements.txt                # Informativo (sem dependências externas)
│   └── README.md                       # Instruções de execução do app
│
├── 📁 assets/                          # Recursos visuais e diagramas
└── 📁 examples/                        # Referências adicionais
```

---

## 📊 O Caso do Cliente: João Silva (Série Histórica 2026)

- **Renda Mensal Comprovada:** R$ 8.000,00 | **Patrimônio Líquido:** R$ 25.000,00
- **Cartão Atual:** Bradesco Classic Internacional pagando **R$ 336,00/ano** de anuidade sem benefícios.
- **Padrão Real de Gastos (Jan a Set/2026):**
  - **Média Mensal:** **R$ 4.638,90/mês** (entre R$ 4.000 e R$ 5.000 todos os meses).
  - **No Débito:** ~R$ 2.540,00/mês (Supermercado: ~R$ 1.856 | Combustível: ~R$ 333 | Farmácia: ~R$ 220).
  - **No Crédito:** ~R$ 2.098,00/mês (Compras online, streaming, lazer, restaurantes).
  - **Frequência:** 13 a 18 transações por mês (146 transações catalogadas).
- **Diagnóstico da Lis:** Centralizando os gastos essenciais rotineiros do débito no crédito (com fatura em débito automático), o cliente atinge **R$ 4.500+/mês**, conquista **100% de isenção de anuidade** no **Bradesco American Express® Gold Card**, passa a acumular cerca de **1.500 pontos Livelo/mês** vitalícios e ativa seguro de viagem de **€ 30.000 no Acordo de Schengen (AIG Seguros)** com Teleconsulta Global 24/7!

---

## ⚡ Inovações Técnicas da Lis

### 1. SimpleRAG (Retrieval-Augmented Generation Nativo)
Implementado 100% com a **Biblioteca Padrão do Python** em [`src/rag.py`](./src/rag.py), sem necessidade de instalar pacotes pesados como ChromaDB, FAISS ou Scikit-learn:
* **Indexação Multidocumento**: Estrutura e indexa transações categorizadas, perfil cadastral, catálogo individual de cartões, apólices de seguro e histórico de chamados.
* **Motor TF-IDF com Normalização Semântica**: Remoção de stopwords do português e normalização de acentos para busca rápida dos blocos mais relevantes.
* **Injeção Cirúrgica**: Em vez de despejar todo o banco de dados no prompt, o agente injeta apenas os 2 chunks mais relevantes para a dúvida atual, economizando tokens e eliminando alucinações.

### 2. Otimização de Prompt Caching (KV Cache)
Para acelerar drasticamente o tempo de resposta no `llama-server` (Gemma 4 local):
* **Prefixo de System Congelado**: O System Prompt e o cadastro básico do cliente permanecem imutáveis no início do prompt.
* **Reaproveitamento de Memória**: O `llama-server` não reprocessa o cabeçalho a cada mensagem, reaproveitando o KV Cache dos turnos anteriores.
* **TTFT Ultrarrápido**: O tempo de início da resposta (**Time To First Token**) cai de segundos para milissegundos nas mensagens subsequentes do diálogo.

### 3. Telemetria em Tempo Real no Console
A cada resposta gerada pelo modelo, o console exibe estatísticas detalhadas de execução:
```text
[Tokens] Prompt: 4972 | Resposta: 783 | Total: 5755 | Término: stop | Tempo: 6.45s (121.4 t/s)
```
* Monitoramento de tokens de entrada e saída.
* Tempo total decorrido em segundos.
* Velocidade de processamento em tokens por segundo (**t/s**).
* Alerta visual automático caso ocorra corte por limite de tokens (`finish_reason: length`).

### 4. Interação 100% Conversacional via IA (Zero Respostas Prontas)
* Todas as mensagens ("Oi", saudações, dúvidas fora de escopo ou perguntas sensíveis) são processadas e redigidas diretamente pelo **Gemma 4**.
* Os guardrails de segurança (não compartilhamento de senhas/CVV) e direcionamento consultivo foram migrados diretamente para o `SYSTEM_PROMPT` da Lis.

---

## 🧠 Arquitetura de LLM: Gemma 4 via Llama-Server no Docker

Para garantir **privacidade total dos dados financeiros** do cliente (sem envio de extratos bancários para APIs públicas em nuvem), o agente opera com inferência local:

- **Modelo de Linguagem:** `Gemma 4 12B IT` (`/models/gemma-4-12b-it-UD-Q4_K_XL.gguf`)
- **Servidor de Inferência:** `llama-server` (llama.cpp) com suporte à API compatível com OpenAI (`/v1/chat/completions`)
- **Infraestrutura:** Container **Docker** com exposição de porta (`-p 8080:8080`)
- **Parâmetros de Geração:** `MAX_TOKENS = 10240`, `TIMEOUT_SECONDS = 180`, `TEMPERATURE = 0.2`

---

## 🚀 Como Executar o Protótipo

A aplicação utiliza exclusivamente a **Biblioteca Padrão do Python**, sem dependências externas adicionais via `pip`:

### 1. Iniciar a Aplicação Web
```bash
python src/app.py
```
Acesse no seu navegador: **`http://localhost:8501`**

### 2. Rodar a Suíte de Testes Automatizados (RAG & Agente)
```bash
python tests_rag.py
```
Valida automaticamente:
- Categorização de gastos e extrato de 2026.
- Apólice de seguro viagem Schengen AIG/Amex.
- Recomendações de cashback e isenção de anuidade.
- Histórico de atendimentos prévios.
- Injeção dinâmica no AgenteLis.

---

## 🛡️ Segurança e Anti-Alucinação

- **Grounding Estrito via RAG:** Todas as respostas baseiam-se exclusivamente nos dados indexados em tempo real na base de conhecimento.
- **Imutabilidade Cadastral (Anti-Privilege Escalation):** Bloqueio estrito de tentativas de manipulação ou alteração cadastral autodeclaradas via chat (ex: simular ou fingir aumento de renda ou investimentos para obter cartões de alta renda como o TPC). O agente recusa qualquer edição de dados, reforça que o perfil é estritamente de consulta (somente leitura) e orienta o cliente a enviar comprovantes formais pelo app ou com o gerente.
- **Proteção LGPD:** O agente nunca solicita, armazena ou aceita senhas, códigos de segurança (CVV) ou tokens.
- **Crédito Consciente:** Alertas constantes para quitação integral da fatura no vencimento e manutenção de reservas com liquidez diária.
