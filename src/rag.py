"""
Módulo SimpleRAG: Sistema de Recuperação e Geração Aumentada (RAG) Simplificado.
Implementado 100% com a Biblioteca Padrão do Python (sem dependências externas).
Indexa transações categorizadas, catálogo de cartões, apólices de seguros e histórico.
"""

import math
import re
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Tuple
try:
    from data_loader import DataLoader
except ImportError:
    from src.data_loader import DataLoader


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e pontuações para correspondência semântica."""
    if not texto:
        return ""
    # Remove acentos
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Minúsculas e apenas alfanuméricos
    return re.sub(r"[^\w\s]", " ", sem_acento.lower())


STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sob", "sobre",
    "e", "ou", "mas", "que", "se", "como", "me", "te", "se", "nos", "lhe", "lhes",
    "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas", "esse", "essa",
    "este", "esta", "aquele", "aquela", "eu", "voce", "você", "ele", "ela", "eles",
    "elas", "qual", "quais", "quem", "quanto", "quantos", "quanta", "quantas",
    "ao", "aos", "à", "às", "pelo", "pela", "pelos", "pelas", "ser",
    "estar", "ter", "haver", "fazer", "ir", "esta", "estao", "tem", "pode", "podem"
}


class Documento:
    def __init__(self, doc_id: str, titulo: str, conteudo: str, categoria: str):
        self.doc_id = doc_id
        self.titulo = titulo
        self.conteudo = conteudo
        self.categoria = categoria
        self.tokens = self._tokenizar(conteudo + " " + titulo)

    def _tokenizar(self, texto: str) -> List[str]:
        tokens = normalizar_texto(texto).split()
        return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


class SimpleRAG:
    """Motor de RAG baseado em TF-IDF nativo para a base de conhecimento da Lis."""

    def __init__(self, data_loader: DataLoader = None):
        self.loader = data_loader or DataLoader()
        self.documentos: List[Documento] = []
        self.idf: Dict[str, float] = {}
        self._construir_base_de_conhecimento()
        self._calcular_idf()

    def _construir_base_de_conhecimento(self):
        """Transforma os arquivos em data/ em documentos indexáveis e contextualizados."""
        perfil = self.loader.carregar_perfil_cliente()
        transacoes = self.loader.carregar_transacoes()
        cartoes = self.loader.carregar_cartoes()
        historico = self.loader.carregar_historico_atendimento()

        # 1. Documento de Transações e Categorização de Gastos
        totais_por_categoria = {}
        credito_por_cat = {}
        debito_por_cat = {}
        total_geral = 0.0

        linhas_transacoes = []
        for t in transacoes:
            val = float(t["valor"])
            cat = t["categoria"].replace("_", " ")
            metodo = t["metodo_pagamento"]
            desc = t["descricao"]
            total_geral += val
            totais_por_categoria[cat] = totais_por_categoria.get(cat, 0.0) + val
            if metodo == "credito":
                credito_por_cat[cat] = credito_por_cat.get(cat, 0.0) + val
            else:
                debito_por_cat[cat] = debito_por_cat.get(cat, 0.0) + val
            linhas_transacoes.append(f"- {t['data']}: {desc} ({cat}) -> R$ {val:.2f} via {metodo}")

        resumo_categorias = "\n".join(
            [f"* {cat.title()}: R$ {totais_por_categoria[cat]:.2f} (Débito: R$ {debito_por_cat.get(cat, 0.0):.2f} | Crédito: R$ {credito_por_cat.get(cat, 0.0):.2f})"
             for cat in sorted(totais_por_categoria.keys())]
        )

        doc_transacoes = f"""EXTRATO DETALHADO E CATEGORIZAÇÃO DE GASTOS DO CLIENTE JOÃO SILVA:
Total de Gastos no Mês: R$ {total_geral:.2f}
Total no Débito: R$ {sum(debito_por_cat.values()):.2f}
Total no Crédito: R$ {sum(credito_por_cat.values()):.2f}

DISTRIBUIÇÃO DE GASTOS POR CATEGORIA:
{resumo_categorias}

OPORTUNIDADE DE MIGRAÇÃO DO DÉBITO PARA O CRÉDITO:
As maiores despesas no débito são Supermercado (R$ 1.700,00) e Combustível (R$ 500,00). 
Transferindo esses R$ 2.200 do débito para um cartão de crédito com benefícios (como Amex Gold ou Like Visa), o cliente atinge isenção total de anuidade e pontua na Livelo ou recebe cashback.

