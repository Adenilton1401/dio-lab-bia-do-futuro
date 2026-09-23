"""
Módulo de carregamento e consolidação de dados da Base de Conhecimento da Lis.
Lê os arquivos em data/ e calcula métricas financeiras essenciais para o agente.
"""

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List


class DataLoader:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Caminho relativo padrão para a pasta data na raiz do projeto
            base_path = Path(__file__).resolve().parent.parent
            self.data_dir = base_path / "data"
        else:
            self.data_dir = Path(data_dir)

    def carregar_cartoes(self) -> List[Dict[str, Any]]:
        """Carrega o catálogo de cartões de crédito."""
        caminho = self.data_dir / "cartoes_credito.json"
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def carregar_perfil_cliente(self) -> Dict[str, Any]:
        """Carrega os dados e perfil do cliente."""
        caminho = self.data_dir / "perfil_cliente.json"
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def carregar_transacoes(self) -> List[Dict[str, Any]]:
        """Carrega as transações do extrato."""
        caminho = self.data_dir / "transacoes.csv"
        transacoes = []
        with open(caminho, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["valor"] = float(row["valor"])
                transacoes.append(row)
        return transacoes

    def carregar_historico_atendimento(self) -> List[Dict[str, Any]]:
        """Carrega os atendimentos anteriores."""
        caminho = self.data_dir / "historico_atendimento.csv"
        historico = []
        with open(caminho, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                historico.append(row)
        return historico

    def obter_resumo_financeiro(self) -> Dict[str, Any]:
        """Calcula o resumo consolidado de gastos e oportunidades do cliente com base na média mensal."""
        perfil = self.carregar_perfil_cliente()
        transacoes = self.carregar_transacoes()
        cartoes = self.carregar_cartoes()

        meses_unicos = set(t["data"][:7] for t in transacoes)
        num_meses = len(meses_unicos) or 1

        total_gastos_acumulado = sum(t["valor"] for t in transacoes)
        gastos_credito_acumulado = sum(t["valor"] for t in transacoes if t.get("metodo_pagamento") == "credito")
        gastos_debito_acumulado = sum(t["valor"] for t in transacoes if t.get("metodo_pagamento") == "debito")

        # Médias mensais de gastos
        media_gastos_mensal = total_gastos_acumulado / num_meses
        media_credito_mensal = gastos_credito_acumulado / num_meses
        media_debito_mensal = gastos_debito_acumulado / num_meses

        # Gastos médios mensais por categoria no débito (potenciais de migração)
        debito_por_categoria = {}
        for t in transacoes:
            if t.get("metodo_pagamento") == "debito":
                cat = t["categoria"]
                debito_por_categoria[cat] = debito_por_categoria.get(cat, 0.0) + (t["valor"] / num_meses)

        # Análise de cartões elegíveis pela renda e média mensal de gastos
        renda = perfil.get("renda_mensal", 0.0)
        cartoes_elegiveis = []
        for c in cartoes:
            if renda >= c.get("renda_minima", 0.0):
                isencao = c.get("politica_isencao", {})
                min_100 = isencao.get("gasto_minimo_mensal_100")
                isencao_atingivel = (min_100 is not None) and (media_gastos_mensal >= min_100)
                cartoes_elegiveis.append({
                    "id": c["id"],
                    "nome": c["nome"],
                    "categoria": c["categoria"],
                    "anuidade_mensal": c["anuidade"]["valor_parcela"],
                    "isencao_100_atingivel": isencao_atingivel,
                    "regra_isencao": isencao.get("regra"),
                    "programa": c["programa_recompensas"]["tipo"]
                })

        return {
            "cliente_nome": perfil.get("nome"),
            "renda_mensal": renda,
            "total_gastos": media_gastos_mensal,
            "gastos_credito": media_credito_mensal,
            "gastos_debito": media_debito_mensal,
            "total_acumulado_periodo": total_gastos_acumulado,
            "meses_analisados": num_meses,
            "debito_por_categoria": debito_por_categoria,
            "anuidade_atual_paga_ano": perfil.get("cartao_atual", {}).get("anuidade_anual_paga", 0.0),
            "cartoes_elegiveis": cartoes_elegiveis
        }


if __name__ == "__main__":
    loader = DataLoader()
    resumo = loader.obter_resumo_financeiro()
    print("Resumo financeiro carregado com sucesso:")
    print(json.dumps(resumo, indent=2, ensure_ascii=False))
