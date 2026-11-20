"""
relatorio.py
------------
Gera o relatório de execução em texto: matrizes individuais, matrizes
intermediárias (acumuladas), matriz composta final, determinante, verificação
de área/volume, matriz INVERSA, autovalores/autovetores, vértices antes/depois
e uma interpretação em português.
"""

from matrizes import (formatar_matriz, determinante, autovalores, autovalores_distintos,
                      autovetores, formatar_numero, inversa, multiplicar, identidade,
                      diferenca_maxima, EPS)
from transformacoes import (compor, compor_inversa, parte_linear, aplicar_matriz,
                            vetor_translacao)
from objetos import medida_assinada, vertices_formatados

LIMITE_VERTICES = 12      # quantos vértices listar (objetos de texto têm centenas)


def indentar(texto, espacos=4):
    """Adiciona recuo a cada linha de um texto de várias linhas."""
    return "\n".join(" " * espacos + linha for linha in texto.split("\n"))


def analisar_matriz(M):
    """
    Devolve um dicionário com det e autovalores/autovetores da parte linear A
    (2x2 ou 3x3) da matriz homogênea M.
    """
    A = parte_linear(M)
    lams = autovalores(A)
    grupos = autovalores_distintos(lams)
    return {"A": A, "det": determinante(A), "det_homogenea": determinante(M),
            "autovalores": lams, "grupos": grupos,
            "autovetores": {i: autovetores(A, lam) for i, (lam, _) in enumerate(grupos)}}


def interpretar(obj, info, M):
    """Lista de frases interpretando det, autovalores e translação."""
    det, dim = info["det"], obj.dim
    medida = "área" if dim == 2 else "volume"
    frases = []
    if abs(det) < EPS:
        frases.append(f"det = 0: a transformação ACHATA o objeto (perde uma dimensão) e "
                      f"não pode ser desfeita (não existe M⁻¹).")
    else:
        frases.append(f"|det| = {abs(det):.4f}: a {medida} do objeto é multiplicada por {abs(det):.4f}"
                      + (" (aumenta)." if abs(det) > 1 + 1e-9 else
                         " (diminui)." if abs(det) < 1 - 1e-9 else " (não muda)."))
        frases.append("det > 0: a orientação é preservada." if det > 0 else
                      "det < 0: a orientação é INVERTIDA (há uma reflexão no meio da composição).")
    complexos = [l for l in info["autovalores"] if isinstance(l, complex)]
    if complexos:
        frases.append("Há autovalores complexos: existe um componente de ROTAÇÃO "
                      "(no plano, nenhuma direção real é mantida)." if dim == 2 else
                      "Há um par de autovalores complexos: existe um componente de ROTAÇÃO "
                      "em torno do eixo dado pelo autovetor do autovalor real.")
    else:
        frases.append("Todos os autovalores são reais: não há rotação líquida; as direções dos "
                      "autovetores são apenas esticadas/encolhidas (setas/retas verdes nos gráficos).")
    t = vetor_translacao(M)
    if any(abs(c) > EPS for c in t):
        frases.append("A última coluna (" + ", ".join(f"{c:.4f}" for c in t) +
                      ") é o deslocamento da origem: translação resultante.")
    return frases