ITENS DO EXTRATO:
""" + "\n".join(linhas_transacoes)

        self.documentos.append(Documento(
            doc_id="extrato_transacoes",
            titulo="Extrato, Transações e Categorização de Gastos",
            conteudo=doc_transacoes,
            categoria="financeiro"
        ))

        # 2. Documento do Perfil do Cliente e Diagnóstico
        c_atual = perfil.get("cartao_atual", {})
        diag = perfil.get("diagnostico_oportunidade", {})
        doc_perfil = f"""PERFIL FINANCEIRO DO CLIENTE JOÃO SILVA:
- Nome: {perfil.get('nome')} | Idade: {perfil.get('idade')} anos | Profissão: {perfil.get('profissao')}
- Renda Mensal Comprovada: R$ {perfil.get('renda_mensal', 0):.2f}
- Reserva de Emergência / Investimentos: R$ {perfil.get('reserva_emergencia_atual', 0):.2f}
- Cartão Atual: {c_atual.get('nome')} (Bandeira {c_atual.get('bandeira')})
  * Anuidade Paga: R$ {c_atual.get('anuidade_mensal_paga', 0):.2f}/mês (R$ {c_atual.get('anuidade_anual_paga', 0):.2f}/ano)
  * Benefícios: Nenhum. Não pontua na Livelo, sem cashback e sem seguro viagem.
- Objetivos do Cliente: {', '.join(perfil.get('interesses_e_preferencias', []))}
- Diagnóstico da Lis: {diag.get('problema_atual')}
- Estratégia Recomendada: {diag.get('potencial_migracao')}
- Alerta Consciente: {diag.get('alerta_consciente')}
"""
        self.documentos.append(Documento(
            doc_id="perfil_cliente",
            titulo="Perfil Financeiro, Cartão Atual e Objetivos de João Silva",
            conteudo=doc_perfil,
            categoria="cliente"
        ))

        # 3. Documentos Individuais de Cada Cartão do Catálogo
        for c in cartoes:
            isencao = c.get("politica_isencao", {})
            seg = c.get("seguros_e_assistencias", {})
            prog = c.get("programa_recompensas", {})
            anuidade_info = c.get("anuidade", {})
            val_parc = anuidade_info.get("valor_parcela", 0.0)
            val_total = anuidade_info.get("valor_total", 0.0)
            
            doc_cartao = f"""CARTÃO BRADESCO: {c['nome']} (Categoria: {c.get('categoria', '')})
- Renda Mínima Exigida: R$ {c.get('renda_minima', 0):.2f}
- Anuidade: 12x de R$ {val_parc:.2f} (Total: R$ {val_total:.2f}/ano)
- Regra de Isenção de Anuidade (100%): {isencao.get('regra', 'Consulte condições')}
- Programa de Recompensas: {prog.get('tipo', 'Nenhum')} ({prog.get('descricao', '')})
  * Fator de Conversão / Pontos: {prog.get('fator_conversao', 'N/A')}
  * Validade dos Pontos: {prog.get('validade_pontos', 'N/A')}
- Seguros e Assistências:
  * Cobertura Médica Viagem: {seg.get('despesas_medicas_internacionais', 'Não inclusa')}
  * Teleconsulta 24/7: {'Inclusa (' + seg.get('teleconsulta_descricao', '') + ')' if seg.get('teleconsulta_24h') else 'Não inclusa'}
  * Bagagem: {seg.get('perda_roubo_bagagem', 'Não inclusa')}
  * Veículo Alugado: {seg.get('seguro_veiculo_alugado_crldi', 'Não incluso')}
- Benefícios Chave:
""" + "\n".join([f"  * {b}" for b in c.get("beneficios_chave", [])]) + f"""
- Perfil Ideal: {c.get('perfil_ideal', '')}
"""
            self.documentos.append(Documento(
                doc_id=f"cartao_{c['id']}",
                titulo=f"Catálogo de Cartão: {c['nome']}",
                conteudo=doc_cartao,
                categoria="cartoes"
            ))

        # 4. Documento Especial de Apólice AIG Seguros / Amex
        doc_apolice = """APÓLICE E COBERTURAS DE SEGURO VIAGEM AIG SEGUROS / BRADESCO AMERICAN EXPRESS:
