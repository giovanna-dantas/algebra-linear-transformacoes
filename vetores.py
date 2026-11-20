"""
vetores.py
----------
Operações com VETORES implementadas "na mão" (sem NumPy), para a parte de
Vetores e Geometria Analítica da disciplina.

Um vetor é uma tupla ou lista de números: (x, y) no plano e (x, y, z) no espaço.
Estas funções aparecem em vários pontos do projeto:
  - fonte.py ........ transforma cada traço de letra em um retângulo
                      (vetor diretor, vetor normal, norma);
  - graficos.py ..... iluminação das faces 3D (vetor normal pelo produto
                      vetorial e produto escalar com a direção da luz);
  - objetos.py ...... volume de sólidos pelo produto misto;
  - transformacoes.py  rotação em torno de um eixo arbitrário (Rodrigues).
"""

import math

# Tolerância numérica: valores menores que isso são tratados como zero.
EPS = 1e-9


def somar(u, v):
    """Soma de vetores: u + v (componente a componente)."""
    return tuple(a + b for a, b in zip(u, v))


def subtrair(u, v):
    """Diferença de vetores: u - v. Também é o vetor que vai do ponto v ao ponto u."""
    return tuple(a - b for a, b in zip(u, v))


def multiplicar_por_escalar(k, u):
    """Produto de um escalar k por um vetor u: k·u."""
    return tuple(k * a for a in u)


def produto_escalar(u, v):
    """
    Produto escalar (interno): u·v = u1·v1 + u2·v2 + ...
    Geometricamente u·v = |u|·|v|·cos(ângulo entre u e v).
    """
    return sum(a * b for a, b in zip(u, v))


def norma(u):
    """Norma (comprimento) de u: |u| = raiz( u·u )."""
    return math.sqrt(produto_escalar(u, u))


def normalizar(u):
    """Vetor unitário na direção de u: u / |u|. Erro se u for o vetor nulo."""
    n = norma(u)
    if n < EPS:
        raise ValueError("não é possível normalizar o vetor nulo")
    return tuple(a / n for a in u)


def produto_vetorial(u, v):
    """
    Produto vetorial u × v (só existe em R³). O resultado é perpendicular a
    u e a v, e |u × v| é a área do paralelogramo formado por eles.
    Fórmula (determinante simbólico com i, j, k):
        u × v = (u2·v3 - u3·v2,  u3·v1 - u1·v3,  u1·v2 - u2·v1)
    """
    return (u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0])


def produto_misto(u, v, w):
    """
    Produto misto [u, v, w] = u · (v × w).
    Em módulo, é o volume do paralelepípedo formado por u, v e w;
    dividido por 6 dá o volume do tetraedro correspondente.
    """
    return produto_escalar(u, produto_vetorial(v, w))


def perpendicular_2d(u):
    """
    Vetor perpendicular a u = (x, y) no plano, obtido girando u de +90°:
    (x, y) -> (-y, x). Satisfaz u·perpendicular(u) = 0.
    """
    return (-u[1], u[0])


def angulo_entre(u, v):
    """Ângulo (em graus) entre u e v:  cos(θ) = u·v / (|u|·|v|)."""
    c = produto_escalar(u, v) / (norma(u) * norma(v))
    c = max(-1.0, min(1.0, c))          # evita erro de arredondamento fora de [-1, 1]
    return math.degrees(math.acos(c))


def projecao(u, v):
    """Projeção ortogonal de u sobre v:  proj_v(u) = (u·v / v·v) · v."""
    k = produto_escalar(u, v) / produto_escalar(v, v)
    return multiplicar_por_escalar(k, v)
