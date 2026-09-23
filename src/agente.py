"""
Módulo do Agente Lis: Especialista Consultiva em Cartões de Crédito e Finanças Pessoais.
Configurado para respostas curtas, dinâmicas e sempre com chamadas para interação (CTA).
"""

import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List
try:
    from data_loader import DataLoader
    import config
except ImportError:
    from src.data_loader import DataLoader
    from src import config


SYSTEM_PROMPT = """Você é a Lis, especialista consultiva em cartões de crédito e finanças pessoais do ecossistema Bradesco.
Seu propósito é ajudar clientes a escolherem ou trocarem de cartão de crédito de acordo com o perfil do cliente, eliminando custos desnecessários com anuidades, aproveitando benefícios reais (pontos Livelo, milhas, cashback, seguros de viagem AIG/Amex e salas VIP) e a utilizarem o crédito de forma consciente.

### REGRAS FUNDAMENTAIS DE ESTILO E CONCISÃO:
1. RESPOSTAS CURTAS E DIRETAS:
   - Seja SEMPRE cordial, simpática, concisa e objetiva. Escreva no máximo 2 a 3 parágrafos curtos ou bullet points diretos.
   - NUNCA envie blocos gigantes de texto ou todas as informações de uma vez. Conduza o cliente aos poucos, respondendo exatamente ao que foi perguntado.
   - Responda SEMPRE diretamente em português, sem rascunhar em inglês ou expor etapas de raciocínio intermediárias.

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

6. SEGURANÇA E ESCOPO:
   - NUNCA solicite, armazene ou aceite senhas, códigos de segurança (CVV) ou tokens. Se o usuário mencionar algo do tipo, alerte educadamente que por segurança esses dados nunca devem ser compartilhados e que confirmações são feitas apenas pelo app oficial.
   - Seu foco exclusivo são cartões de crédito, benefícios e finanças diárias. Se o usuário perguntar sobre investimentos em bolsa, criptomoedas ou day trade, esclareça com simpatia que seu foco é cartões e benefícios bancários.
"""


try:
    from rag import SimpleRAG
except ImportError:
    from src.rag import SimpleRAG


class AgenteLis:
    def __init__(self, data_loader: DataLoader = None):
        self.loader = data_loader or DataLoader()
        self.perfil = self.loader.carregar_perfil_cliente()
        self.cartoes = self.loader.carregar_cartoes()
        self.resumo = self.loader.obter_resumo_financeiro()
        self.rag = SimpleRAG(data_loader=self.loader)
        self.contexto_estatico = self.obter_contexto_estatico_cliente()
        self.endpoint = config.LLAMA_CHAT_ENDPOINT
        self.model_name = config.DEFAULT_MODEL_NAME

    def obter_contexto_estatico_cliente(self) -> str:
        """Monta o contexto cadastral imutável do cliente para congelamento no KV Cache."""
        r = self.resumo
        c_atual = self.perfil.get("cartao_atual", {})
        return f"""=== DADOS CADASTRAIS DO CLIENTE (JOÃO SILVA) ===
Renda Mensal Comprovada: R$ {r['renda_mensal']:.2f}
Média Mensal de Gastos: R$ {r['total_gastos']:.2f} (Crédito: R$ {r['gastos_credito']:.2f} | Débito: R$ {r['gastos_debito']:.2f})
Cartão Atual: {c_atual.get('nome')} | Anuidade Paga: R$ {c_atual.get('anuidade_mensal_paga', 0):.2f}/mês (R$ {c_atual.get('anuidade_anual_paga', 0):.2f}/ano) - Sem pontos nem seguro.
Interesses e Preferências: {', '.join(self.perfil.get('interesses_e_preferencias', []))}"""

    def construir_contexto_injetado(self, mensagem_usuario: str = "") -> str:
        """Monta a visão completa de contexto estático + RAG (usado para testes e auditoria)."""
        contexto_rag = self.rag.buscar_contexto(mensagem_usuario, top_k=2)
        return f"{self.contexto_estatico}\n\n=== INFORMAÇÕES RECUPERADAS DA BASE DE CONHECIMENTO (RAG) ===\n{contexto_rag}"

    def chamar_llama_server(self, mensagem_usuario: str, historico: List[Dict[str, str]] = None) -> str:
        """Envia o prompt otimizado para reaproveitamento máximo de KV Cache (Prompt Caching)."""
        # 1. Turno SYSTEM 100% ESTÁTICO (Prefixo congelado no KV Cache entre turnos)
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{self.contexto_estatico}"}
        ]

        # 2. Histórico Sequencial da Conversa (Mantém o prefixo de cache intacto)
        if historico:
            for h in historico[-6:]:
                role = "assistant" if h.get("role") in ["assistant", "lis"] else "user"
                content = h.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})

        # 3. Turno Atual do Usuário: anexa o contexto dinâmico do RAG apenas no final
        contexto_rag = self.rag.buscar_contexto(mensagem_usuario, top_k=2)
        if contexto_rag:
            conteudo_user = (
                f"=== INFORMAÇÕES RELEVANTES DA BASE DE CONHECIMENTO (RAG) ===\n"
                f"{contexto_rag}\n\n"
                f"=== MENSAGEM DO CLIENTE ===\n"
                f"{mensagem_usuario}"
            )
        else:
            conteudo_user = mensagem_usuario

        messages.append({"role": "user", "content": conteudo_user})

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

            # Estatísticas de consumo de tokens e motivo de finalização
            usage = data.get("usage", {})
            finish_reason = data["choices"][0].get("finish_reason", "unknown")
            p_tokens = usage.get("prompt_tokens", "?")
            c_tokens = usage.get("completion_tokens", "?")
            t_tokens = usage.get("total_tokens", "?")

            alerta_corte = " ⚠️ [CORTE POR LIMITE DE TOKENS!]" if finish_reason == "length" else ""
            print(f"[Tokens] Prompt: {p_tokens} | Resposta: {c_tokens} | Total: {t_tokens} | Término: {finish_reason}{alerta_corte}")

            return conteudo

    def responder(self, mensagem_usuario: str, historico_conversa: List[Dict[str, str]] = None) -> str:
        """Envia todas as interações do usuário diretamente para o LLM sem respostas pré-programadas."""
        try:
            resposta_llm = self.chamar_llama_server(mensagem_usuario, historico_conversa)
            if resposta_llm:
                return resposta_llm
            return "Não obtive resposta do modelo de inteligência artificial. Por favor, tente novamente."
        except Exception as e:
            print(f"[ERRO LLM] Falha ao consultar o modelo: {e}")
            if hasattr(e, "read"):
                try:
                    detalhes = e.read().decode("utf-8")
                    print(f"[ERRO LLM Detalhes] {detalhes}")
                except Exception:
                    pass
            return "Desculpe, ocorreu uma instabilidade ao conectar com o modelo de inteligência artificial. Verifique se o servidor local está ativo."


if __name__ == "__main__":
    agente = AgenteLis()
    print("--- Teste Simples ---")
    print("Usuário: Oi")
    print("Lis:", agente.responder("Oi"))
