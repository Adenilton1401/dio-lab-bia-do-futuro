# 🤖 Lis 💳: Agente Financeira Inteligente com IA Generativa

> **Bootcamp Bradesco / DIO - Desafio de Projeto: Agente Financeiro Inteligente**  
> Desenvolvido com foco em consultoria de cartões de crédito, consumo consciente, otimização de gastos e eliminação de tarifas.

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
│
├── 📁 data/                            # Base de conhecimento com dados mockados
│   ├── cartoes_credito.json            # Catálogo oficial de cartões e apólice AIG/Amex
│   ├── perfil_cliente.json             # Perfil do cliente (João Silva: R$ 8k renda, R$ 4.5k gastos)
│   ├── transacoes.csv                  # Extrato discriminado em crédito (R$ 2k) e débito (R$ 2.5k)
│   └── historico_atendimento.csv       # Histórico de chamados prévios
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
│   ├── agente.py                       # Orquestrador da Lis e guardrails
│   ├── config.py                       # Configurações do LLM (Gemma 4 via Docker)
│   ├── data_loader.py                  # Processamento dos datasets e métricas financeiras
│   ├── requirements.txt                # Informativo (sem dependências externas)
│   └── README.md                       # Instruções de execução do app
│
├── 📁 assets/                          # Recursos visuais e diagramas
└── 📁 examples/                        # Referências adicionais
```

---

## 📊 O Caso do Cliente: João Silva

- **Renda Mensal:** R$ 8.000,00 | **Patrimônio Líquido:** R$ 25.000,00
- **Cartão Atual:** Classic Internacional pagando **R$ 336,00/ano** de anuidade sem benefícios.
- **Padrão de Gastos:** R$ 4.500,00 por mês (**R$ 2.000 no crédito** e **R$ 2.500 no débito** em supermercados e postos).
- **Diagnóstico da Lis:** Centralizando os R$ 2.500 de despesas rotineiras no cartão de crédito certo (com débito automático na data de vencimento), o cliente atinge **R$ 4.500/mês**, conquista **100% de isenção de anuidade** no **Bradesco American Express® Gold Card**, passa a acumular cerca de **1.500 pontos Livelo/mês** (que nunca expiram) e ativa seguro de viagem de **€ 30.000 no Acordo de Schengen (AIG Seguros)** com Teleconsulta Global Virtual 24/7!

---

## 🧠 Arquitetura de LLM: Gemma 4 via Llama-Server no Docker

Para garantir **privacidade total dos dados financeiros** do cliente (sem envio de extratos para APIs públicas em nuvem) e conformidade estrita com as diretrizes de segurança bancária, o agente opera com um modelo fundacional local:

- **Modelo de Linguagem:** `Gemma 4 12B IT` (`/models/gemma-4-12b-it-UD-Q4_K_XL.gguf`)
- **Servidor de Inferência:** `llama-server` (llama.cpp) com suporte à API compatível com OpenAI (`/v1/chat/completions`)
- **Infraestrutura:** Container **Docker** com exposição de porta (`-p 8080:8080`)
- **Integração do Agente:** O módulo [`src/agente.py`](./src/agente.py) conecta-se via HTTP ao endpoint `http://localhost:8080/v1/chat/completions`
- **Flexibilidade de Ambiente:** Configurado via [`src/config.py`](./src/config.py) através da variável `LLAMA_SERVER_HOST` (suporta `localhost`, `host.docker.internal` ou rede interna de containers)
- **Modo Reasoning / Thinking:** Parâmetro `max_tokens` ajustado para 2048, permitindo que o Gemma 4 processe o raciocínio financeiro estruturado antes de emitir a resposta consultiva ao cliente.

---

## 🚀 Como Executar o Protótipo

A aplicação utiliza exclusivamente a **Biblioteca Padrão do Python**, sem necessidade de instalar pacotes via `pip`:

### 1. Iniciar a Aplicação Web
```bash
python src/app.py
```
Acesse no seu navegador: **`http://localhost:8501`**

### 2. Teste Direto pelo Terminal (CLI)
```bash
python src/agente.py
```

---

## 🛡️ Segurança e Anti-Alucinação

- **Grounding Estrito:** Recomendações restritas aos produtos cadastrados no catálogo oficial.
- **Proteção LGPD:** Recusa explícita e automática a pedidos de senhas, CVV ou números de cartão.
- **Crédito Consciente:** Alertas constantes para manutenção de reservas financeiras e quitação integral da fatura no vencimento.
