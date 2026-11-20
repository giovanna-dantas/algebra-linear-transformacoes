"""
transformacoes.py
-----------------
Matrizes de transformação geométrica em coordenadas HOMOGÊNEAS e funções
para compor e aplicar essas transformações a um objeto.

  - 2D: matrizes 3x3.  Um ponto (x, y) é a coluna [x, y, 1]^T.
  - 3D: matrizes 4x4.  Um ponto (x, y, z) é a coluna [x, y, z, 1]^T.

A translação NÃO é linear (move a origem), mas vira uma multiplicação de
matrizes quando acrescentamos a coordenada homogênea 1.

Forma geral (2D):   | a  b  tx |        Forma geral (3D):  | A(3x3)  t |
                    | c  d  ty |                           |  0 0 0  1 |
                    | 0  0  1  |
onde A é a parte LINEAR (rotação, escala, cisalhamento) e t é a translação.

Convenção: pontos são vetores COLUNA, então a sequência T1, T2, ..., Tn
(T1 aplicada primeiro) tem matriz composta  M = Tn · ... · T2 · T1.
"""

import math

from matrizes import identidade, multiplicar, multiplicar_varias, inversa
from vetores import normalizar


# ----------------------------------------------------------------------------
# 1) Matrizes elementares 2D (3x3)
# ----------------------------------------------------------------------------

def rotacao(theta_graus):
    """Rotação anti-horária de θ graus em torno da origem (2D)."""
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


# ----------------------------------------------------------------------------
# 2) Matrizes elementares 3D (4x4)
# ----------------------------------------------------------------------------

def rotacao_x(theta_graus):
    """Rotação de θ em torno do eixo x (regra da mão direita): x fica fixo."""
    t = math.radians(theta_graus)
    c, s = math.cos(t), math.sin(t)
    return [[1.0, 0.0, 0.0, 0.0],
            [0.0,  c,  -s, 0.0],
            [0.0,  s,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0]]


def rotacao_y(theta_graus):
    """Rotação de θ em torno do eixo y (regra da mão direita): y fica fixo."""
    t = math.radians(theta_graus)
    c, s = math.cos(t), math.sin(t)
    return [[c,  0.0,  s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0,  c, 0.0],
            [0.0, 0.0, 0.0, 1.0]]


def rotacao_z(theta_graus):
    """Rotação de θ em torno do eixo z (regra da mão direita): z fica fixo."""
    t = math.radians(theta_graus)
    c, s = math.cos(t), math.sin(t)
    return [[c,  -s, 0.0, 0.0],
            [s,   c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]]


def rotacao_eixo(theta_graus, ax, ay, az):
    """
    Rotação de θ em torno de um EIXO ARBITRÁRIO (ax, ay, az) pela fórmula de
    Rodrigues. Com k = eixo unitário e [k]× a matriz do produto vetorial por k:
        R = cos θ · I + sen θ · [k]× + (1 - cos θ) · k·kᵀ
    onde  [k]× = |  0  -kz   ky |
                 |  kz   0  -kx |
                 | -ky  kx    0 |
    """
    k = normalizar((ax, ay, az))               # vetor unitário na direção do eixo
    t = math.radians(theta_graus)
    c, s = math.cos(t), math.sin(t)
    K = [[0.0, -k[2], k[1]],
         [k[2], 0.0, -k[0]],
         [-k[1], k[0], 0.0]]
    R = identidade(4)
    for i in range(3):
        for j in range(3):
            R[i][j] = (c if i == j else 0.0) + s * K[i][j] + (1 - c) * k[i] * k[j]
    return R


def escala3(sx, sy, sz):
    """Escala 3D por (sx, sy, sz); fator negativo = reflexão naquele eixo."""
    return [[sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]]


def cisalhamento3(kxy, kxz, kyx, kyz, kzx, kzy):
    """
    Cisalhamento 3D geral:
        x' = x + kxy·y + kxz·z
        y' = y + kyx·x + kyz·z
        z' = z + kzx·x + kzy·y
    """
    return [[1.0, kxy, kxz, 0.0],
            [kyx, 1.0, kyz, 0.0],
            [kzx, kzy, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]]


