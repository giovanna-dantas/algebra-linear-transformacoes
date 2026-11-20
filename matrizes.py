"""
matrizes.py
-----------
Operações básicas de álgebra linear implementadas "na mão", em Python puro
(sem NumPy). Uma matriz é representada como uma lista de listas, onde cada
sublista é uma LINHA da matriz.

Exemplo: [[1, 2], [3, 4]] representa a matriz  | 1 2 |
                                               | 3 4 |

Conteúdo:
  - produto de matrizes, transposta, determinante (cofatores);
  - matriz INVERSA (eliminação de Gauss-Jordan);
  - autovalores 2x2 (Bhaskara) e 3x3 (equação característica);
  - autovetores como ESPAÇO NULO de (A - λI) (eliminação de Gauss).
"""

import math

from vetores import normalizar

# Tolerância numérica: valores menores que isso são tratados como zero
# (evita resultados como 6.1e-17 no lugar de 0 ao usar seno/cosseno).
EPS = 1e-9


# ----------------------------------------------------------------------------
# Construção e operações elementares
# ----------------------------------------------------------------------------

def identidade(n):
    """Devolve a matriz identidade n x n."""
    # Elemento (i, j) vale 1 quando i == j e 0 caso contrário.
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def dimensoes(A):
    """Devolve (linhas, colunas) de uma matriz."""
    return len(A), len(A[0])


def copiar(A):
    """Cópia independente de uma matriz."""
    return [linha[:] for linha in A]


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


def diferenca_maxima(A, B):
    """Maior diferença (em módulo) entre elementos correspondentes de A e B."""
    return max(abs(a - b) for la, lb in zip(A, B) for a, b in zip(la, lb))


def matrizes_iguais(A, B, tol=1e-6):
    """True se A e B têm os mesmos elementos, a menos de uma tolerância."""
    return diferenca_maxima(A, B) <= tol


# ----------------------------------------------------------------------------
# Determinante, traço e inversa
# ----------------------------------------------------------------------------

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


def inversa(A):
    """
    Matriz inversa por eliminação de Gauss-Jordan.

    Monta a matriz aumentada [A | I] e faz operações elementares nas linhas
    até transformar A em I; no mesmo processo, I vira A⁻¹:
        [A | I]  ->  [I | A⁻¹]
    Usa pivoteamento parcial (escolhe o maior pivô da coluna) para reduzir
    erros de arredondamento. Se algum pivô for ~0, det(A) = 0 e a matriz
    NÃO tem inversa (levanta ValueError).
    """
    n = len(A)
    if n != len(A[0]):
        raise ValueError("só matrizes quadradas têm inversa")
    # Matriz aumentada [A | I].
    aug = [A[i][:] + identidade(n)[i] for i in range(n)]
    for col in range(n):
        # Pivoteamento parcial: linha (a partir de 'col') com maior |elemento|.
        melhor = max(range(col, n), key=lambda i: abs(aug[i][col]))
        if abs(aug[melhor][col]) < 1e-12:
            raise ValueError("matriz singular (det = 0): não existe inversa")
        aug[col], aug[melhor] = aug[melhor], aug[col]
        # Divide a linha do pivô para o pivô valer 1.
        pivo = aug[col][col]
        aug[col] = [x / pivo for x in aug[col]]
        # Zera a coluna 'col' em todas as outras linhas.
        for i in range(n):
            if i != col:
                fator = aug[i][col]
                aug[i] = [a - fator * b for a, b in zip(aug[i], aug[col])]
    # A metade direita da matriz aumentada é a inversa.
    return [linha[n:] for linha in aug]


# ----------------------------------------------------------------------------
# Autovalores e autovetores
# ----------------------------------------------------------------------------

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


def _agrupar_repetidas(raizes, tol=1e-4):
    """
    Raízes repetidas de um polinômio são numericamente sensíveis (erro ~1e-5).
    Raízes que diferem menos que 'tol' são consideradas a MESMA e substituídas
    pela média do grupo (a média é mais precisa: a soma das raízes é exata).
    """
    grupos = []
    for x in raizes:
        for g in grupos:
            if abs(g[0] - x) < tol:
                g.append(x)
                break
        else:
            grupos.append([x])
    resultado = []
    for g in grupos:
        media = sum(g) / len(g)
        resultado += [media + 0.0] * len(g)
    return resultado


