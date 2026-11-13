"""
transformacoes.py
-----------------
Matrizes de transformação geométrica 2D em coordenadas HOMOGÊNEAS (3x3) e
funções para compor e aplicar essas transformações a um objeto.

Convenção: um ponto (x, y) é a coluna  [x, y, 1]^T.  Assim a translação,
que NÃO é linear em R², passa a ser uma multiplicação de matrizes em R³.

Forma geral da matriz homogênea:    | a  b  tx |
                                    | c  d  ty |    onde [[a,b],[c,d]] é a parte linear
                                    | 0  0  1  |
"""

import math
from matrizes import identidade, multiplicar, limpar


# 1) Matrizes elementares

def rotacao(theta_graus):
    """Rotação anti-horária de θ graus em torno da origem."""
    t = math.radians(theta_graus)          # converte graus -> radianos
    c, s = math.cos(t), math.sin(t)
    return [[c, -s, 0.0],
            [s,  c, 0.0],
            [0.0, 0.0, 1.0]]


def escala(sx, sy):
    """Escala por sx na horizontal e sy na vertical (valor negativo = reflexão)."""
    return [[sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0]]


def cisalhamento(kx, ky):
    """
    Cisalhamento (shear): x' = x + kx·y   e   y' = y + ky·x.
    kx desliza as linhas horizontais; ky desliza as verticais.
    """
    return [[1.0, kx, 0.0],
            [ky, 1.0, 0.0],
            [0.0, 0.0, 1.0]]


def translacao(tx, ty):
    """Translação pelo vetor (tx, ty) — só existe em coordenadas homogêneas."""
    return [[1.0, 0.0, tx],
            [0.0, 1.0, ty],
            [0.0, 0.0, 1.0]]


def construir(tipo, parametros):
    """
    Constrói a matriz a partir do nome da transformação e da lista de parâmetros.
    Tipos aceitos: 'rotacao', 'escala', 'cisalhamento', 'translacao'.
    """
    if tipo == "rotacao":
        return rotacao(parametros[0])
    if tipo == "escala":
        return escala(parametros[0], parametros[1])
    if tipo == "cisalhamento":
        return cisalhamento(parametros[0], parametros[1])
    if tipo == "translacao":
        return translacao(parametros[0], parametros[1])
    raise ValueError(f"Transformação desconhecida: {tipo}")


def descrever(tipo, parametros):
    """Texto curto descrevendo a transformação (usado nos relatórios)."""
    p = parametros
    if tipo == "rotacao":
        return f"Rotação de {p[0]:g}°"
    if tipo == "escala":
        return f"Escala (sx={p[0]:g}, sy={p[1]:g})"
    if tipo == "cisalhamento":
        return f"Cisalhamento (kx={p[0]:g}, ky={p[1]:g})"
    return f"Translação (tx={p[0]:g}, ty={p[1]:g})"


# 2) Composição

def compor(sequencia):
    """
    Compõe uma sequência de transformações aplicadas NA ORDEM dada.

    Se a sequência é T1, T2, T3 (T1 aplicada primeiro), a matriz composta é
        M = T3 · T2 · T1
    pois o ponto fica à direita:  p' = T3·(T2·(T1·p)).

    Devolve (M, passos), onde 'passos' é a lista de dicionários com cada matriz
    individual e a matriz ACUMULADA após aquele passo (matrizes intermediárias).
    """
    acumulada = identidade(3)
    passos = []
    for tipo, parametros in sequencia:
        T = construir(tipo, parametros)
        # A nova transformação entra à ESQUERDA do que já foi acumulado.
        acumulada = multiplicar(T, acumulada)
        passos.append({
            "descricao": descrever(tipo, parametros),
            "matriz": T,
            "acumulada": [linha[:] for linha in acumulada],
        })
    return acumulada, passos


def parte_linear(M):
    """Extrai o bloco 2x2 (a b; c d) de uma matriz homogênea 3x3."""
    return [[M[0][0], M[0][1]], [M[1][0], M[1][1]]]


# 3) Aplicação a um objeto

def matriz_de_vertices(contornos):
    """
    Junta todos os contornos numa única matriz 2 x N de vértices
    (cada COLUNA é um vértice).
    """
    xs, ys = [], []
    for contorno in contornos:
        for (x, y) in contorno:
            xs.append(x)
            ys.append(y)
    return [xs, ys]


def aplicar(M, contornos):
    """
    Aplica a matriz homogênea M (3x3) a todos os vértices do objeto.
    Cada contorno é uma lista de pontos (x, y); devolve a nova lista de contornos.
    """
    novos = []
    for contorno in contornos:
        novo = []
        for (x, y) in contorno:
            # Produto M · [x, y, 1]^T feito termo a termo (linhas 0 e 1).
            xn = M[0][0] * x + M[0][1] * y + M[0][2]
            yn = M[1][0] * x + M[1][1] * y + M[1][2]
            novo.append((xn, yn))
        novos.append(novo)
    return novos


def vertices_formatados(contornos):
    """Lista de textos '(x, y)' com todos os vértices (para relatórios)."""
    saida = []
    for contorno in contornos:
        for (x, y) in contorno:
            saida.append((round(x, 4) + 0.0, round(y, 4) + 0.0))
    return saida