def translacao3(tx, ty, tz):
    """Translação 3D pelo vetor (tx, ty, tz)."""
    return [[1.0, 0.0, 0.0, tx],
            [0.0, 1.0, 0.0, ty],
            [0.0, 0.0, 1.0, tz],
            [0.0, 0.0, 0.0, 1.0]]


# ----------------------------------------------------------------------------
# 3) Construção a partir de uma descrição (tipo + parâmetros)
# ----------------------------------------------------------------------------

def construir(tipo, parametros):
    """
    Constrói a matriz a partir do nome da transformação e da lista de parâmetros.
    A dimensão (2D/3D) é deduzida do tipo e da quantidade de parâmetros:

      'rotacao'        [θ]                      2D
      'rotacao_x|y|z'  [θ]                      3D
      'rotacao_eixo'   [θ, ax, ay, az]          3D
      'escala'         [sx, sy] ou [sx, sy, sz]
      'cisalhamento'   [kx, ky] ou 6 valores (3D)
      'translacao'     [tx, ty] ou [tx, ty, tz]
      'translacao_pivo' igual a 'translacao' (usada ao girar/escalar em torno
                        de um ponto; não é interpolada nas animações)
    """
    p = parametros
    if tipo == "rotacao":
        return rotacao(p[0])
    if tipo == "rotacao_x":
        return rotacao_x(p[0])
    if tipo == "rotacao_y":
        return rotacao_y(p[0])
    if tipo == "rotacao_z":
        return rotacao_z(p[0])
    if tipo == "rotacao_eixo":
        return rotacao_eixo(p[0], p[1], p[2], p[3])
    if tipo == "escala":
        return escala(p[0], p[1]) if len(p) == 2 else escala3(p[0], p[1], p[2])
    if tipo == "cisalhamento":
        return cisalhamento(p[0], p[1]) if len(p) == 2 else cisalhamento3(*p)
    if tipo in ("translacao", "translacao_pivo"):
        return translacao(p[0], p[1]) if len(p) == 2 else translacao3(p[0], p[1], p[2])
    raise ValueError(f"Transformação desconhecida: {tipo}")


def descrever(tipo, parametros):
    """Texto curto descrevendo a transformação (usado nos relatórios)."""
    p = parametros
    if tipo == "rotacao":
        return f"Rotação de {p[0]:g}°"
    if tipo in ("rotacao_x", "rotacao_y", "rotacao_z"):
        return f"Rotação de {p[0]:g}° em torno do eixo {tipo[-1]}"
    if tipo == "rotacao_eixo":
        return f"Rotação de {p[0]:g}° em torno do eixo ({p[1]:g}, {p[2]:g}, {p[3]:g})"
    if tipo == "escala":
        if len(p) == 2:
            return f"Escala (sx={p[0]:g}, sy={p[1]:g})"
        return f"Escala (sx={p[0]:g}, sy={p[1]:g}, sz={p[2]:g})"
    if tipo == "cisalhamento":
        if len(p) == 2:
            return f"Cisalhamento (kx={p[0]:g}, ky={p[1]:g})"
        nomes = ("xy", "xz", "yx", "yz", "zx", "zy")
        return "Cisalhamento 3D (" + ", ".join(f"{n}={v:g}" for n, v in zip(nomes, p)) + ")"
    if tipo == "translacao_pivo":
        return "Translação do pivô (" + ", ".join(f"{v:g}" for v in p) + ")"
    rotulos = ("tx", "ty", "tz")
    return "Translação (" + ", ".join(f"{r}={v:g}" for r, v in zip(rotulos, p)) + ")"


def com_pivo(tipo, parametros, pivo):
    """
    Rotação/escala em torno de um ponto qualquer 'pivo' (e não da origem):
        M = T(pivô) · Op · T(-pivô)
    Devolve os 3 passos na ordem de aplicação (cada um aparece no relatório):
    levar o pivô à origem, aplicar a operação, trazer o pivô de volta.
    """
    ida = [-c for c in pivo]
    volta = list(pivo)
    return [("translacao_pivo", ida), (tipo, parametros), ("translacao_pivo", volta)]


# ----------------------------------------------------------------------------
# 4) Composição
# ----------------------------------------------------------------------------