def gerar_relatorio(obj, sequencia):
    """Monta e devolve (texto, M): o relatório completo e a matriz composta."""
    M, passos = compor(sequencia)
    if len(M) - 1 != obj.dim:
        raise ValueError(f"A sequência é {len(M) - 1}D, mas o objeto é {obj.dim}D")
    Vf = aplicar_matriz(M, obj.V)
    final = obj.com_vertices(Vf)
    info = analisar_matriz(M)
    medida = "área" if obj.dim == 2 else "volume"

    L = []   # lista de linhas do relatório
    L.append("=" * 68)
    L.append(f"RELATÓRIO DE EXECUÇÃO - TRANSFORMAÇÕES LINEARES {obj.dim}D")
    L.append("=" * 68)
    L.append(f"Objeto: {obj.nome}")
    L.append(f"Matriz de vértices V: {obj.dim} x {obj.n_vertices()} "
             f"({obj.n_vertices()} vértices, {len(obj.faces)} faces)")
    L.append(f"Coordenadas homogêneas: matrizes {obj.dim + 1}x{obj.dim + 1}")
    L.append("")
    L.append("1) SEQUÊNCIA APLICADA (na ordem de aplicação)")
    for i, p in enumerate(passos, 1):
        L.append(f"  T{i}: {p['descricao']}")
    L.append("")
    L.append(f"2) MATRIZES INDIVIDUAIS (coordenadas homogêneas {obj.dim + 1}x{obj.dim + 1})")
    for i, p in enumerate(passos, 1):
        L.append(f"  T{i} = {p['descricao']}")
        L.append(indentar(formatar_matriz(p["matriz"])))
    L.append("")
    L.append("3) MATRIZES INTERMEDIÁRIAS (acumuladas)")
    for i, p in enumerate(passos, 1):
        nome = "M1 = T1" if i == 1 else f"M{i} = T{i}·M{i - 1}"
        L.append(f"  {nome}")
        L.append(indentar(formatar_matriz(p["acumulada"])))
    L.append("")
    L.append("4) MATRIZ COMPOSTA FINAL")
    produto = "·".join(f"T{i}" for i in range(len(passos), 0, -1))
    L.append(f"  M = {produto}")
    L.append(indentar(formatar_matriz(M)))
    L.append("")
    L.append("5) PROPRIEDADES DA PARTE LINEAR A (bloco superior esquerdo de M)")
    L.append(indentar(formatar_matriz(info["A"])))
    L.append(f"  det(A) = {info['det']:.4f}   (fator de variação de {medida})")
    L.append(f"  det(M) = {info['det_homogenea']:.4f}   (igual a det(A), pois a última linha é 0 ... 0 1)")
    antes, depois = medida_assinada(obj), medida_assinada(final)
    L.append(f"  {medida} (soma com sinal) antes  = {antes:.4f}")
    L.append(f"  {medida} (soma com sinal) depois = {depois:.4f}")
    L.append(f"  det(A) · {medida} antes          = {info['det'] * antes:.4f}   "
             f"-> {'confere' if abs(depois - info['det'] * antes) < 1e-6 * max(1, abs(depois)) else 'NÃO confere'}")
    for idx, (lam, mult) in enumerate(info["grupos"]):
        rot = f" (multiplicidade {mult})" if mult > 1 else ""
        vecs = info["autovetores"][idx]
        if isinstance(lam, complex):
            L.append(f"  autovalor λ = {formatar_numero(lam)}{rot}  (complexo: sem direção real invariante)")
        else:
            textos = "; ".join("(" + ", ".join(f"{c:.4f}" for c in v) + ")" for v in vecs)
            L.append(f"  autovalor λ = {formatar_numero(lam)}{rot}  autovetor(es) ≈ {textos}")
    L.append("")
    L.append("6) MATRIZ INVERSA (desfazer a transformação)")
    if abs(info["det_homogenea"]) < EPS:
        L.append("  det = 0: M não é invertível (a transformação perde informação).")
    else:
        Minv = inversa(M)                                  # Gauss-Jordan
        L.append("  M⁻¹ (eliminação de Gauss-Jordan):")
        L.append(indentar(formatar_matriz(Minv)))
        erro_I = diferenca_maxima(multiplicar(M, Minv), identidade(len(M)))
        L.append(f"  Verificação M·M⁻¹ = I: erro máximo = {erro_I:.2e}")
        try:
            Minv2 = compor_inversa(sequencia)              # T1⁻¹·T2⁻¹·...·Tn⁻¹
            L.append(f"  M⁻¹ = T1⁻¹·...·Tn⁻¹ (produto das inversas): diferença máxima = "
                     f"{diferenca_maxima(Minv, Minv2):.2e}")
        except ValueError:
            pass
        Vr = aplicar_matriz(Minv, Vf)
        L.append(f"  M⁻¹ aplicada ao objeto final recupera o original: erro máximo nos "
                 f"vértices = {diferenca_maxima(Vr, obj.V):.2e}")
    L.append("")
    L.append("7) VÉRTICES ANTES E DEPOIS" +
             (f" (primeiros {LIMITE_VERTICES} de {obj.n_vertices()})"
              if obj.n_vertices() > LIMITE_VERTICES else ""))
    a = vertices_formatados(obj, LIMITE_VERTICES)
    d = vertices_formatados(final, LIMITE_VERTICES)
    for (va, vd) in zip(a, d):
        L.append(f"  {str(va):>26}  ->  {vd}")
    L.append("")
    L.append("8) INTERPRETAÇÃO")
    for frase in interpretar(obj, info, M):
        L.append(f"  - {frase}")
    L.append("")
    return "\n".join(L), M
