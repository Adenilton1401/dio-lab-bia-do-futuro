"""
Teste de verificação do SimpleRAG e integração com o AgenteLis.
"""

from src.rag import SimpleRAG
from src.agente import AgenteLis

def test_rag():
    rag = SimpleRAG()
    print("=" * 60)
    print("TESTE 1: Categorização de Gastos")
    ctx_gastos = rag.buscar_contexto("Você pode categorizar os meus gastos?")
    assert "Supermercado" in ctx_gastos or "supermercado" in ctx_gastos.lower()
    assert "Combustivel" in ctx_gastos or "combustivel" in ctx_gastos.lower()
    print("-> OK! Categorias encontradas no contexto:")
    for linha in ctx_gastos.splitlines():
        if "*" in linha:
            print("  ", linha)

    print("\n" + "=" * 60)
    print("TESTE 2: Seguro Viagem Europa / Schengen")
    ctx_seguro = rag.buscar_contexto("Qual cartão tem seguro para Europa e Acordo de Schengen?")
    assert "Schengen" in ctx_seguro or "schengen" in ctx_seguro.lower()
    assert "Amex" in ctx_seguro or "Gold" in ctx_seguro
    print("-> OK! Apólice Schengen e Amex Gold recuperados:")
    for linha in ctx_seguro.splitlines()[:10]:
        print("  ", linha)

    print("\n" + "=" * 60)
    print("TESTE 3: Cashback no Supermercado e Combustível")
    ctx_cashback = rag.buscar_contexto("Qual opção me dá cashback no supermercado?")
    assert "Like" in ctx_cashback or "cashback" in ctx_cashback.lower()
    print("-> OK! Bradesco Like recuperado:")
    for linha in ctx_cashback.splitlines()[:6]:
        print("  ", linha)

    print("\n" + "=" * 60)
    print("TESTE 4: Histórico de Atendimentos Anteriores")
    ctx_hist = rag.buscar_contexto("Quando liguei ou falei sobre anuidade no passado?")
    assert "Tarifa de Anuidade" in ctx_hist or "Classic" in ctx_hist
    print("-> OK! Histórico recuperado:")
    for linha in ctx_hist.splitlines()[:6]:
        print("  ", linha)

    print("\n" + "=" * 60)
    print("TESTE 5: Contexto Injetado no AgenteLis")
    agente = AgenteLis()
    ctx_agente = agente.construir_contexto_injetado("Você pode categorizar os meus gastos?")
    print("Tamanho do contexto gerado (caracteres):", len(ctx_agente))
    assert "CATEGORIA" in ctx_agente and "Supermercado" in ctx_agente
    print("-> OK! O Agente agora injeta o extrato categorizado quando o cliente pergunta sobre gastos!")

    print("\nTODOS OS 5 TESTES DO RAG PASSARAM COM SUCESSO!")

    # =========================================================================
    # 🔍 DEMONSTRAÇÃO / INSPEÇÃO DETALHADA DO PROMPT E DO RAG NO TERMINAL:
    # Para exibir no terminal o que é estático, o que veio do RAG e o prompt completo,
    # basta DESCOMENTAR a linha desejada abaixo:
    # =========================================================================
    # agente.exibir_inspecao_prompt("Qual cartão tem sala VIP e seguro para Europa?")
    # agente.exibir_inspecao_prompt("Você pode categorizar os meus gastos?")

if __name__ == "__main__":
    test_rag()
