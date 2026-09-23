# 🤖 Lis 💳: Agente Financeira Inteligente com IA Generativa

> **Bootcamp Bradesco / DIO - Desafio de Projeto: Agente Financeiro Inteligente**  
> Consultoria especializada em cartões de crédito, consumo consciente, otimização de gastos, eliminação de tarifas e inteligência financeira.

---

## 🎯 Sobre o Projeto

A **Lis** é uma agente financeira de inteligência artificial generativa com perfil consultivo e proativo do ecossistema Bradesco. Diferente de chatbots tradicionais baseados em menus estáticos ou respostas pré-programadas, a Lis analisa o comportamento financeiro real do cliente através de seu extrato e histórico de consumo.

Seu principal objetivo é identificar oportunidades de **migração consciente de gastos do débito para o crédito**, permitindo que o cliente alcance **100% de isenção de anuidade**, acumule pontos Livelo permanentes ou cashback e ative seguros internacionais de viagem (**AIG Seguros / Bradesco American Express**), sem gastar um centavo a mais do seu orçamento.

---

## 🏗️ Estrutura Completa do Repositório

A estrutura de arquivos do projeto reflete exatamente a organização dos módulos de código, bases de dados mockadas, documentação metodológica e suítes de teste:

```
dio-lab-bia-do-futuro/
│
├── 📄 README.md                        # Documentação consolidada e guia do projeto
├── 📄 tests_rag.py                     # Suíte de testes automatizados do SimpleRAG e Agente
├── 📄 Saidas_PowerShell _para_Analise.txt # Log real de execução e telemetria capturado do terminal
│
├── 📁 assets/                          # Recursos visuais e material de apoio
│   ├── README.md                       # Diretrizes de assets visuais
│   └── RoteiroLab.md                   # Roteiro das aulas e pitch do Bootcamp DIO
│
├── 📁 data/                            # Base de conhecimento oficial (6 arquivos de dados)
│   ├── cartoes_credito.json            # Catálogo oficial de cartões, faixas de isenção e apólice AIG/Amex
│   ├── historico_atendimento.csv       # Histórico de chamados prévios (anuidade, milhas, seguros)
│   ├── perfil_cliente.json             # Perfil do cliente (João Silva: R$ 8k renda, Classic atual)
│   ├── perfil_investidor.json          # Perfil de investidor (moderado com foco em liquidez)
│   ├── produtos_financeiros.json       # Catálogo de renda fixa e fundos para alocação de reserva
│   └── transacoes.csv                  # 146 transações categorizadas em 2026 (Janeiro a 20/Setembro)
│
├── 📁 docs/                            # Documentação técnica e metodológica oficial
│   ├── 01-documentacao-agente.md       # Persona, arquitetura, caso de uso e guardrails anti-alucinação
│   ├── 02-base-conhecimento.md         # Modelagem dos dados e estratégia de RAG
│   ├── 03-prompts.md                   # System Prompt, Few-Shot e tratamento de Edge Cases
│   ├── 04-metricas.md                  # Matriz de avaliação, testes estruturados e qualidade
│   └── 05-pitch.md                     # Roteiro cronometrado de Pitch (3 minutos)
│
├── 📁 examples/                        # Referências adicionais do desafio
│   └── README.md                       # Links e referências das etapas do desafio
│
└── 📁 src/                             # Aplicação e protótipo funcional (100% Python Standard Library)
    ├── app.py                          # Servidor HTTP multi-thread e interface web interativa
    ├── agente.py                       # Orquestrador da Lis (Prompt Caching, telemetria e guardrails)
    ├── config.py                       # Configurações do LLM (Gemma 4 via llama-server no Docker)
    ├── data_loader.py                  # Processador de dados (cálculo de médias mensais e elegibilidade)
    ├── rag.py                          # SimpleRAG: Motor semântico TF-IDF nativo multidocumento
    ├── README.md                       # Instruções específicas de execução da pasta src
    └── requirements.txt                # Informativo (projeto com zero dependências externas)
```

---

## 📊 O Caso do Cliente: João Silva (Série Histórica 2026)

O agente trabalha sobre o histórico financeiro consolidado do cliente **João Silva**:

- **Renda Mensal Comprovada:** R$ 8.000,00 | **Patrimônio / Reserva Investida:** R$ 25.000,00 (CDB Liquidez Diária)
- **Cartão Atual:** *Bradesco Classic Internacional*
  - Anuidade paga: **R$ 28,00/mês (R$ 336,00/ano)**
  - Benefícios: **Zero** (sem pontos Livelo, sem cashback, sem seguro de viagem)
- **Comportamento Real de Gastos (Jan a Set/2026 - 146 transações):**
  - **Média Mensal:** **R$ 4.638,90/mês** (entre R$ 4.000 e R$ 5.000 em todos os 9 meses)
  - **No Débito:** Média de **R$ 2.540,15/mês** (Supermercado: ~R$ 1.856 | Combustível: ~R$ 333 | Farmácia: ~R$ 220)
  - **No Crédito:** Média de **R$ 2.098,75/mês** (Compras online, streaming, lazer, restaurantes)
  - **Frequência:** 13 a 18 transações por mês
