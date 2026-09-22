"""
Módulo do Agente Lis: Especialista Consultiva em Cartões de Crédito e Finanças Pessoais.
Configurado para respostas curtas, dinâmicas e sempre com chamadas para interação (CTA).
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List
from data_loader import DataLoader
import config

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


SYSTEM_PROMPT = """Você é a Lis, especialista consultiva em cartões de crédito e finanças pessoais do ecossistema Bradesco.
Seu propósito é ajudar clientes a eliminarem custos desnecessários com anuidades, aproveitarem benefícios reais (pontos Livelo, milhas, cashback, seguros de viagem AIG/Amex e salas VIP) e utilizarem o crédito de forma consciente.

### REGRAS FUNDAMENTAIS DE ESTILO E CONCISÃO:
1. RESPOSTAS CURTAS E DIRETAS:
   - Seja SEMPRE concisa e objetiva. Escreva no máximo 2 a 3 parágrafos curtos ou bullet points diretos.
   - NUNCA envie blocos gigantes de texto ou todas as informações de uma vez. Conduza o cliente aos poucos, respondendo exatamente ao que foi perguntado.

2. SAUDAÇÕES SIMPLES (NÃO DESPEJE DADOS DE UMA VEZ):
   - Se o cliente apenas disser "Oi", "Olá", "Bom dia" ou mensagens curtas de cumprimento, responda de forma calorosa e breve (1 ou 2 frases) e pergunte como pode ajudar.
   - NUNCA despeje a análise do cartão ou valores do extrato logo no primeiro cumprimento sem o cliente ter perguntado!

3. SEMPRE TERMINE COM UMA CHAMADA PARA INTERAÇÃO:
   - Ao final de toda resposta, faça uma pergunta curta e engajadora para continuar o diálogo (ex: "Quer que eu calcule quanto você economizaria?", "Prefere focar em milhas ou cashback?", "Gostaria de ver os detalhes desse seguro?").

4. FLUIDEZ NATURAL DE CHAT:
   - Responda de forma ágil, empática e conversacional, aproveitando o histórico do diálogo para dar respostas conectadas e fluidas.

5. GROUNDING E ANTI-ALUCINAÇÃO:
   - Use apenas os dados oficiais fornecidos (cartões, valores de anuidade, regras de isenção e seguros AIG/Amex). Nunca invente benefícios.
   - Alerte sempre sobre consumo consciente e pagamento integral da fatura em débito automático.
"""


class AgenteLis:
    def __init__(self, data_loader: DataLoader = None):
        self.loader = data_loader or DataLoader()
        self.perfil = self.loader.carregar_perfil_cliente()
        self.cartoes = self.loader.carregar_cartoes()
        self.resumo = self.loader.obter_resumo_financeiro()
        self.endpoint = config.LLAMA_CHAT_ENDPOINT
        self.model_name = config.DEFAULT_MODEL_NAME

    def construir_contexto_injetado(self) -> str:
        """Monta o contexto enxuto com base nos dados reais mockados."""
        r = self.resumo
        c_atual = self.perfil.get("cartao_atual", {})

        contexto = f"""=== DADOS DO CLIENTE ===
Nome: {r['cliente_nome']} | Renda: R$ {r['renda_mensal']:.2f}
Cartão Atual: {c_atual.get('nome')} | Anuidade Atual: R$ {c_atual.get('anuidade_mensal_paga', 0):.2f}/mês (R$ {c_atual.get('anuidade_anual_paga', 0):.2f}/ano) - Sem pontos nem seguro.
Gastos Mensais: R$ {r['total_gastos']:.2f} (Crédito: R$ {r['gastos_credito']:.2f} | Débito: R$ {r['gastos_debito']:.2f})
Interesses: {', '.join(self.perfil.get('interesses_e_preferencias', []))}

