"""
objetos.py
----------
Objetos geométricos 2D e 3D definidos por uma MATRIZ DE COORDENADAS DE VÉRTICES.

Um objeto tem:
  - V ........ matriz n x N (n = 2 ou 3): cada COLUNA é um vértice (x, y[, z]);
  - faces .... lista de faces; cada face é a lista dos ÍNDICES (colunas de V)
               dos seus vértices, em ordem. Em 2D a face é um polígono
               (anti-horário); em 3D, vista de fora do sólido, a ordem dos
               vértices é anti-horária (normal apontando para fora).

Uma transformação muda só V (V' = M·V); as faces continuam as mesmas.

Objetos disponíveis:
  2D: texto (QUALQUER palavra digitada), quadrado, triângulo, casinha
  3D: texto extrudado (QUALQUER palavra com profundidade), cubo, pirâmide
"""

from fonte import texto_para_poligonos
from vetores import produto_misto


class Objeto:
    """Objeto geométrico: matriz de vértices V (n x N) + faces (índices de colunas)."""

    def __init__(self, nome, V, faces, borda=True):
        self.nome = nome
        self.V = V
        self.faces = faces
        self.borda = borda          # desenhar o contorno de cada face?
        self.dim = len(V)           # 2 (plano) ou 3 (espaço)

    def n_vertices(self):
        """Quantidade de vértices (número de colunas de V)."""
        return len(self.V[0])

    def vertice(self, i):
        """Vértice i como tupla de coordenadas."""
        return tuple(self.V[k][i] for k in range(self.dim))

    def vertices(self):
        """Lista com todos os vértices (tuplas)."""
        return [self.vertice(i) for i in range(self.n_vertices())]

    def poligono(self, face):
        """Coordenadas dos vértices de uma face."""
        return [self.vertice(i) for i in face]

    def com_vertices(self, V):
        """Novo objeto com a MESMA topologia (faces) e novos vértices V."""
        return Objeto(self.nome, V, self.faces, self.borda)


# ----------------------------------------------------------------------------
# Construção a partir de polígonos
# ----------------------------------------------------------------------------

def _de_poligonos_2d(nome, poligonos, borda=True):
    """Monta o objeto 2D juntando os vértices de todos os polígonos numa matriz 2 x N."""
    xs, ys, faces = [], [], []
    for poligono in poligonos:
        indices = []
        for (x, y) in poligono:
            indices.append(len(xs))
            xs.append(float(x))
            ys.append(float(y))
        faces.append(indices)
    return Objeto(nome, [xs, ys], faces, borda)


def _centralizar(poligonos):
    """Desloca os polígonos para que o centro da caixa envolvente fique na origem."""
    xs = [x for pol in poligonos for (x, _) in pol]
    ys = [y for pol in poligonos for (_, y) in pol]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return [[(x - cx, y - cy) for (x, y) in pol] for pol in poligonos]


# ----------------------------------------------------------------------------
# Objetos 2D
# ----------------------------------------------------------------------------

def quadrado_unitario():
    """Quadrado de lado 1 com um vértice na origem."""
    return _de_poligonos_2d("quadrado", [[(0, 0), (1, 0), (1, 1), (0, 1)]])


def triangulo():
    """Triângulo retângulo com catetos de comprimento 2."""
    return _de_poligonos_2d("triângulo", [[(0, 0), (2, 0), (0, 2)]])


def casinha():
    """Pentágono em forma de 'casinha' (quadrado + telhado)."""
    return _de_poligonos_2d("casinha", [[(0, 0), (2, 0), (2, 2), (1, 3), (0, 2)]])


def texto_2d(texto):
    """
    Texto digitado pelo usuário como objeto 2D, CENTRALIZADO na origem
    (assim rotação e escala acontecem em torno do centro do desenho).
    Devolve (objeto, caracteres_desconhecidos).
    """
    retangulos, desconhecidos = texto_para_poligonos(texto)
    retangulos = _centralizar(retangulos)
    return _de_poligonos_2d(f'texto "{texto}"', retangulos, borda=False), desconhecidos


# ----------------------------------------------------------------------------
# Objetos 3D
# ----------------------------------------------------------------------------

def cubo():
    """Cubo de aresta 2 centrado na origem (8 vértices, 6 faces)."""
    xs = [-1, 1, 1, -1, -1, 1, 1, -1]
    ys = [-1, -1, 1, 1, -1, -1, 1, 1]
    zs = [-1, -1, -1, -1, 1, 1, 1, 1]
    faces = [[0, 3, 2, 1],      # base   (z = -1)
             [4, 5, 6, 7],      # topo   (z = +1)
             [0, 1, 5, 4],      # frente (y = -1)
             [2, 3, 7, 6],      # fundo  (y = +1)
             [3, 0, 4, 7],      # esquerda (x = -1)
             [1, 2, 6, 5]]      # direita  (x = +1)
    return Objeto("cubo", [[float(v) for v in xs], [float(v) for v in ys],
                           [float(v) for v in zs]], faces)


