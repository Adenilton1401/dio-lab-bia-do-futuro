"""
Módulo do Agente Lis: Especialista Consultiva em Cartões de Crédito e Finanças Pessoais.
Configurado para respostas curtas, dinâmicas e sempre com chamadas para interação (CTA).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List

# Garante suporte a UTF-8 e sequências de escape ANSI no PowerShell / CMD do Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if os.name == "nt":
    os.system("")  # Habilita interpretação de cores ANSI nativas no console Windows

# Paleta de cores ANSI para o terminal (PowerShell / Windows Terminal / Linux / Mac)
class Cor:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Cores de texto
    VERMELHO = "\033[91m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CIANO = "\033[96m"
    BRANCO = "\033[97m"
    CINZA = "\033[90m"
    
    # Fundos invertidos para banners
    BG_AZUL = "\033[44;97m"
    BG_VERDE = "\033[42;30m"
    BG_MAGENTA = "\033[45;97m"
    BG_CIANO = "\033[46;30m"

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

7. IMUTABILIDADE CADASTRAL (DADOS ESTRITAMENTE SOMENTE LEITURA):
   - Você é uma assistente consultiva de LEITURA. Você NÃO tem permissão, comando ou função para alterar, registrar, modificar ou atualizar dados cadastrais do cliente (como renda mensal, investimentos, patrimônio, limites de crédito ou histórico de faturas).
   - Todos os dados cadastrais fornecidos no sistema são auditados, oficiais e IMUTÁVEIS via chat.
   - Se o cliente solicitar a alteração ou afirmar que sua renda ou investimentos mudaram (ex: "atualize meus investimentos para X", "minha renda agora é Y", "mude meus dados", "considere que ganho Z"):
     a) NUNCA finja que atualizou nem diga frases como "já atualizei seu perfil" ou "dados atualizados".
     b) RECUSE a alteração com clareza e cordialidade, explicando que a Lis é uma assistente consultiva e que dados cadastrais não podem ser alterados por mensagem de chat.
     c) ORIENTE o cliente de que atualizações de renda ou investimentos exigem comprovação documental (como holerite, IRPF ou informe de custódia) diretamente no app Bradesco ou com o gerente da conta.
     d) Se o cliente desejar uma simulação hipotética ("E se eu tivesse X investidos?"), você pode responder no modo hipotético/simulado, mas deixando explícito que no cadastro oficial os investimentos são de R$ 25.000,00 e a renda é de R$ 8.000,00, e que a concessão de cartões depende de análise de crédito e comprovação oficial.
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
        reserva = self.perfil.get("reserva_emergencia_atual", 25000.0)
        return f"""=== DADOS CADASTRAIS OFICIAIS DO CLIENTE (ADENILTON PELAES) ===