=== CARTÕES DISPONÍVEIS ===
{json.dumps(self.cartoes, indent=2, ensure_ascii=False)}
"""
        return contexto

    def chamar_llama_server(self, mensagem_usuario: str, historico: List[Dict[str, str]] = None) -> str:
        """Envia o prompt para o Gemma 4 via llama-server mantendo o histórico conversacional."""
        contexto = self.construir_contexto_injetado()

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{contexto}"}
        ]

        # Envia o histórico real de mensagens anteriores para contexto contínuo
        if historico:
            for h in historico[-6:]:
                role = "assistant" if h.get("role") in ["assistant", "lis"] else "user"
                content = h.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": mensagem_usuario})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": config.TEMPERATURE,
            "max_tokens": config.MAX_TOKENS
        }

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=config.TIMEOUT_SECONDS) as res:
            raw_body = res.read().decode("utf-8")
            data = json.loads(raw_body)
            choice = data["choices"][0]["message"]
            conteudo = choice.get("content", "").strip()
            
            if not conteudo and choice.get("reasoning_content"):
                conteudo = choice.get("reasoning_content").strip()
            
            return conteudo

    def responder(self, mensagem_usuario: str, historico_conversa: List[Dict[str, str]] = None) -> str:
        """Processa a mensagem com validação rápida e chamada ao Gemma 4."""
        msg_clean = mensagem_usuario.strip()
        msg_lower = msg_clean.lower()
        palavras = msg_lower.split()

        # Resposta amigável e breve para cumprimentos isolados
        saudacoes = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "e aí", "e ai", "opa", "hello", "hey"]
        if msg_lower in saudacoes or (len(palavras) <= 2 and any(w in saudacoes for w in palavras)):
            return (
                f"Olá, {self.resumo['cliente_nome']}! Tudo bem? "
                "Sou a Lis, sua especialista em cartões e finanças no Bradesco. "
                "Como posso te ajudar hoje? Quer ver opções para zerar sua anuidade ou planejar pontos para viagens?"
            )

        # Guardrail 1: Dados sensíveis (senhas, cvv)
        if any(w in msg_lower for w in ["senha", "cvv", "código de segurança", "codigo de seguranca", "token"]):
            return (
                "Por segurança, eu nunca solicito nem armazeno senhas ou o CVV do seu cartão. "
                "Toda confirmação é feita com segurança diretamente no app Bradesco. Posso te ajudar com outra dúvida sobre benefícios?"
            )

        # Guardrail 2: Fora de escopo
        if any(w in msg_lower for w in ["bitcoin", "cripto", "comprar ações", "bolsa de valores", "day trade"]):
            return (
                "Meu foco é te ajudar com cartões de crédito, benefícios e economia diária! "
                "Para investimentos em bolsa ou cripto, recomendo falar com a assessoria especializada do banco. Quer tirar dúvidas sobre seus cartões?"
            )

        # Chamada ao Gemma 4 no llama-server
        try:
            resposta_llm = self.chamar_llama_server(mensagem_usuario, historico_conversa)
            if resposta_llm:
                return resposta_llm
        except Exception:
            pass

        # Fallback grounded conciso
        return self._resposta_consultiva_grounded(mensagem_usuario)

    def _resposta_consultiva_grounded(self, mensagem: str) -> str:
        """Fallback grounded curto e sempre com chamada para interação."""
        msg = mensagem.lower()
        r = self.resumo
        c_atual = self.perfil.get("cartao_atual", {})

        if any(k in msg for k in ["anuidade", "trocar", "viagem", "recomenda", "melhor cartão", "europa", "milhas", "debito", "débito"]):
            return (
                f"Hoje você paga **R$ 336/ano de anuidade** no cartão Classic sem nenhum retorno. "
                f"Concentrando seus **R$ 2.500 do débito no crédito** (somando R$ 4.500/mês), você garante **100% de isenção de anuidade** no **Bradesco Amex Gold Card**!\n\n"
                f"Além de custo zero, você acumula cerca de **1.500 pontos Livelo/mês** (vitalícios) e ganha **seguro médico de € 30.000 para a Europa (Acordo de Schengen)** com Teleconsulta 24/7.\n\n"
                f"Gostaria que eu te mostrasse como funciona a regra de isenção ou prefere comparar com a opção de cashback?"
            )
        elif any(k in msg for k in ["cashback", "like"]):
            return (
                f"Com o **Bradesco Like Visa**, você tem **isenção total de anuidade** (gastos acima de R$ 3.000/mês) e recebe até **3% de cashback direto na fatura**.\n\n"
                f"Com seus R$ 4.500 de gastos habituais, isso representa um desconto mensal de **R$ 90 a R$ 130** todo mês, sem burocracia de milhas.\n\n"
                f"Faz mais sentido para você economizar com cashback direto ou acumular pontos para viajar?"
            )
        elif any(k in msg for k in ["platinum", "tpc", "centurion"]):
            return (
                f"O **The Platinum Card (TPC)** é incrível para salas VIP ilimitadas, mas exige **renda mínima de R$ 20.000** e gastos de R$ 10.000/mês para isenção.\n\n"
                f"Com sua renda de R$ 8.000 e gastos de R$ 4.500, o degrau perfeito é o **Amex Gold Card**, onde você tem isenção total e constrói relacionamento para um upgrade futuro.\n\n"
                f"Quer ver os benefícios de viagem do Amex Gold?"
            )
        else:
            return (
                "Posso te ajudar a eliminar anuidade, simular pontos Livelo ou cashback com seus gastos do dia a dia, ou tirar dúvidas sobre seguros de viagem.\n\n"
                "Qual desses temas você prefere explorar agora?"
            )


if __name__ == "__main__":
    agente = AgenteLis()
    print("--- Teste Simples ---")
    print("Usuário: Oi")
    print("Lis:", agente.responder("Oi"))
