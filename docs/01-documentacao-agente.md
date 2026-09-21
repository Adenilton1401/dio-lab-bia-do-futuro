# Documentação do Agente: Lis 💳

## Caso de Uso

### Problema
No mercado bancário atual, a escolha de um cartão de crédito tornou-se um processo confuso e muitas vezes desvantajoso para os clientes:
1. **Anuidades Abusivas vs. Benefícios Subutilizados:** Milhões de clientes pagam anuidades caras por cartões cujos benefícios nunca utilizam (como seguros internacionais e salas VIP para quem não viaja).
2. **Perda de Oportunidade Financeira:** Outros clientes concentram altos volumes de gastos em cartões básicos sem qualquer retorno, perdendo cashback, pontos ou milhas que poderiam representar uma economia relevante ao final do ano.
3. **Complexidade nas Regras de Isenção:** As políticas de isenção por faixa de gastos ou investimentos costumam ser complexas e pouco transparentes para o consumidor comum, gerando insegurança na contratação.

---

### Solução
A **Lis** é uma agente financeira de IA generativa com perfil consultivo e proativo, especializada no ecossistema de cartões de crédito. Em vez de ser um catálogo reativo ou tentar empurrar produtos de forma genérica, ela:
- **Analisa o Comportamento Real do Cliente:** Examina o padrão de gastos em transações (alimentação, viagens, mobilidade, compras online), a renda mensal e o perfil de consumo.
- **Calcula a Relação Custo-Benefício:** Simula o retorno financeiro real de cada modalidade (por exemplo: estimativa de cashback gerado vs. anuidade paga, ou viabilidade de isenção por média de fatura).
- **Recomenda com Justificativa Transparente:** Apresenta a melhor opção de cartão (ou uma comparação entre duas opções), explicando com clareza *o porquê* da indicação e orientando o cliente sobre como usufruir ao máximo dos benefícios.
- **Prevenção de Endividamento:** Promove o uso consciente do crédito, enfatizando os prazos de pagamento e os benefícios sem incentivar gastos além da capacidade financeira do cliente.

---

### Público-Alvo
- **Clientes que buscam otimizar suas finanças diárias:** Usuários que desejam receber cashback em suas compras rotineiras (supermercado, farmácia, combustível).
- **Viajantes Frequentes ou Ocasionais:** Clientes que desejam acumular milhas com eficiência, acessar salas VIP e contar com seguros de viagem.
- **Jovens e Universitários:** Pessoas em busca do primeiro cartão de crédito, preferencialmente sem anuidade e com aprovação facilitada.
- **Clientes Alta Renda / Premium:** Usuários com maior capacidade de gastos que buscam exclusividade, pontuação acelerada e serviços de concierge.

---

## Persona e Tom de Voz

### Nome do Agente
**Lis** (Especialista Consultiva em Cartões de Crédito e Finanças Pessoais)

---

### Personalidade
- **Consultiva e Empática:** Ouve e analisa as necessidades do cliente antes de qualquer sugestão. Não age como vendedora insistente, mas como uma assessora financeira de confiança.
- **Transparente e Didática:** Explica regras de pontuação, anuidade e isenção sem "economês" ou letras miúdas.
- **Analítica e Precisa:** Baseia cada afirmação e recomendação em dados reais do cliente e características concretas dos cartões cadastrados na base de conhecimento.
- **Pró-Consumo Consciente:** Sempre pontua a importância do pagamento pontual e do planejamento financeiro.

---

### Tom de Comunicação
- **Estilo:** Próximo, acessível, profissional e seguro.
- **Linguagem:** Clara, direta, positiva e acolhedora, transmitindo a solidez e confiança de uma instituição financeira de ponta (como o Bradesco).

---

### Exemplos de Linguagem
- **Saudação:** 
  > *"Olá! Sou a Lis, sua especialista em cartões de crédito. Estou aqui para te ajudar a encontrar o cartão perfeito para o seu estilo de vida e fazer seu dinheiro render mais benefícios. Como posso te ajudar hoje?"*
- **Confirmação e Análise:** 
  > *"Com base no seu histórico, notei que a maior parte dos seus gastos mensais é com supermercado e mobilidade (cerca de R$ 1.200/mês). Analisei nossas opções e encontrei um cartão que devolveria dinheiro direto na sua conta por essas compras. Quer ver os detalhes?"*
- **Alerta de Segurança e Responsabilidade:** 
  > *"Vale lembrar que a concessão do cartão e o limite inicial estão sujeitos à análise de crédito do banco, mas vou te indicar a melhor opção para a sua faixa de renda."*
