"""
fonte.py
--------
Fonte VETORIAL própria: transforma QUALQUER texto digitado em polígonos
(listas de vértices), sem usar nenhuma biblioteca de fontes.

Como funciona
  1) Cada caractere é definido por TRAÇOS: um traço é uma poligonal, isto é,
     uma lista de pontos (x, y) ligados por segmentos de reta. Curvas (O, C, S,
     2, 3, 8...) são aproximadas por vários segmentos pequenos calculados com
     seno e cosseno (equação paramétrica da elipse).
  2) Cada SEGMENTO de reta p -> q é transformado em um retângulo (a "tinta"):
         d = (q - p) / |q - p|        vetor diretor unitário
         n = d girado de +90°          vetor normal unitário  (n ⟂ d)
         vértices = p ± h·n  e  q ± h·n      com h = espessura / 2
     (as pontas são estendidas para os retângulos se encontrarem sem falhas;
     nas juntas usa-se esquadria (miter) h·tan(φ/2) ou, se muito agudas, um octógono).
  3) O texto inteiro vira uma lista de polígonos (retângulos e, nas juntas
     agudas, octógonos). A matriz de vértices do objeto é formada pelos cantos
     desses polígonos.

Cada letra cabe numa caixa de ~4 de largura por ~6 de altura (como o logo do
trabalho original); letras minúsculas são desenhadas como maiúsculas, e
acentos (á, ã, ç, ü, ...) são desenhados como pequenos traços extras.
"""

import math
import unicodedata

from vetores import (subtrair, somar, multiplicar_por_escalar, normalizar,
                     perpendicular_2d, norma, produto_escalar)

ESPESSURA = 0.9          # espessura padrão do traço
ESPACO_ENTRE_LETRAS = 0.8
LARGURA_ESPACO = 2.2     # avanço do caractere ' ' (espaço)
MAX_CARACTERES = 60


def _arco(cx, cy, rx, ry, a0, a1, n=None):
    """
    Pontos de um arco de elipse de centro (cx, cy) e semi-eixos (rx, ry),
    do ângulo a0 ao ângulo a1 (em graus):  (cx + rx·cos a,  cy + ry·sen a).
    Ângulo 0° aponta para a direita e 90° para cima; a1 < a0 percorre o arco
    no sentido horário.
    """
    if n is None:
        n = max(4, int(math.ceil(abs(a1 - a0) / 15.0)))   # ~1 segmento a cada 15°
    pontos = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pontos.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pontos


# ----------------------------------------------------------------------------
# Definição dos caracteres (caixa de 3 x 5 para as linhas centrais dos traços)
# ----------------------------------------------------------------------------

_B_SUP = [(0, 5), (1.8, 5)] + _arco(1.8, 3.75, 0.9, 1.25, 90, -90) + [(0, 2.5)]
_P_BOJO = [(0, 5), (1.8, 5)] + _arco(1.8, 3.75, 1.2, 1.25, 90, -90) + [(0, 2.5)]
_S = _arco(1.5, 3.75, 1.5, 1.25, 20, 270) + _arco(1.5, 1.25, 1.5, 1.25, 90, -160)[1:]
_3 = _arco(1.5, 3.75, 1.4, 1.25, 150, -90) + _arco(1.5, 1.25, 1.5, 1.25, 90, -150)[1:]