def piramide():
    """Pirâmide de base quadrada (lado 2, em z = -1) e ápice em (0, 0, 1)."""
    xs = [-1, 1, 1, -1, 0]
    ys = [-1, -1, 1, 1, 0]
    zs = [-1, -1, -1, -1, 1]
    faces = [[0, 3, 2, 1],      # base
             [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
    return Objeto("pirâmide", [[float(v) for v in xs], [float(v) for v in ys],
                               [float(v) for v in zs]], faces)


def texto_3d(texto, profundidade=1.5):
    """
    Texto digitado pelo usuário como SÓLIDO 3D: cada polígono da fonte é
    extrudado (empurrado) em z, de -profundidade/2 até +profundidade/2, formando
    um prisma (retângulo: 8 vértices e 6 faces = topo, base e 4 laterais).
    Devolve (objeto, caracteres_desconhecidos).
    """
    retangulos, desconhecidos = texto_para_poligonos(texto)
    retangulos = _centralizar(retangulos)
    z = profundidade / 2.0
    xs, ys, zs, faces = [], [], [], []
    for r in retangulos:                                # r = polígono 2D (k vértices, anti-horário)
        k = len(r)
        b = len(xs)                                     # índice do 1º vértice deste prisma
        for (x, y) in r:                                # k vértices da base (z = -z)
            xs.append(x); ys.append(y); zs.append(-z)
        for (x, y) in r:                                # k vértices do topo (z = +z)
            xs.append(x); ys.append(y); zs.append(+z)
        faces.append([b + k + i for i in range(k)])             # topo (normal +z)
        faces.append([b + i for i in range(k - 1, -1, -1)])     # base (normal -z)
        for i in range(k):                              # k faces laterais
            j = (i + 1) % k
            faces.append([b + i, b + j, b + k + j, b + k + i])
    return Objeto(f'texto 3D "{texto}"', [xs, ys, zs], faces, borda=False), desconhecidos


# ----------------------------------------------------------------------------
# Escolha do objeto
# ----------------------------------------------------------------------------

OBJETOS_SIMPLES = {
    "quadrado": quadrado_unitario,
    "triangulo": triangulo,
    "casinha": casinha,
    "cubo": cubo,
    "piramide": piramide,
}


def obter_objeto(tipo, texto=None):
    """
    Devolve (objeto, caracteres_desconhecidos).
    tipo: 'texto', 'texto3d', 'quadrado', 'triangulo', 'casinha', 'cubo' ou 'piramide'.
    """
    if tipo == "texto":
        return texto_2d(texto)
    if tipo == "texto3d":
        return texto_3d(texto)
    if tipo in OBJETOS_SIMPLES:
        return OBJETOS_SIMPLES[tipo](), set()
    raise ValueError(f"Objeto desconhecido: {tipo}")


# ----------------------------------------------------------------------------
# Medidas: área (2D) e volume (3D) com sinal
# ----------------------------------------------------------------------------

def area_assinada(obj):
    """
    Soma das áreas (com sinal) dos polígonos 2D pela fórmula do cadarço:
        A = 1/2 · soma_i ( x_i·y_{i+1} - x_{i+1}·y_i )
    Positiva para vértices em sentido anti-horário. Se um objeto tem partes
    sobrepostas (como letras feitas de vários traços), a sobreposição é
    contada duas vezes: é uma medida de "tinta", que também é multiplicada
    por det(A) numa transformação.
    """
    total = 0.0
    for face in obj.faces:
        pts = obj.poligono(face)
        soma = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            soma += x1 * y2 - x2 * y1
        total += soma / 2.0
    return total


def volume_assinado(obj):
    """
    Volume (com sinal) de um sólido 3D pelo PRODUTO MISTO. Cada face é dividida
    em triângulos (p0, pk, pk+1) e cada triângulo forma com a origem um tetraedro
    de volume (1/6)·[p0, pk, pk+1] = (1/6)·p0·(pk × pk+1).
    Com as faces orientadas para fora, a soma dá o volume do sólido.
    """
    total = 0.0
    for face in obj.faces:
        pts = obj.poligono(face)
        for k in range(1, len(pts) - 1):
            total += produto_misto(pts[0], pts[k], pts[k + 1]) / 6.0
    return total


def medida_assinada(obj):
    """Área (2D) ou volume (3D), com sinal."""
    return area_assinada(obj) if obj.dim == 2 else volume_assinado(obj)


def caixa_envolvente(obj):
    """Devolve [(min, max), ...] para cada coordenada."""
    return [(min(linha), max(linha)) for linha in obj.V]


def vertices_formatados(obj, limite=None):
    """Lista de tuplas arredondadas com os vértices (para relatórios)."""
    saida = []
    for i in range(obj.n_vertices() if limite is None else min(limite, obj.n_vertices())):
        saida.append(tuple(round(c, 4) + 0.0 for c in obj.vertice(i)))
    return saida