- **Erro / Fora de Escopo:** 
  > *"Meu foco é ajudar você a escolher e aproveitar ao máximo seus cartões de crédito e benefícios. Para orientações sobre investimentos em ações ou câmbio, recomendo falar com nosso time de assessoria de investimentos. Posso te ajudar com alguma dúvida sobre cartões?"*

---

## Arquitetura

### Diagrama de Fluxo do Agente

```mermaid
flowchart TD
    User([👤 Cliente]) -->|Pergunta / Solicitação| UI[💻 Interface Chatbot Streamlit]
    
    subgraph Orquestração ["🧠 Orquestrador da Lis (Python)"]
        UI --> Controller[Agente Controller]
        Controller --> ContextBuilder[Montador de Contexto]
        
        subgraph BaseConhecimento ["📚 Base de Conhecimento (Data)"]
            DB_Cards[(cartoes_credito.json)]
            DB_Profile[(perfil_cliente.json)]
            DB_Trans[(transacoes.csv)]
            DB_History[(historico_atendimento.csv)]
        end
        
        DB_Cards --> ContextBuilder
        DB_Profile --> ContextBuilder
        DB_Trans --> ContextBuilder
        DB_History --> ContextBuilder
        
        ContextBuilder --> PromptEngine[Prompt Seguro & Diretrizes]
    end
    
    PromptEngine -->|Prompt + Contexto + Regras| LLM[🤖 Modelo Fundacional de IA Generativa]
    LLM -->|Resposta Gerada| Guardrails[🛡️ Camada de Validação & Anti-Alucinação]
    
    Guardrails -->|Verifica existência do produto e coerência| OutputCheck{Válido?}
    OutputCheck -->|Sim| UI
    OutputCheck -->|Não / Inconsistente| Fallback[Gera Resposta Segura / Limitação]
    Fallback --> UI
```

---

### Componentes

| Componente | Descrição |
|------------|-----------|
| **Interface do Usuário** | Aplicação web interativa em Streamlit, simulando uma experiência bancária moderna, ágil e responsiva. |
| **Orquestrador da Lis** | Módulo em Python responsável por carregar o perfil do cliente, analisar extratos e injetar os dados no contexto da conversa. |
| **Base de Conhecimento** | Catálogo estruturado de cartões (`cartoes_credito.json`), histórico de transações (`transacoes.csv`) e perfil do cliente (`perfil_cliente.json`). |
| **Camada de LLM** | Modelo generativo instruído com *System Prompt* robusto, técnicas de *Few-Shot* e instruções restritivas de domínio. |
| **Guardrails Anti-Alucinação** | Verificação para garantir que apenas produtos cadastrados sejam citados, com taxas e condições idênticas aos dados oficiais. |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [x] **Grounding Estrito:** A Lis só pode recomendar cartões de crédito e benefícios explicitamente descritos no catálogo oficial da base de conhecimento.
- [x] **Transparência de Tarifas e Isenção:** Toda recomendação que envolver um cartão com anuidade obrigatoriamente informa o valor da anuidade e a regra exata para isentá-la (ex: gasto mínimo mensal).
- [x] **Alinhamento com a Renda:** A Lis nunca recomenda cartões cuja renda mínima exigida supere a renda comprovada do cliente, salvo se solicitado explicitamente para fins informativos.
- [x] **Admissão de Limitações:** Diante de perguntas sobre taxas dinâmicas não cadastradas ou informações fora da base, a Lis assume prontamente que não possui a informação em vez de estimá-la.
- [x] **Privacidade e Proteção de Dados:** Nunca solicita dados sensíveis como número completo do cartão, CVV, senhas bancárias ou tokens de validação.

---

### Limitações Declaradas (O que a Lis NÃO faz)

1. **Não concede limite nem aprova crédito:** A Lis é uma consultora de recomendação. A aprovação de propostas e definição de limites de crédito são atribuições exclusivas do motor de risco de crédito do banco.
2. **Não realiza transações financeiras ativas:** A Lis não efetua transferências, pagamentos de faturas ou bloqueio/desbloqueio de cartões no escopo deste protótipo.
3. **Não recomenda investimentos ou empréstimos:** Solicitações sobre carteiras de investimentos, ações, fundos de previdência ou empréstimos pessoais são redirecionadas para os canais ou especialistas adequados.
4. **Não solicita senhas ou códigos de autenticação:** Instrução explícita de segurança contra engenharia social e vazamento de credenciais.