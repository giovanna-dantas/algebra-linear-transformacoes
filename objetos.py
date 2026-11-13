"""
objetos.py
----------
Objetos geométricos 2D definidos por vértices.

Um objeto é uma LISTA DE CONTORNOS; cada contorno é uma lista de pontos (x, y)
na ordem em que o polígono é desenhado. Assim, um objeto simples (quadrado)
tem 1 contorno e o logo em letras tem vários.
"""

# Objetos simples

def quadrado_unitario():
    """Quadrado de lado 1 com um vértice na origem."""
    return [[(0, 0), (1, 0), (1, 1), (0, 1)]]


def triangulo():
    """Triângulo retângulo com catetos de comprimento 2."""
    return [[(0, 0), (2, 0), (0, 2)]]


def casinha():
    """Pentágono em forma de 'casinha' (quadrado + telhado)."""
    return [[(0, 0), (2, 0), (2, 2), (1, 3), (0, 2)]]


# Logo "IFSP" em letras de bloco (desenho próprio, feito só de vértices)

# Cada letra cabe numa caixa de 4 de largura por 6 de altura.
# NOTA: são letras simples escritas com polígonos; não é o logotipo oficial.

# Letra I (com "serifas" em cima e embaixo).
_LETRA_I = [(0, 0), (4, 0), (4, 1), (2.5, 1), (2.5, 5), (4, 5),
            (4, 6), (0, 6), (0, 5), (1.5, 5), (1.5, 1), (0, 1)]

# Letra F.
_LETRA_F = [(0, 0), (1.5, 0), (1.5, 2.5), (3.5, 2.5), (3.5, 3.5),
            (1.5, 3.5), (1.5, 5), (4, 5), (4, 6), (0, 6)]

# Letra S (blocos: barra de baixo, meio e de cima ligadas por hastes).
_LETRA_S = [(0, 0), (0, 1.2), (2.7, 1.2), (2.7, 2.4), (0, 2.4), (0, 6),
            (4, 6), (4, 4.8), (1.3, 4.8), (1.3, 3.6), (4, 3.6), (4, 0)]

# Letra P: contorno externo e um "buraco" interno (contorno separado).
_LETRA_P = [(0, 0), (1.5, 0), (1.5, 2), (3, 2), (4, 3), (4, 5), (3, 6), (0, 6)]
_BURACO_P = [(1.5, 3.2), (2.7, 3.2), (2.7, 4.8), (1.5, 4.8)]


def _deslocar(contorno, dx, dy):
    """Soma (dx, dy) a cada vértice (só para posicionar as letras)."""
    return [(x + dx, y + dy) for (x, y) in contorno]


def logo_ifsp():
    """
    Logo 'IFSP' centralizado na ORIGEM (0, 0), para que a rotação e a escala
    aconteçam em torno do centro do desenho.
    Devolve (contornos, indices_buracos): indices dos contornos que são buracos
    (desenhados na cor de fundo).
    """
    # Posição x inicial de cada letra (largura 4 + espaço 1).
    letras = [(_LETRA_I, 0), (_LETRA_F, 5), (_LETRA_S, 10), (_LETRA_P, 15)]
    contornos = [_deslocar(c, x0, 0) for (c, x0) in letras]
    contornos.append(_deslocar(_BURACO_P, 15, 0))
    indices_buracos = [len(contornos) - 1]
    # Centraliza: o desenho vai de x=0..19 e y=0..6 -> centro em (9.5, 3).
    contornos = [_deslocar(c, -9.5, -3) for c in contornos]
    return contornos, indices_buracos


def obter_objeto(nome):
    """Devolve (contornos, indices_buracos) a partir do nome do objeto."""
    if nome == "quadrado":
        return quadrado_unitario(), []
    if nome == "triangulo":
        return triangulo(), []
    if nome == "casinha":
        return casinha(), []
    if nome == "logo":
        return logo_ifsp()
    raise ValueError(f"Objeto desconhecido: {nome}")