- **Diagnóstico da Lis:**  
  Centralizando os R$ 2.540 de despesas rotineiras do débito no cartão de crédito adequado (com débito automático da fatura no vencimento), o cliente totaliza **R$ 4.638/mês**, conquista **100% de isenção de anuidade** no **Bradesco American Express® Gold Card**, passa a acumular cerca de **1.500 pontos Livelo/mês** vitalícios e ativa cobertura médica de **€ 30.000 no Acordo de Schengen (AIG Seguros)** com Teleconsulta Global Virtual 24/7!

---

## ⚡ Inovações Técnicas da Lis

### 1. SimpleRAG (Retrieval-Augmented Generation Nativo)
Implementado exclusivamente com a **Biblioteca Padrão do Python** em [`src/rag.py`](./src/rag.py), sem bibliotecas pesadas de terceiros (como ChromaDB, FAISS ou Scikit-learn):
* **Indexação Multidocumento**: Indexa e estrutura as 146 transações do extrato de 2026, perfil financeiro cadastral, catálogo individual de cartões, apólices AIG/Amex e chamados prévios.
* **Motor TF-IDF com Normalização Semântica**: Normalização Unicode (remoção de acentos) e exclusão de stopwords do português para busca assertiva dos chunks mais relevantes.
* **Injeção Cirúrgica no Prompt**: Injeta apenas os 2 chunks mais relevantes para a dúvida do usuário, economizando até 70% de tokens de contexto.

### 2. Arquitetura de Prompt Caching (KV Cache Optimization)
Para viabilizar respostas instantâneas no `llama-server` (Gemma 4 local via Docker):
* **Prefixo de System Congelado**: O `SYSTEM_PROMPT` e os dados cadastrais auditados do cliente ficam estáticos no início do prompt (Tokens 0 a ~650).
* **Reaproveitamento de Memória KV**: O servidor de LLM reutiliza os cálculos dos tokens anteriores entre as mensagens do chat.
* **TTFT Ultrarrápido**: O tempo até o primeiro token (**Time To First Token**) é reduzido de segundos para milissegundos nas mensagens seguintes da conversa.

### 3. Telemetria em Tempo Real no Console
A cada chamada ao modelo, o terminal do PowerShell exibe métricas completas de inferência:
```text
[Tokens] Prompt: 4972 | Resposta: 783 | Total: 5755 | Término: stop | Tempo: 6.45s (121.4 t/s)
```
* **Contagem de Tokens:** Prompt, resposta e total consumido.
* **Tempo Decorrido:** Medição precisa da requisição em segundos.
* **Vazão de Geração:** Velocidade de saída em tokens por segundo (**t/s**).
* **Alerta de Corte:** Indicação visual caso a resposta seja interrompida pelo limite de tokens (`finish_reason: length`).

### 4. Interação 100% Conversacional via LLM
* Todas as mensagens (saudações, dúvidas fora de escopo, transações ou cartões) são processadas e redigidas diretamente pelo modelo **Gemma 4**.
* Respostas pré-programadas/estáticas foram 100% eliminadas; as diretrizes operacionais foram integradas ao System Prompt.

---

## 🧠 Arquitetura de LLM: Gemma 4 via Llama-Server no Docker

Para assegurar **privacidade total dos dados bancários do cliente** (sem envio de extratos financeiros para APIs comerciais em nuvem) e conformidade com diretrizes regulatórias:

- **Modelo de Linguagem:** `Gemma 4 12B IT` (`/models/gemma-4-12b-it-UD-Q4_K_XL.gguf`)
- **Servidor de Inferência:** `llama-server` (llama.cpp) com endpoint compatível com OpenAI (`/v1/chat/completions`)
- **Infraestrutura:** Container **Docker** com exposição de porta (`-p 8080:8080`)
- **Parâmetros de Geração:** `MAX_TOKENS = 10240`, `TIMEOUT_SECONDS = 180`, `TEMPERATURE = 0.2`

---

## 🚀 Como Executar o Protótipo

A aplicação não requer a instalação de nenhum pacote externo via `pip`:

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
- Recuperação e cálculo de médias das transações de 2026 por categoria.
- Apólice de seguro viagem Schengen AIG/Amex.
- Recomendações de cashback e faixas de isenção de anuidade.
- Histórico de contatos anteriores do cliente.
- Injeção dinâmica no AgenteLis.

### 3. Teste Direto pelo Terminal (CLI)
```bash
python src/agente.py
```

---

## 🛡️ Segurança, Anti-Alucinação e Imutabilidade Cadastral

- **Grounding Estrito via RAG:** Todas as recomendações fundamentam-se exclusivamente nos dados reais indexados na base.
- **Imutabilidade Cadastral (Anti-Privilege Escalation):** Bloqueio estrito de tentativas de manipulação ou autodeclaração de dados via chat (ex: fingir aumento de renda ou investimentos para liberar cartões de alta renda como o TPC). O agente recusa a alteração, reforça que o perfil é de somente leitura e orienta a comprovação documental formal no app ou com o gerente.
- **Proteção LGPD:** O agente nunca solicita, armazena ou aceita senhas, códigos de segurança (CVV) ou tokens.
- **Crédito Consciente:** Alertas contínuos para quitação integral da fatura no vencimento e manutenção de reservas com liquidez diária.
