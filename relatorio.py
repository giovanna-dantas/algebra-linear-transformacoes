"""
relatorio.py
------------
Gera o relatório de execução em texto: matrizes
individuais, matrizes intermediárias (acumuladas), matriz composta final,
determinante, autovalores/autovetores e vértices antes/depois.
"""

from matrizes import (formatar_matriz, determinante, autovalores_2x2,
                      autovetor_2x2, formatar_numero)
from transformacoes import compor, parte_linear, aplicar, vertices_formatados


def indentar(texto, espacos=4):
    """Adiciona recuo a cada linha de um texto de várias linhas."""
    return "\n".join(" " * espacos + linha for linha in texto.split("\n"))


def analisar_matriz(M):
    """
    Devolve um dicionário com det, traço-relacionados e autovalores/autovetores
    da parte linear 2x2 da matriz homogênea M.
    """
    A = parte_linear(M)
    autovalores = autovalores_2x2(A)
    autovetores = [autovetor_2x2(A, lam) for lam in autovalores]
    return {"A": A, "det": determinante(A), "det_homogenea": determinante(M),
            "autovalores": autovalores, "autovetores": autovetores}


def gerar_relatorio(nome_objeto, contornos, sequencia):
    """Monta e devolve o texto completo do relatório de execução."""
    M, passos = compor(sequencia)
    finais = aplicar(M, contornos)
    info = analisar_matriz(M)

    L = []   # lista de linhas do relatório
    L.append("=" * 64)
    L.append("RELATÓRIO DE EXECUÇÃO - TRANSFORMAÇÕES LINEARES 2D")
    L.append("=" * 64)
    L.append(f"Objeto: {nome_objeto}")
    L.append(f"Número de vértices: {len(vertices_formatados(contornos))}")
    L.append("")
    L.append("1) SEQUÊNCIA APLICADA (na ordem de aplicação)")
    for i, p in enumerate(passos, 1):
        L.append(f"  T{i}: {p['descricao']}")
    L.append("")
    L.append("2) MATRIZES INDIVIDUAIS (coordenadas homogêneas 3x3)")
    for i, p in enumerate(passos, 1):
        L.append(f"  T{i} = {p['descricao']}")
        L.append(indentar(formatar_matriz(p["matriz"])))
    L.append("")
    L.append("3) MATRIZES INTERMEDIÁRIAS (acumuladas)")
    for i, p in enumerate(passos, 1):
        if i == 1:
            nome = "M1 = T1"
        else:
            nome = f"M{i} = T{i}·M{i-1}"
        L.append(f"  {nome}")
        L.append(indentar(formatar_matriz(p["acumulada"])))
    L.append("")
    L.append("4) MATRIZ COMPOSTA FINAL")
    produto = "·".join(f"T{i}" for i in range(len(passos), 0, -1))
    L.append(f"  M = {produto}")
    L.append(indentar(formatar_matriz(M)))
    L.append("")
    L.append("5) PROPRIEDADES DA PARTE LINEAR A (bloco 2x2 de M)")
    L.append(indentar(formatar_matriz(info["A"])))
    L.append(f"  det(A) = {info['det']:.4f}   (fator de variação de área)")
    if info["det"] < 0:
        L.append("  det(A) < 0: a transformação inverte a orientação (reflexão).")
    L.append(f"  det(M) = {info['det_homogenea']:.4f}   (igual a det(A), pois a última linha é 0 0 1)")
    for lam, v in zip(info["autovalores"], info["autovetores"]):
        if v is None:
            L.append(f"  autovalor λ = {formatar_numero(lam)}  (complexo: sem direção real invariante)")
        else:
            L.append(f"  autovalor λ = {formatar_numero(lam)}  autovetor ≈ ({v[0]:.4f}, {v[1]:.4f})")
    L.append("")
    L.append("6) VÉRTICES ANTES E DEPOIS")
    antes = vertices_formatados(contornos)
    depois = vertices_formatados(finais)
    for (a, d) in zip(antes, depois):
        L.append(f"  {str(a):>18}  ->  {d}")
    L.append("")
    return "\n".join(L), M