- Cobertura Médica Internacional (DMH): O Amex Gold oferece até US$ 25.000 (€ 30.000), atendendo plenamente às exigências do Acordo de Schengen para viagens à Europa.
- Teleconsulta Global Virtual 24/7: Atendimento médico por vídeo ou chat em português, 24 horas por dia em qualquer país, sem necessidade de deslocamento hospitalar para casos simples.
- Seguro Bagagem: Cobertura de até US$ 2.000 para extravio ou atraso de malas.
- Acompanhante em caso de hospitalização prolongada: Até US$ 3.000.
- Seguro para Veículo Alugado (CDW/LDW): Isenta franquia em caso de colisão ou roubo no exterior ao pagar a locação com o cartão.
- Como Ativar o Seguro: Basta comprar as passagens aéreas ou taxas de embarque integralmente com o cartão elegível (ex: Amex Gold) e emitir o Bilhete de Seguro no portal antes do embarque.
"""
        self.documentos.append(Documento(
            doc_id="apolice_seguro_viagem",
            titulo="Apólice de Seguro Viagem AIG / Amex e Acordo de Schengen",
            conteudo=doc_apolice,
            categoria="seguros"
        ))

        # 5. Documento de Histórico de Atendimentos Anteriores
        linhas_hist = []
        for h in historico:
            linhas_hist.append(f"- Data: {h['data']} | Canal: {h['canal']} | Tema: {h['tema']} | Resumo: {h['resumo']}")
        doc_hist = "HISTÓRICO DE ATENDIMENTOS E CONTATOS ANTERIORES DO CLIENTE:\n" + "\n".join(linhas_hist)

        self.documentos.append(Documento(
            doc_id="historico_atendimento",
            titulo="Histórico de Chamados e Atendimentos Anteriores",
            conteudo=doc_hist,
            categoria="atendimento"
        ))

    def _calcular_idf(self):
        """Calcula o IDF (Inverse Document Frequency) de cada termo na coleção."""
        num_docs = len(self.documentos)
        freq_docs = Counter()

        for doc in self.documentos:
            termos_unicos = set(doc.tokens)
            for t in termos_unicos:
                freq_docs[t] += 1

        for termo, freq in freq_docs.items():
            self.idf[termo] = math.log((num_docs + 1) / (freq + 1)) + 1.0

    def buscar(self, query: str, top_k: int = 3) -> List[Tuple[Documento, float]]:
        """Busca os documentos mais relevantes usando similaridade TF-IDF ponderada."""
        tokens_query = normalizar_texto(query).split()
        tokens_query = [t for t in tokens_query if len(t) > 1 and t not in STOPWORDS]

        if not tokens_query:
            return []

        pontuacoes: List[Tuple[Documento, float]] = []

        for doc in self.documentos:
            tf = Counter(doc.tokens)
            total_tokens = len(doc.tokens) or 1

            score = 0.0
            for t in tokens_query:
                if t in tf:
                    tf_val = tf[t] / total_tokens
                    idf_val = self.idf.get(t, 1.0)
                    score += tf_val * idf_val

                    # Bônus para correspondência no título do documento
                    if t in normalizar_texto(doc.titulo):
                        score += 0.15

            # Bônus específicos para intenções claras
            q_norm = " ".join(tokens_query)
            if any(k in q_norm for k in ["categoriz", "categoria", "extrato", "gasto", "distribui", "supermercado", "combustivel"]) and doc.doc_id == "extrato_transacoes":
                score += 0.5
            if any(k in q_norm for k in ["seguro", "viagem", "schengen", "europa", "medico", "aig"]) and doc.doc_id in ["apolice_seguro_viagem", "cartao_amex_gold"]:
                score += 0.4
            if any(k in q_norm for k in ["cashback", "like", "devolve", "dinheiro"]) and doc.doc_id == "cartao_like_visa":
                score += 0.5
            if any(k in q_norm for k in ["pontos", "milhas", "livelo", "gold", "amex"]) and doc.doc_id == "cartao_amex_gold":
                score += 0.4
            if any(k in q_norm for k in ["historico", "liguei", "atendimento", "chamado", "passado"]) and doc.doc_id == "historico_atendimento":
                score += 0.6

            if score > 0:
                pontuacoes.append((doc, score))

        pontuacoes.sort(key=lambda x: x[1], reverse=True)
        return pontuacoes[:top_k]

    def buscar_contexto(self, query: str, top_k: int = 3) -> str:
        """Retorna uma string consolidada e formatada com os blocos mais relevantes para injetar no prompt."""
        resultados = self.buscar(query, top_k=top_k)

        # Se não houver correspondência específica, retorne os cartões elegíveis principais e perfil
        if not resultados:
            docs_padrao = [d for d in self.documentos if d.doc_id in ["perfil_cliente", "cartao_amex_gold", "cartao_like_visa"]]
            resultados = [(d, 1.0) for d in docs_padrao[:top_k]]

        blocos = []
        for doc, score in resultados:
            blocos.append(f"### [FONTE: {doc.titulo}]\n{doc.conteudo.strip()}")

        return "\n\n".join(blocos)
