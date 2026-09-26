# Roteiro do Pitch: Lis 💳 (3 Minutos)

> **Projeto:** Lis — Especialista Consultiva em Cartões de Crédito e Finanças Pessoais  
> **Desenvolvido por:** Adenilton Pelaes  
> **Contexto:** Bootcamp Bradesco / DIO (BIA do Futuro)  
> **Arquitetura:** Python Standard Library (100% Nativo) + SimpleRAG (TF-IDF multidocumento, top_k=9) + Prompt Caching (KV Cache) + LLM Local (Gemma 4 / Llama 3.2)  

---

## 1. Roteiro Cronometrado para Apresentação em Vídeo

```
[00:00 - 00:30] Bloco 1: O Problema do Consumidor Bancário
[00:30 - 01:30] Bloco 2: A Solução Lis e o Diagnóstico de Adenilton Pelaes
[01:30 - 02:30] Bloco 3: Demonstração na Prática & Engenharia de IA de Ponta
[02:30 - 03:00] Bloco 4: Diferenciais de Negócio, Impacto e Encerramento
```

---

### ⏱️ Bloco 1: O Problema Real (00:00 - 00:30 — 30 segundos)

> *"Você sabia que mais de 60% dos brasileiros pagam anuidades bancárias caras por cartões que não devolvem nada, enquanto milhões gastam fortunas no débito e perdem milhas, seguros e dinheiro de volta que poderiam render mais de R$ 1.500 de economia por ano?*
>
> *A escolha de cartões virou um labirinto de letrinhas miúdas: regras de isenção confusas, benefícios ocultos e chatbots tradicionais que só sabem exibir saldo ou empurrar produtos de forma cega sem entender a realidade de quem está do outro lado."*

---

### ⏱️ Bloco 2: A Solução Lis & O Caso Real (00:30 - 01:30 — 1 minuto)

> *"Para transformar essa experiência, desenvolvi a **Lis**: uma inteligência artificial consultiva, empática e focada em crédito consciente, inspirada no ecossistema de inovação do Bradesco.*
>
> *Diferente de um assistente de vendas comum, a Lis analisa o comportamento financeiro real do cliente através de seu extrato categorizado e perfil de consumo.*
>
> *Veja o caso real do cliente **Adenilton Pelaes**: ele possui uma renda comprovada de R$ 8.000,00 e uma reserva de R$ 25.000,00, mas está preso a um cartão Classic básico pagando R$ 336,00 de anuidade por ano sem direito a pontos nem seguros. Além disso, gasta R$ 2.540,00 no débito em contas essenciais como supermercado e combustível, e R$ 2.098,00 no crédito.*
>
> *Em vez de empurrar um cartão inacessível, a Lis calcula uma virada estratégica: ao migrar os gastos habituais do débito para o crédito com débito automático da fatura, o Adenilton atinge R$ 4.638,00 por mês, conquista **100% de isenção de anuidade** no **Bradesco American Express® Gold Card**, passa a acumular **pontos Livelo vitalícios**, ativa apólice internacional de seguro viagem de **€ 30.000 no Tratado de Schengen** com teleconsulta 24/7 e garante **acesso gratuito a Salas VIP via LoungeKey**! Tudo isso sem gastar um único real a mais do seu orçamento."*

---

### ⏱️ Bloco 3: Demonstração na Prática & Engenharia de IA (01:30 - 02:30 — 1 minuto)

*(Gravação de tela exibindo a interface web interativa em modo escuro e os logs coloridos no terminal do PowerShell)*

