"""
matrizes.py
-----------
Operações básicas de álgebra linear implementadas "na mão", em Python puro
(sem NumPy). Uma matriz é representada como uma lista de listas, onde cada
sublista é uma LINHA da matriz.

Exemplo: [[1, 2], [3, 4]] representa a matriz  | 1 2 |
                                               | 3 4 |
"""

import math

# Tolerância numérica: valores menores que isso são tratados como zero
# (evita resultados como 6.1e-17 no lugar de 0 ao usar seno/cosseno).
EPS = 1e-9


def identidade(n):
    """Devolve a matriz identidade n x n."""
    # Elemento (i, j) vale 1 quando i == j e 0 caso contrário.
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def dimensoes(A):
    """Devolve (linhas, colunas) de uma matriz."""
    return len(A), len(A[0])


def multiplicar(A, B):
    """
    Produto matricial A·B.
    O elemento (i, j) do resultado é o produto escalar da linha i de A
    pela coluna j de B:  C[i][j] = soma_k A[i][k] * B[k][j].
    """
    m, n = dimensoes(A)
    n2, p = dimensoes(B)
    # O produto só existe se o número de colunas de A for igual ao de linhas de B.
    if n != n2:
        raise ValueError("Dimensões incompatíveis para multiplicação: "
                         f"{m}x{n} por {n2}x{p}")
    C = [[0.0 for _ in range(p)] for _ in range(m)]
    for i in range(m):          # percorre as linhas de A
        for j in range(p):      # percorre as colunas de B
            soma = 0.0
            for k in range(n):  # produto escalar linha i · coluna j
                soma += A[i][k] * B[k][j]
            C[i][j] = soma
    return C


def multiplicar_varias(lista):
    """Multiplica uma lista de matrizes na ordem dada: M0·M1·M2·..."""
    resultado = lista[0]
    for M in lista[1:]:
        resultado = multiplicar(resultado, M)
    return resultado


def transposta(A):
    """Devolve a transposta de A (troca linhas por colunas)."""
    m, n = dimensoes(A)
    return [[A[i][j] for i in range(m)] for j in range(n)]


def submatriz(A, linha, coluna):
    """Remove a 'linha' e a 'coluna' de A (usada no cálculo de cofatores)."""
    return [[A[i][j] for j in range(len(A[0])) if j != coluna]
            for i in range(len(A)) if i != linha]


def determinante(A):
    """
    Determinante por expansão de Laplace (cofatores) ao longo da 1ª linha:
        det(A) = soma_j (-1)^(0+j) * A[0][j] * det(submatriz sem linha 0 e coluna j)
    Funciona para qualquer matriz quadrada (recursivo).
    """
    n = len(A)
    # Caso base: matriz 1x1.
    if n == 1:
        return A[0][0]
    # Caso base: matriz 2x2 -> ad - bc.
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    total = 0.0
    for j in range(n):
        sinal = (-1) ** j                       # sinal do cofator
        total += sinal * A[0][j] * determinante(submatriz(A, 0, j))
    return total


def tracos(A):
    """Traço de A: soma dos elementos da diagonal principal."""
    return sum(A[i][i] for i in range(len(A)))


def autovalores_2x2(A):
    """
    Autovalores de uma matriz 2x2 pela equação característica:
        det(A - λI) = 0   ->   λ² - tr(A)·λ + det(A) = 0
    Devolve uma lista de números (reais) ou de complexos, quando
    o discriminante é negativo (ex.: rotações).
    """
    tr = tracos(A)
    det = determinante(A)
    delta = tr * tr - 4 * det                   # discriminante de Bhaskara
    if delta >= -EPS:
        delta = max(delta, 0.0)
        raiz = math.sqrt(delta)
        return [(tr + raiz) / 2, (tr - raiz) / 2]
    # Discriminante negativo: autovalores complexos conjugados.
    raiz = math.sqrt(-delta)
    return [complex(tr / 2, raiz / 2), complex(tr / 2, -raiz / 2)]


def autovetor_2x2(A, lam):
    """
    Autovetor (normalizado) de A 2x2 associado ao autovalor REAL 'lam',
    resolvendo (A - λI)v = 0.  Devolve None se λ for complexo.
    """
    if isinstance(lam, complex):
        return None
    a, b = A[0][0], A[0][1]
    c, d = A[1][0], A[1][1]
    # Da 1ª linha:  (a-λ)x + b·y = 0   ->  v = (b, λ-a)   (se b != 0)
    if abs(b) > EPS:
        v = (b, lam - a)
    # Da 2ª linha:  c·x + (d-λ)y = 0   ->  v = (λ-d, c)   (se c != 0)
    elif abs(c) > EPS:
        v = (lam - d, c)
    # Matriz diagonal: os autovetores são os eixos coordenados.
    else:
        v = (1.0, 0.0) if abs(a - lam) < EPS else (0.0, 1.0)
    norma = math.hypot(v[0], v[1])
    return (v[0] / norma, v[1] / norma)


def limpar(A, casas=6):
    """Arredonda os elementos e troca -0.0 por 0.0 (só para exibição)."""
    return [[round(x, casas) + 0.0 for x in linha] for linha in A]


def formatar_matriz(A, casas=3):
    """Devolve uma string com a matriz em linhas alinhadas, ex.: '[ 1.000  0.000 ]'."""
    textos = [[f"{x:.{casas}f}" for x in linha] for linha in limpar(A, casas)]
    largura = max(len(t) for linha in textos for t in linha)
    linhas = ["[ " + "  ".join(t.rjust(largura) for t in linha) + " ]"
              for linha in textos]
    return "\n".join(linhas)


def formatar_numero(x, casas=4):
    """Formata número real ou complexo para impressão."""
    if isinstance(x, complex):
        return f"{x.real:.{casas}f} {'+' if x.imag >= 0 else '-'} {abs(x.imag):.{casas}f}i"
    return f"{x:.{casas}f}"