GLIFOS = {
    # --- letras ---------------------------------------------------------------
    "A": [[(0, 0), (1.5, 5), (3, 0)], [(0.5, 1.7), (2.5, 1.7)]],
    "B": [[(0, 0), (0, 5)], _B_SUP,
          [(0, 2.5), (2.0, 2.5)] + _arco(2.0, 1.25, 1.0, 1.25, 90, -90) + [(0, 0)]],
    "C": [_arco(1.5, 2.5, 1.5, 2.5, 45, 315)],
    "D": [[(0, 0), (0, 5)],
          [(0, 5), (1.5, 5)] + _arco(1.5, 2.5, 1.5, 2.5, 90, -90) + [(0, 0)]],
    "E": [[(3, 5), (0, 5), (0, 0), (3, 0)], [(0, 2.5), (2.4, 2.5)]],
    "F": [[(3, 5), (0, 5), (0, 0)], [(0, 2.6), (2.4, 2.6)]],
    "G": [_arco(1.5, 2.5, 1.5, 2.5, 40, 360) + [(1.6, 2.5)]],
    "H": [[(0, 0), (0, 5)], [(3, 0), (3, 5)], [(0, 2.5), (3, 2.5)]],
    "I": [[(0.2, 5), (2.8, 5)], [(1.5, 5), (1.5, 0)], [(0.2, 0), (2.8, 0)]],
    "J": [[(3, 5), (3, 1.5)] + _arco(1.5, 1.5, 1.5, 1.5, 0, -180) + [(0, 2.0)]],
    "K": [[(0, 0), (0, 5)], [(3, 5), (0, 2.2)], [(0.9, 3.04), (3, 0)]],
    "L": [[(0, 5), (0, 0), (3, 0)]],
    "M": [[(0, 0), (0, 5), (1.5, 2.2), (3, 5), (3, 0)]],
    "N": [[(0, 0), (0, 5), (3, 0), (3, 5)]],
    "O": [_arco(1.5, 2.5, 1.5, 2.5, 0, 360)],
    "P": [[(0, 0), (0, 5)], _P_BOJO],
    "Q": [_arco(1.5, 2.5, 1.5, 2.5, 0, 360), [(1.8, 1.2), (3.1, -0.2)]],
    "R": [[(0, 0), (0, 5)], _P_BOJO, [(1.2, 2.5), (3, 0)]],
    "S": [_S],
    "T": [[(0, 5), (3, 5)], [(1.5, 5), (1.5, 0)]],
    "U": [[(0, 5), (0, 1.5)] + _arco(1.5, 1.5, 1.5, 1.5, 180, 360) + [(3, 5)]],
    "V": [[(0, 5), (1.5, 0), (3, 5)]],
    "W": [[(0, 5), (0.75, 0), (1.5, 3.0), (2.25, 0), (3, 5)]],
    "X": [[(0, 5), (3, 0)], [(0, 0), (3, 5)]],
    "Y": [[(0, 5), (1.5, 2.5), (3, 5)], [(1.5, 2.5), (1.5, 0)]],
    "Z": [[(0, 5), (3, 5), (0, 0), (3, 0)]],
    # --- algarismos -----------------------------------------------------------
    "0": [_arco(1.5, 2.5, 1.3, 2.5, 0, 360), [(0.7, 0.9), (2.3, 4.1)]],
    "1": [[(0.4, 4.0), (1.5, 5), (1.5, 0)], [(0.3, 0), (2.7, 0)]],
    "2": [_arco(1.5, 3.6, 1.5, 1.4, 170, -40) + [(0, 0), (3, 0)]],
    "3": [_3],
    "4": [[(2.2, 0), (2.2, 5), (0, 1.6), (3, 1.6)]],
    "5": [[(3, 5), (0.2, 5), (0, 2.8)] + _arco(1.5, 1.75, 1.5, 1.75, 140, -140)],
    "6": [_arco(1.5, 1.7, 1.5, 1.7, 0, 360),
          [(0, 1.7), (0.1, 3.2), (1.0, 4.6), (2.6, 5)]],
    "7": [[(0, 5), (3, 5), (1.0, 0)]],
    "8": [_arco(1.5, 3.8, 1.3, 1.2, 0, 360), _arco(1.5, 1.25, 1.5, 1.25, 0, 360)],
    "9": [_arco(1.5, 3.3, 1.5, 1.7, 0, 360),
          [(3, 3.3), (2.9, 1.8), (2.0, 0.4), (0.4, 0)]],
    # --- pontuação ------------------------------------------------------------
    ".": [[(0, 0), (0, 0.1)]],
    ",": [[(0.4, 0.3), (0, -0.9)]],
    ":": [[(0, 0), (0, 0.1)], [(0, 3.0), (0, 3.1)]],
    "!": [[(0, 5), (0, 1.6)], [(0, 0), (0, 0.1)]],
    "'": [[(0, 5), (0, 4.0)]],
    "-": [[(0.3, 2.5), (2.7, 2.5)]],
    "_": [[(0, -0.8), (3, -0.8)]],
    "+": [[(0.3, 2.5), (2.7, 2.5)], [(1.5, 1.3), (1.5, 3.7)]],
    "=": [[(0.3, 1.7), (2.7, 1.7)], [(0.3, 3.3), (2.7, 3.3)]],
    "/": [[(0, 0), (3, 5)]],
    "?": [_arco(1.5, 3.7, 1.4, 1.3, 170, -90) + [(1.5, 1.6)], [(1.5, 0), (1.5, 0.1)]],
    "(": [_arco(2.2, 2.5, 1.6, 2.8, 115, 245)],
    ")": [_arco(0.8, 2.5, 1.6, 2.8, -65, 65)],
}