> *"Na tela, vemos a solução completa funcionando:*
>
> 1. *O cliente envia dúvidas naturais como: 'Eu tenho acesso à sala VIP?' ou 'Como funciona a cobertura para a Europa?'.*
> 2. *Nos bastidores, entra em ação o **SimpleRAG**: um mecanismo de recuperação vetorial TF-IDF implementado **100% com a Biblioteca Padrão do Python**, sem dependências externas pesadas. Ele indexa 9 documentos da base de conhecimento — extrato anual, apólice AIG/Amex, catálogo de cartões e histórico — recuperando exatamente as evidências contratuais corretas com zero alucinação.*
> 3. *Implementamos **Prompt Caching** congelando o System Prompt e os dados cadastrais no prefixo do KV Cache, reduzindo a latência de resposta e o consumo computacional.*
> 4. *Para auditoria de engenharia, criamos um módulo de inspeção no terminal com cores ANSI dinâmicas, permitindo validar em tempo real o que é estático, o que veio do RAG e o payload final enviado ao modelo local.*
> 5. *E os **Guardrails de Segurança e LGPD** são inflexíveis: a Lis bloqueia tentativas de alteração cadastral por chat, recusa a captura de senhas ou códigos de segurança (CVV) e nunca recomenda cartões de alta renda, como o The Platinum Card de R$ 20k, sem explicar a barreira de elegibilidade."*

---

### ⏱️ Bloco 4: Diferenciais e Impacto (02:30 - 03:00 — 30 segundos)

> *"O grande diferencial da Lis é ser uma **mentora financeira leal** e não um bot de bater metas. Ela alia a vanguarda dos Grandes Modelos de Linguagem à transparência regulatória e à educação financeira.*
>
> *O impacto gerado é imediato: eliminamos custos ocultos para o cliente, otimizamos o retorno de cada compra e construímos um vínculo de confiança inabalável entre o cliente e o banco.*
>
> *Com a Lis, o cartão de crédito deixa de ser um gerador de dívidas para se tornar uma poderosa alavanca de benefícios, segurança e qualidade de vida. Muito obrigado!"*

---

## 2. Ficha Técnica do Projeto (Resumo de Engenharia)

| Componente | Especificação Técnica | Destaque de Inovação |
| :--- | :--- | :--- |
| **Desenvolvedor** | Adenilton Pelaes | Bootcamp Bradesco / DIO (BIA do Futuro) |
| **Core Runtime** | Python 3 (Standard Library pura) | **Zero dependências externas pip** (`urllib`, `json`, `math`, `re`, `unicodedata`, `collections`, `http.server`) |
| **Mecanismo RAG** | SimpleRAG TF-IDF Multidocumento | Busca em 9 fontes de conhecimento com heurísticas semânticas de intenção bancária (`top_k=9`) |
| **Otimização LLM** | Prompt Caching / KV Cache Freeze | Prefixo estático congelado (System Prompt + Dados Oficiais Imutáveis) |
| **Modelo de IA** | Gemma 4 / Llama 3.2 via llama-server | Execução local com endpoint OpenAI compatível e controle de temperatura |
| **Auditoria & Telemetria** | `exibir_inspecao_prompt` Colorido | Exibição em cores ANSI no PowerShell: Bloco Estático (Azul), RAG (Verde) e Payload Completo (Magenta) |
| **Interface Web** | Servidor HTTP Multi-thread (`app.py`) | UI Moderna Dark Mode com atalhos rápidos e rodapé autoral com créditos do desenvolvedor |
| **Guardrails** | Anti-Alucinação, LGPD e Imutabilidade | Dados oficiais em modo somente leitura; bloqueio de senhas/CVV; crédito consciente contra endividamento |

---

## 3. Checklist de Gravação do Pitch

- [x] Roteiro cronometrado rigorosamente em 3 minutos (30s + 60s + 60s + 30s)
- [x] Apresentação do problema real do consumidor bancário brasileiro
- [x] Solução e estratégia de crédito consciente com o caso real de **Adenilton Pelaes**
- [x] Demonstração técnica da aplicação web, do SimpleRAG nativo e dos logs no terminal
- [x] Menção à apólice AIG Seguros (Schengen € 30.000), pontos Livelo e salas VIP via LoungeKey
- [x] Destaque para os guardrails anti-alucinação, Prompt Caching e segurança LGPD
- [ ] Gravação do vídeo e publicação no YouTube / Loom / Google Drive

---

## 4. Link do Vídeo da Apresentação

> Adicione aqui o link final do vídeo gravado:

`[Insira aqui o link do seu vídeo do Pitch - YouTube, Loom ou Google Drive]`