def compor(sequencia):
    """
    Compõe uma sequência de transformações aplicadas NA ORDEM dada.

    Se a sequência é T1, T2, T3 (T1 aplicada primeiro), a matriz composta é
        M = T3 · T2 · T1
    pois o ponto fica à direita:  p' = T3·(T2·(T1·p)).

    Devolve (M, passos), onde 'passos' é a lista de dicionários com cada matriz
    individual e a matriz ACUMULADA após aquele passo (matrizes intermediárias).
    """
    acumulada = None
    passos = []
    for tipo, parametros in sequencia:
        T = construir(tipo, parametros)
        if acumulada is None:
            acumulada = identidade(len(T))      # 3x3 (2D) ou 4x4 (3D)
        elif len(T) != len(acumulada):
            raise ValueError("não é possível misturar transformações 2D e 3D")
        # A nova transformação entra à ESQUERDA do que já foi acumulado.
        acumulada = multiplicar(T, acumulada)
        passos.append({
            "tipo": tipo,
            "descricao": descrever(tipo, parametros),
            "matriz": T,
            "acumulada": [linha[:] for linha in acumulada],
        })
    if acumulada is None:
        raise ValueError("sequência vazia")
    return acumulada, passos


def compor_inversa(sequencia):
    """
    Inversa da composta SEM inverter M diretamente:
        M = Tn·...·T2·T1   =>   M⁻¹ = T1⁻¹·T2⁻¹·...·Tn⁻¹
    (a inversa de um produto é o produto das inversas na ordem contrária).
    Levanta ValueError se alguma Ti for singular (ex.: escala 0).
    """
    inversas = [inversa(construir(t, p)) for t, p in sequencia]
    return multiplicar_varias(inversas)


def parte_linear(M):
    """Extrai o bloco A (2x2 ou 3x3) de uma matriz homogênea (3x3 ou 4x4)."""
    n = len(M) - 1
    return [[M[i][j] for j in range(n)] for i in range(n)]


def vetor_translacao(M):
    """Última coluna (sem a linha de baixo) da matriz homogênea: o vetor t."""
    n = len(M) - 1
    return [M[i][n] for i in range(n)]


# ----------------------------------------------------------------------------
# 5) Aplicação a uma matriz de vértices
# ----------------------------------------------------------------------------

def aplicar_matriz(M, V):
    """
    Aplica a matriz homogênea M a TODOS os vértices de uma vez.

    V é a matriz de coordenadas de vértices, de ordem n x N (n = 2 ou 3):
    cada COLUNA é um vértice. Acrescenta-se a linha de 1s (coordenada
    homogênea), calcula-se o produto M·H e descarta-se a última linha:
        H = [V ; 1...1]      V' = (M·H) sem a última linha
    """
    n = len(V)
    N = len(V[0])
    H = [linha[:] for linha in V] + [[1.0] * N]
    R = multiplicar(M, H)
    return R[:n]


def aplicar_aos_pontos(M, pontos):
    """Versão para uma lista de pontos [(x, y[, z]), ...] (usada na malha do gráfico)."""
    if not pontos:
        return []
    n = len(pontos[0])
    V = [[p[i] for p in pontos] for i in range(n)]
    R = aplicar_matriz(M, V)
    return [tuple(R[i][j] for i in range(n)) for j in range(len(pontos))]


# ----------------------------------------------------------------------------
# 6) Interpolação (animações)
# ----------------------------------------------------------------------------

def interpolar_sequencia(sequencia, t):
    """
    Sequência "parcial" no instante t (0 = nada acontece, 1 = sequência completa).
    Cada parâmetro vai do valor NEUTRO ao valor final:
        ângulo: 0 -> θ     escala: 1 -> s     cisalhamento: 0 -> k     translação: 0 -> v
    As translações de pivô ('translacao_pivo') ficam fixas para que a rotação
    continue sendo feita em torno do mesmo ponto durante a animação.
    """
    nova = []
    for tipo, p in sequencia:
        if tipo in ("rotacao", "rotacao_x", "rotacao_y", "rotacao_z"):
            q = [p[0] * t]
        elif tipo == "rotacao_eixo":
            q = [p[0] * t] + list(p[1:])
        elif tipo == "escala":
            q = [1 + (s - 1) * t for s in p]
        elif tipo in ("cisalhamento", "translacao"):
            q = [v * t for v in p]
        else:                                   # translacao_pivo
            q = list(p)
        nova.append((tipo, q))
    return nova