def autovalores_3x3(A):
    """
    Autovalores de uma matriz 3x3 pela equação característica (cúbica):
        det(A - λI) = 0  ->  λ³ - tr(A)·λ² + c1·λ - det(A) = 0
    onde c1 é a soma dos três menores principais 2x2 (cofatores da diagonal).

    Método:
      1) toda cúbica real tem ao menos uma raiz REAL r: achada por bisseção
         (o polinômio é negativo em -R e positivo em +R);
      2) divide-se o polinômio por (λ - r) (deflação), sobrando uma equação
         do 2º grau, resolvida por Bhaskara (raízes reais ou complexas).
    """
    tr = tracos(A)
    c1 = ((A[0][0] * A[1][1] - A[0][1] * A[1][0]) +
          (A[0][0] * A[2][2] - A[0][2] * A[2][0]) +
          (A[1][1] * A[2][2] - A[1][2] * A[2][1]))
    det = determinante(A)
    # p(λ) = λ³ + a·λ² + b·λ + c
    a, b, c = -tr, c1, -det

    def p(x):
        """Avalia o polinômio característico (forma de Horner)."""
        return ((x + a) * x + b) * x + c

    # Limite de Cauchy: todas as raízes têm módulo <= R.
    R = 1 + max(abs(a), abs(b), abs(c))
    baixo, alto = -R, R
    for _ in range(200):                        # bisseção
        meio = (baixo + alto) / 2
        if p(meio) > 0:
            alto = meio
        else:
            baixo = meio
    r = (baixo + alto) / 2
    # Deflação: λ³ + aλ² + bλ + c = (λ - r)(λ² + pp·λ + q)
    pp = a + r
    q = b + r * pp
    delta = pp * pp - 4 * q
    escala = 1 + pp * pp + abs(q)
    if delta >= -1e-8 * escala:                 # raízes reais (inclui repetidas)
        s = math.sqrt(max(delta, 0.0))
        raizes = sorted([r, (-pp + s) / 2, (-pp - s) / 2], reverse=True)
        return _agrupar_repetidas(raizes)
    s = math.sqrt(-delta)                       # par de complexos conjugados
    return [r, complex(-pp / 2, s / 2), complex(-pp / 2, -s / 2)]


def autovalores(A):
    """Autovalores de uma matriz 2x2 ou 3x3 (despacha para a função certa)."""
    if len(A) == 2:
        return autovalores_2x2(A)
    if len(A) == 3:
        return autovalores_3x3(A)
    raise NotImplementedError("autovalores só implementados para 2x2 e 3x3")


def espaco_nulo(B, tol=1e-4):
    """
    Base do espaço nulo de B (soluções de B·v = 0) por eliminação de Gauss-Jordan
    (forma escalonada reduzida). Colunas sem pivô são as variáveis LIVRES; cada
    variável livre gera um vetor da base. 'tol' é relativa ao maior elemento de B.
    """
    m, n = dimensoes(B)
    R = copiar(B)
    escala = max(abs(x) for linha in R for x in linha) or 1.0
    limite = tol * escala
    colunas_pivo = []
    linha = 0
    for col in range(n):
        if linha >= m:
            break
        melhor = max(range(linha, m), key=lambda i: abs(R[i][col]))
        if abs(R[melhor][col]) <= limite:
            continue                                # coluna sem pivô -> variável livre
        R[linha], R[melhor] = R[melhor], R[linha]
        pivo = R[linha][col]
        R[linha] = [x / pivo for x in R[linha]]
        for i in range(m):
            if i != linha:
                fator = R[i][col]
                R[i] = [a - fator * b for a, b in zip(R[i], R[linha])]
        colunas_pivo.append(col)
        linha += 1
    base = []
    for livre in (c for c in range(n) if c not in colunas_pivo):
        v = [0.0] * n
        v[livre] = 1.0
        for i, c in enumerate(colunas_pivo):
            v[c] = -R[i][livre]
        base.append(v)
    return base


def autovetores(A, lam):
    """
    Autovetores (normalizados) de A associados ao autovalor REAL 'lam':
    base do espaço nulo de (A - λI), isto é, soluções de (A - λI)·v = 0.
    Devolve uma lista de vetores (vazia se λ for complexo: não há direção real).
    O sinal é escolhido de modo que a primeira componente não nula seja positiva.
    """
    if isinstance(lam, complex):
        return []
    n = len(A)
    B = [[A[i][j] - (lam if i == j else 0.0) for j in range(n)] for i in range(n)]
    vetores = []
    for v in espaco_nulo(B):
        v = normalizar(v)
        primeiro = next(x for x in v if abs(x) > 1e-9)
        if primeiro < 0:
            v = tuple(-x for x in v)
        vetores.append(tuple(x + 0.0 for x in v))
    return vetores


def autovalores_distintos(lista, tol=1e-4):
    """Agrupa autovalores repetidos: devolve [(valor, multiplicidade), ...]."""
    grupos = []
    for lam in lista:
        for g in grupos:
            if abs(g[0] - lam) < tol:
                g[1] += 1
                break
        else:
            grupos.append([lam, 1])
    return [(g[0], g[1]) for g in grupos]


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


# ----------------------------------------------------------------------------
# Formatação (só para exibição)
# ----------------------------------------------------------------------------

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
        return f"{x.real + 0.0:.{casas}f} {'+' if x.imag >= 0 else '-'} {abs(x.imag):.{casas}f}i"
    return f"{x + 0.0:.{casas}f}"