# Acentos (marcas de combinação Unicode). Cada um é uma função do x central 'cx'
# da letra e devolve (lista de traços, espessura do traço).
ACENTOS = {
    "\u0301": lambda cx: ([[(cx - 0.3, 6.0), (cx + 0.5, 6.9)]], 0.55),              # agudo  ´
    "\u0300": lambda cx: ([[(cx - 0.5, 6.9), (cx + 0.3, 6.0)]], 0.55),              # grave  `
    "\u0302": lambda cx: ([[(cx - 0.8, 6.0), (cx, 6.9), (cx + 0.8, 6.0)]], 0.55),   # circunflexo ^
    "\u0303": lambda cx: ([[(cx - 1.0, 6.1), (cx - 0.5, 6.7), (cx + 0.5, 6.1),
                            (cx + 1.0, 6.7)]], 0.5),                                # til ~
    "\u0308": lambda cx: ([[(cx - 0.7, 6.4), (cx - 0.7, 6.5)],
                           [(cx + 0.7, 6.4), (cx + 0.7, 6.5)]], 0.6),               # trema ¨
    "\u0327": lambda cx: ([[(cx, -0.45), (cx + 0.4, -1.1), (cx - 0.2, -1.5)]], 0.5),  # cedilha ¸
}


def segmento_para_retangulo(p, q, espessura, ext_ini=None, ext_fim=None):
    """
    Transforma o segmento p -> q em um retângulo de largura 'espessura'
    (4 vértices em sentido ANTI-HORÁRIO), usando vetores:
        d = (q - p)/|q - p|   (vetor diretor unitário)
        n = perpendicular(d)  (vetor normal unitário, d girado +90°)
        h = espessura / 2
    As pontas são estendidas em 'ext_ini' e 'ext_fim' na direção d, para que
    segmentos vizinhos se encontrem sem frestas (por padrão, h = tampa quadrada).
    Devolve None para segmentos de comprimento ~0.
    """
    v = subtrair(q, p)
    if norma(v) < 1e-6:
        return None
    h = espessura / 2.0
    ext_ini = h if ext_ini is None else ext_ini
    ext_fim = h if ext_fim is None else ext_fim
    d = normalizar(v)
    n = perpendicular_2d(d)
    a = subtrair(p, multiplicar_por_escalar(ext_ini, d))   # ponta inicial estendida
    b = somar(q, multiplicar_por_escalar(ext_fim, d))      # ponta final estendida
    hn = multiplicar_por_escalar(h, n)
    return [subtrair(a, hn), subtrair(b, hn), somar(b, hn), somar(a, hn)]


def tipo_de_junta(d1, d2, h):
    """
    Decide como unir dois segmentos consecutivos com direções unitárias d1 e d2.
    Seja φ o ângulo de desvio entre eles:
        cos φ = d1·d2            sen φ = |d1 × d2|     (produto vetorial 2D)
        tan(φ/2) = sen φ / (1 + cos φ)
    - Se φ <= 90° (curvas suaves e cantos retos): junta em ESQUADRIA (miter):
      estende cada retângulo de h·tan(φ/2) e os cantos externos se encontram.
    - Se φ > 90° (ângulo muito agudo, como no topo do A ou no fundo do V): a
      esquadria viraria uma ponta enorme; então não se estende nada e coloca-se
      uma junta ARREDONDADA (octógono de raio h) sobre o vértice.
    Devolve (extensão, arredondar?).
    """
    cos_phi = produto_escalar(d1, d2)
    sen_phi = abs(d1[0] * d2[1] - d1[1] * d2[0])
    if 1 + cos_phi < 1e-9:                      # meia-volta de 180°
        return 0.0, True
    tan_meio = sen_phi / (1 + cos_phi)
    if tan_meio <= 1.0 + 1e-9:
        return h * tan_meio, False
    return 0.0, True