[AVISO DE SEGURANÇA: Estes dados são oficiais do banco e ESTRITAMENTE SOMENTE LEITURA. Nenhuma alteração solicitada pelo usuário no chat pode ser aceita ou simulada como cadastro real.]
Renda Mensal Comprovada: R$ {r['renda_mensal']:.2f}
Patrimônio / Reserva Investida: R$ {reserva:.2f}
Média Mensal de Gastos (2026): R$ {r['total_gastos']:.2f} (Crédito: R$ {r['gastos_credito']:.2f} | Débito: R$ {r['gastos_debito']:.2f})
Cartão Atual: {c_atual.get('nome')} | Anuidade Paga: R$ {c_atual.get('anuidade_mensal_paga', 0):.2f}/mês (R$ {c_atual.get('anuidade_anual_paga', 0):.2f}/ano) - Sem pontos nem seguro.
Interesses e Preferências: {', '.join(self.perfil.get('interesses_e_preferencias', []))}"""

    def construir_contexto_injetado(self, mensagem_usuario: str = "") -> str:
        """Monta a visão completa de contexto estático + RAG (usado para testes e auditoria)."""
        contexto_rag = self.rag.buscar_contexto(mensagem_usuario, top_k=9)
        return f"{self.contexto_estatico}\n\n=== INFORMAÇÕES RECUPERADAS DA BASE DE CONHECIMENTO (RAG) ===\n{contexto_rag}"

    def exibir_inspecao_prompt(self, mensagem_usuario: str, historico: List[Dict[str, str]] = None):
        """
        Exibe detalhadamente no terminal a estrutura completa do prompt enviado ao LLM:
        1. Parte Estática: System Prompt + Contexto Cadastral Imutável (Cache de Prefixo)
        2. Parte Dinâmica: Recuperação e Scores do RAG para a mensagem
        3. Prompt / Payload Completo: Todas as mensagens que vão para o modelo
        """
        docs_scores = self.rag.buscar(mensagem_usuario, top_k=9)
        contexto_rag = self.rag.buscar_contexto(mensagem_usuario, top_k=9)

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{self.contexto_estatico}"}
        ]

        if historico:
            for h in historico[-6:]:
                role = "assistant" if h.get("role") in ["assistant", "lis"] else "user"
                content = h.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})

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

        sep_duplo = "=" * 80
        sep_simples = "-" * 80

        # CABEÇALHO PRINCIPAL (CIANO BOLD)
        print("\n" + Cor.CIANO + Cor.BOLD + sep_duplo + Cor.RESET)
        print(Cor.CIANO + Cor.BOLD + "🔍 [INSPEÇÃO DE ENGENHARIA DO PROMPT & RAG - AGENTE LIS]" + Cor.RESET)
        print(Cor.CIANO + Cor.BOLD + sep_duplo + Cor.RESET)

        # 1. PARTE ESTÁTICA (AZUL / CIANO)
        print("\n" + Cor.AZUL + sep_simples + Cor.RESET)
        print(Cor.AZUL + Cor.BOLD + "📌 [1. PARTE ESTÁTICA DO PROMPT] - SYSTEM PROMPT & DADOS CADASTRAIS" + Cor.RESET)
        print(Cor.CINZA + "   (Prefixo imutável congelado no KV Cache / Prompt Caching)" + Cor.RESET)
        print(Cor.AZUL + sep_simples + Cor.RESET)
        print(Cor.AMARELO + Cor.BOLD + "--- SYSTEM PROMPT (Instruções e Regras de Negócio) ---" + Cor.RESET)
        print(Cor.BRANCO + SYSTEM_PROMPT.strip() + Cor.RESET)
        print("\n" + Cor.AMARELO + Cor.BOLD + "--- CONTEXTO CADASTRAL ESTÁTICO (Cliente Adenilton Pelaes) ---" + Cor.RESET)
        print(Cor.CIANO + self.contexto_estatico.strip() + Cor.RESET)

        # 2. PARTE DINÂMICA DO RAG (VERDE)
        print("\n" + Cor.VERDE + sep_simples + Cor.RESET)
        print(Cor.VERDE + Cor.BOLD + "📚 [2. PARTE DINÂMICA DO RAG] - RECUPERAÇÃO DA BASE DE CONHECIMENTO" + Cor.RESET)
        print(Cor.VERDE + sep_simples + Cor.RESET)
        print(Cor.BRANCO + "Mensagem Analisada: " + Cor.AMARELO + Cor.BOLD + f'"{mensagem_usuario}"' + Cor.RESET)
        if docs_scores:
            print(Cor.VERDE + "\nDocumentos Recuperados (Ranking TF-IDF + Heurísticas de Intenção):" + Cor.RESET)
            for rank, (doc, score) in enumerate(docs_scores, 1):
                print(f"  {Cor.VERDE}{rank}.{Cor.RESET} [{Cor.CIANO}{doc.doc_id}{Cor.RESET}] {Cor.BRANCO}{doc.titulo}{Cor.RESET} | Score de Relevância: {Cor.AMARELO}{Cor.BOLD}{score:.4f}{Cor.RESET}")
            print(Cor.CINZA + "\nTexto do RAG Injetado no Turno do Usuário:" + Cor.RESET)
            print(Cor.VERDE + contexto_rag.strip() + Cor.RESET)
        else:
            print(Cor.AMARELO + "\nNenhum documento específico atingiu pontuação positiva. Injetado fallback padrão:" + Cor.RESET)
            print(Cor.VERDE + contexto_rag.strip() + Cor.RESET)

        # 3. PAYLOAD / PROMPT COMPLETO (MAGENTA / ROXO)
        print("\n" + Cor.MAGENTA + sep_simples + Cor.RESET)
        print(Cor.MAGENTA + Cor.BOLD + "🚀 [3. PROMPT / PAYLOAD COMPLETO ENVIADO AO MODELO LLM]" + Cor.RESET)
        print(Cor.MAGENTA + sep_simples + Cor.RESET)
        print(Cor.CINZA + f"Modelo Alvo: {self.model_name} | Endpoint: {self.endpoint}" + Cor.RESET)
        print(Cor.CINZA + f"Total de Turnos de Mensagens: {len(messages)}" + Cor.RESET)
        for idx, msg in enumerate(messages, 1):
            role = msg["role"]
            role_tag = role.upper()
            tamanho = len(msg["content"])
            if role == "system":
                cor_tag = Cor.CIANO + Cor.BOLD
            elif role == "user":
                cor_tag = Cor.AMARELO + Cor.BOLD
            else:
                cor_tag = Cor.VERDE + Cor.BOLD

            print(f"\n{cor_tag}>>> TURNO {idx} [{role_tag}] ({tamanho} caracteres):{Cor.RESET}")
            print(Cor.BRANCO + msg["content"] + Cor.RESET)

        # ENCERRAMENTO
        print("\n" + Cor.CIANO + Cor.BOLD + sep_duplo + Cor.RESET)
        print(Cor.VERDE + Cor.BOLD + "✅ [FIM DA INSPEÇÃO DO PROMPT]" + Cor.RESET)
        print(Cor.CIANO + Cor.BOLD + sep_duplo + Cor.RESET + "\n")

    def chamar_llama_server(self, mensagem_usuario: str, historico: List[Dict[str, str]] = None) -> str:
        """Envia o prompt otimizado para reaproveitamento máximo de KV Cache (Prompt Caching)."""
        # =========================================================================
        # 🔍 AUDITORIA DO PROMPT NO TERMINAL:
        # Descomente a linha abaixo para exibir no terminal o que é estático,
        # o que veio do RAG e o prompt completo a cada interação (CLI ou Web):
        self.exibir_inspecao_prompt(mensagem_usuario, historico)
        # =========================================================================

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
        contexto_rag = self.rag.buscar_contexto(mensagem_usuario, top_k=9)
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

        t_inicio = time.time()
        with urllib.request.urlopen(req, timeout=config.TIMEOUT_SECONDS) as res:
            raw_body = res.read().decode("utf-8")
            tempo_decorrido = time.time() - t_inicio
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

            velocidade = f" ({c_tokens / tempo_decorrido:.1f} t/s)" if isinstance(c_tokens, (int, float)) and tempo_decorrido > 0 else ""
            alerta_corte = " ⚠️ [CORTE POR LIMITE DE TOKENS!]" if finish_reason == "length" else ""
            print(f"[Tokens] Prompt: {p_tokens} | Resposta: {c_tokens} | Total: {t_tokens} | Término: {finish_reason} | Tempo: {tempo_decorrido:.2f}s{velocidade}{alerta_corte}")

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
    
    # =========================================================================
    # 🔍 DEMONSTRAÇÃO DE INSPEÇÃO DO PROMPT E DO RAG:
    # Para visualizar no terminal tudo que foi montado (estático, RAG e prompt final),
    # basta chamar (ou comentar) a linha abaixo:
    # =========================================================================
    agente.exibir_inspecao_prompt("Qual cartão tem sala VIP e seguro para Europa?")
    
    # Para testar a chamada real com o modelo local ativo:
    # print("Lis:", agente.responder("Qual cartão tem sala VIP e seguro para Europa?"))