def octogono(centro, h):
    """Octógono regular (anti-horário) que contém o círculo de raio h: junta arredondada."""
    r = h / math.cos(math.radians(22.5))
    return [(centro[0] + r * math.cos(math.radians(22.5 + 45 * k)),
             centro[1] + r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]


def _tracos_para_retangulos(tracos, deslocamento, espessura):
    """
    Converte traços (poligonais) em polígonos, deslocando tudo em x por
    'deslocamento'. Cada segmento vira um retângulo; as pontas livres do traço
    têm tampa quadrada (extensão h) e as juntas internas seguem tipo_de_junta().
    """
    h = espessura / 2.0
    poligonos = []
    for traco in tracos:
        pontos = []
        for (x, y) in traco:                    # remove pontos repetidos consecutivos
            p = (x + deslocamento, y)
            if not pontos or norma(subtrair(p, pontos[-1])) > 1e-6:
                pontos.append(p)
        if len(pontos) < 2:
            continue
        fechado = len(pontos) > 2 and norma(subtrair(pontos[0], pontos[-1])) < 1e-6
        if fechado:
            pontos.pop()                        # curva fechada (O, 0, 8...): último = primeiro
        n = len(pontos)
        total = n if fechado else n - 1         # número de segmentos
        dirs = [normalizar(subtrair(pontos[(i + 1) % n], pontos[i])) for i in range(total)]
        # Juntas: o vértice j une o segmento j-1 ao segmento j.
        juntas = {}
        for j in range(0 if fechado else 1, total):
            ext, redonda = tipo_de_junta(dirs[(j - 1) % total], dirs[j % total], h)
            juntas[j] = ext
            if redonda:
                poligonos.append(octogono(pontos[j % n], h))
        for i in range(total):
            j_fim = 0 if (i + 1 == total and fechado) else i + 1
            ext_ini = juntas.get(i, h)          # ponta livre do traço -> tampa quadrada
            ext_fim = juntas.get(j_fim, h)
            r = segmento_para_retangulo(pontos[i], pontos[(i + 1) % n], espessura,
                                        ext_ini, ext_fim)
            if r is not None:
                poligonos.append(r)
    return poligonos


def _decompor(caractere):
    """Separa a letra-base de seus acentos: 'ã' -> ('A', ['\\u0303'])."""
    nfd = unicodedata.normalize("NFD", caractere.upper())
    base = nfd[0]
    marcas = [c for c in nfd[1:] if unicodedata.combining(c)]
    return base, marcas


def texto_para_poligonos(texto, espessura=ESPESSURA):
    """
    Converte um texto QUALQUER em polígonos (cada um é uma lista de vértices
    (x, y) em sentido anti-horário: retângulos e octógonos de junta).

    Devolve (retangulos, desconhecidos): 'desconhecidos' é o conjunto de
    caracteres que a fonte não possui (são desenhados como '?').
    O texto começa em x = 0 (a centralização é feita em objetos.py).
    """
    texto = texto.replace("\t", " ").strip()
    if not texto:
        raise ValueError("o texto está vazio")
    if len(texto) > MAX_CARACTERES:
        raise ValueError(f"texto muito longo (máximo de {MAX_CARACTERES} caracteres)")
    h = espessura / 2.0
    retangulos = []                             # (na verdade: polígonos)
    desconhecidos = set()
    pen = 0.0                                   # posição horizontal onde a próxima letra começa
    for caractere in texto:
        if unicodedata.category(caractere).startswith("C"):
            continue                            # ignora caracteres de controle
        if caractere.isspace():
            pen += LARGURA_ESPACO
            continue
        base, marcas = _decompor(caractere)
        if base not in GLIFOS:
            desconhecidos.add(caractere)
            base, marcas = "?", []
        tracos = GLIFOS[base]
        xs = [x for traco in tracos for (x, _) in traco]
        xmin, xmax = min(xs), max(xs)
        desloc = pen - xmin + h                 # borda esquerda da tinta fica em 'pen'
        retangulos += _tracos_para_retangulos(tracos, desloc, espessura)
        for marca in marcas:                    # acentos desenhados sobre/sob a letra
            if marca in ACENTOS:
                tracos_acento, esp_acento = ACENTOS[marca]((xmin + xmax) / 2.0)
                retangulos += _tracos_para_retangulos(tracos_acento, desloc, esp_acento)
        pen += (xmax - xmin) + espessura + ESPACO_ENTRE_LETRAS
    if not retangulos:
        raise ValueError("o texto não tem caracteres desenháveis")
    return retangulos, desconhecidos


# Nome antigo mantido por compatibilidade.
texto_para_retangulos = texto_para_poligonos
