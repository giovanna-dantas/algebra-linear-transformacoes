"""
graficos.py
-----------
Gráficos (Matplotlib) e animação GIF (Pillow) para objetos 2D e 3D.

O Matplotlib é usado SÓ para desenhar polígonos e linhas já calculados. Toda a
matemática vem do próprio projeto:
  - matrizes.py / transformacoes.py : produto de matrizes, determinante, autovalores;
  - vetores.py ........................ produto escalar e vetorial.

Renderização 3D (feita aqui, sem biblioteca 3D):
  1) CÂMERA: as coordenadas do mundo são giradas por R = Rx(elevação)·Ry(azimute),
     que são matrizes de rotação 3x3; o observador fica no eixo z, olhando para -z.
  2) PERSPECTIVA: ponto (x, y, z) -> (x, y)·D/(D - z), com D = distância da câmera.
  3) FACES VISÍVEIS: o vetor normal de cada face vem do PRODUTO VETORIAL de duas
     arestas; a face aparece se normal · (olho - ponto) > 0.
  4) ILUMINAÇÃO (Lambert): brilho = ambiente + difusa · max(0, normal · luz),
     um PRODUTO ESCALAR entre dois vetores unitários.
  5) ORDEM DE DESENHO (algoritmo do pintor): faces mais distantes primeiro.
"""

import io
import math

import matplotlib
matplotlib.use("Agg")                 # backend sem janela (gera só arquivos)
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import to_rgb
from PIL import Image

from matrizes import (determinante, autovalores, autovalores_distintos, autovetores,
                      formatar_matriz, formatar_numero, multiplicar, EPS)
from vetores import produto_escalar, produto_vetorial, subtrair, normalizar, norma
from transformacoes import (aplicar_matriz, aplicar_aos_pontos, parte_linear, compor,
                            interpolar_sequencia, rotacao_x, rotacao_y)
from objetos import volume_assinado

COR_ORIGINAL = "#1f77b4"     # azul
COR_FINAL = "#d62728"        # vermelho
COR_AUTOVETOR = "#2ca02c"    # verde

AZIMUTE_PADRAO = -28.0       # graus: giro da câmera em torno do eixo y
ELEVACAO_PADRAO = 18.0       # graus: inclinação da câmera em torno do eixo x
LUZ = normalizar((-0.35, 0.55, 0.75))   # direção (unitária) de onde vem a luz, no referencial da câmera
AMBIENTE = 0.38              # luz ambiente (brilho mínimo de uma face)


# ----------------------------------------------------------------------------
# Auxiliares comuns
# ----------------------------------------------------------------------------

def clarear(cor, fator):
    """Mistura a cor com branco: fator 0 = cor original, 1 = branco."""
    r, g, b = to_rgb(cor)
    return (r + (1 - r) * fator, g + (1 - g) * fator, b + (1 - b) * fator)


def limites_quadrados(lim):
    """Torna o retângulo (xmin, xmax, ymin, ymax) um quadrado (escala 1:1)."""
    xmin, xmax, ymin, ymax = lim
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    meio = max(xmax - xmin, ymax - ymin) / 2
    return cx - meio, cx + meio, cy - meio, cy + meio


def limites_de_pontos(pontos, margem):
    """Menor retângulo (xmin, xmax, ymin, ymax) que contém os pontos 2D, com margem."""
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    return min(xs) - margem, max(xs) + margem, min(ys) - margem, max(ys) + margem


def passo_da_grade(lim):
    """Espaçamento 'bonito' (1, 2, 5, 10...) para a malha, conforme o tamanho da figura."""
    tamanho = lim[1] - lim[0]
    for passo in (1, 2, 5, 10, 20, 50, 100):
        if tamanho / passo <= 14:
            return passo
    return 200


def orientacao(det):
    """Frase curta sobre o sinal do determinante."""
    if det > EPS:
        return "preserva orientação"
    if det < -EPS:
        return "inverte orientação"
    return "achata (det = 0)"


def configurar_eixos_2d(ax, lim, titulo):
    """Aplica limites, escala 1:1, título e eixos de referência."""
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)
    ax.axvline(0, color="black", linewidth=0.6, zorder=1)
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


# ----------------------------------------------------------------------------
# 2D
# ----------------------------------------------------------------------------

def desenhar_objeto_2d(ax, obj, cor, fantasma=False):
    """
    Desenha as faces de um objeto 2D.
      - objetos com contorno (quadrado, triângulo, casinha): preenchimento
        translúcido + contorno (tracejado se for 'fantasma');
      - texto: preenchimento sólido, sem contorno (traços se sobrepõem).
    """
    poligonos = [obj.poligono(f) for f in obj.faces]
    if obj.borda:
        colecao = PolyCollection(
            poligonos,
            facecolors=[(*to_rgb(cor), 0.0 if fantasma else 0.35)],
            edgecolors=[cor], linewidths=1.8,
            linestyles="--" if fantasma else "-", zorder=3)
    else:
        face = clarear(cor, 0.82) if fantasma else to_rgb(cor)
        colecao = PolyCollection(poligonos, facecolors=[face], edgecolors="none",
                                 linewidths=0, zorder=1.5 if fantasma else 3)
    ax.add_collection(colecao)


def desenhar_grade(ax, M, lim, cor="#999999"):
    """
    Malha do plano deformada pela matriz M (2D). Como a transformação é afim,
    cada reta continua reta: basta transformar suas extremidades.
    """
    passo = passo_da_grade(lim)
    raio = int(max(abs(lim[0]), abs(lim[1]), abs(lim[2]), abs(lim[3]))) * 3 + 6
    raio = (raio // passo + 1) * passo
    pontos = []
    for k in range(-raio, raio + 1, passo):
        pontos += [(k, -raio), (k, raio), (-raio, k), (raio, k)]
    novos = aplicar_aos_pontos(M, pontos)
    segmentos = [[novos[i], novos[i + 1]] for i in range(0, len(novos), 2)]
    ax.add_collection(LineCollection(segmentos, colors=cor, linewidths=0.5,
                                     alpha=0.6, zorder=1))


def direcoes_invariantes(A):
    """
    Direções (vetores unitários) dos autovetores REAIS de A: as direções que a
    transformação só estica ou encolhe, sem girar.
    """
    direcoes = []
    for lam, _ in autovalores_distintos(autovalores(A)):
        direcoes += autovetores(A, lam)
    return direcoes


def desenhar_autovetores_2d(ax, M, lim):
    """Setas verdes, a partir da origem, nas direções dos autovetores reais da parte linear."""
    comprimento = (lim[1] - lim[0]) * 0.45
    for v in direcoes_invariantes(parte_linear(M)):
        ax.annotate("", xy=(v[0] * comprimento, v[1] * comprimento), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=COR_AUTOVETOR, lw=1.6), zorder=4)


def _limites_2d(objetos, margem):
    """Retângulo que contém todos os vértices (a escala 1:1 é garantida pelo Matplotlib)."""
    pontos = [p for o in objetos for p in o.vertices()]
    return limites_de_pontos(pontos, margem)


def _empilhar(lim):
    """True se a região é muito mais larga que alta (ex.: uma palavra): empilhar os painéis."""
    return (lim[1] - lim[0]) > 2.2 * (lim[3] - lim[2])


def _criar_figura(lim):
    """Figura com 2 painéis: lado a lado, ou um sobre o outro se a região for larga."""
    if _empilhar(lim):
        return plt.subplots(2, 1, figsize=(9.5, 8.8))
    return plt.subplots(1, 2, figsize=(11, 5.2))


def _painel_2d(ax, obj, M, lim, titulo, grade=True, autov=True):
    """Painel do estado FINAL: malha deformada, original tracejado, objeto final, autovetores."""
    final = obj.com_vertices(aplicar_matriz(M, obj.V))
    if grade:
        desenhar_grade(ax, M, lim)
    desenhar_objeto_2d(ax, obj, COR_ORIGINAL, fantasma=True)
    desenhar_objeto_2d(ax, final, COR_FINAL)
    if autov:
        desenhar_autovetores_2d(ax, M, lim)
    configurar_eixos_2d(ax, lim, titulo)


# ----------------------------------------------------------------------------
# 3D: câmera, projeção e renderização
# ----------------------------------------------------------------------------

def matriz_camera(azimute=AZIMUTE_PADRAO, elevacao=ELEVACAO_PADRAO):
    """Matriz 3x3 da câmera: R = Rx(elevação) · Ry(azimute) (duas rotações)."""
    return multiplicar(parte_linear(rotacao_x(elevacao)), parte_linear(rotacao_y(azimute)))


def distancia_camera(objetos):
    """Distância D do observador: 4x o raio da esfera que contém todos os vértices."""
    raio = max(norma(p) for o in objetos for p in o.vertices())
    return 4.0 * max(raio, 1e-6)


def projetar(ponto, D):
    """Projeção em perspectiva de um ponto (x, y, z) da câmera: (x, y)·D/(D - z)."""
    f = D / (D - ponto[2])
    return (ponto[0] * f, ponto[1] * f)


def renderizar_3d(obj, R, D, cor, alfa=1.0, sombrear=True):
    """
    Converte um objeto 3D em polígonos 2D sombreados e ordenados do fundo para a
    frente. Devolve (lista de (z_médio, polígono_2d, cor_rgba), pontos_2d_projetados).
    """
    Vc = multiplicar(R, obj.V)                              # coordenadas na câmera (3 x N)
    pts = [(Vc[0][i], Vc[1][i], Vc[2][i]) for i in range(obj.n_vertices())]
    proj = [projetar(p, D) for p in pts]
    volume = volume_assinado(obj)
    sinal = -1.0 if volume < -1e-9 else 1.0                 # reflexão inverte a orientação das faces
    eliminar_costas = abs(volume) > 1e-9                    # sólido achatado: desenha os dois lados
    olho = (0.0, 0.0, D)
    base = to_rgb(cor)
    itens = []
    for face in obj.faces:
        P = [pts[i] for i in face]
        n = produto_vetorial(subtrair(P[1], P[0]), subtrair(P[2], P[1]))   # normal da face
        if norma(n) < 1e-12:
            continue
        n = tuple(sinal * c for c in normalizar(n))
        if eliminar_costas and produto_escalar(n, subtrair(olho, P[0])) <= 0:
            continue                                        # face de trás: não aparece
        cos_luz = produto_escalar(n, LUZ)
        if not eliminar_costas:
            cos_luz = abs(cos_luz)
        brilho = min(1.0, AMBIENTE + (1 - AMBIENTE) * max(0.0, cos_luz)) if sombrear else 1.0
        rgba = (base[0] * brilho, base[1] * brilho, base[2] * brilho, alfa)
        z_medio = sum(p[2] for p in P) / len(P)
        itens.append((z_medio, [proj[i] for i in face], rgba))
    itens.sort(key=lambda it: it[0])                        # mais longe (z menor) primeiro
    return itens, proj


def _geometria_3d(objetos, azimute, elevacao):
    """
    Geometria FIXA da câmera para todos os estados que serão comparados:
    devolve (R, D, limites, (tx, ty, tz) = comprimento de cada eixo). Os limites cobrem todos os
    vértices e as pontas dos eixos, para nada sair do quadro.
    """
    R = matriz_camera(azimute, elevacao)
    D = distancia_camera(objetos)
    # Cada eixo tem comprimento proporcional à extensão dos objetos naquele eixo
    # (um texto largo e fino tem eixo x longo e eixo z curto), com um piso.
    ext = [max(abs(p[k]) for o in objetos for p in o.vertices()) for k in range(3)]
    tamanho = tuple(max(1.15 * e, 0.2 * max(ext)) for e in ext)   # (tx, ty, tz)
    pontos = []
    for o in objetos:
        Vc = multiplicar(R, o.V)
        pontos += [projetar((Vc[0][i], Vc[1][i], Vc[2][i]), D) for i in range(o.n_vertices())]
    for k, e in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
        ponta = tuple(sum(R[i][j] * e[j] * tamanho[k] for j in range(3)) for i in range(3))
        pontos.append(projetar(ponta, D))
    largura = max(p[0] for p in pontos) - min(p[0] for p in pontos)
    altura = max(p[1] for p in pontos) - min(p[1] for p in pontos)
    lim = limites_de_pontos(pontos, 0.1 * max(largura, altura))
    return R, D, lim, tamanho


def desenhar_eixos_3d(ax, R, D, tamanho):
    """Eixos x, y, z (cinza) a partir da origem, já girados pela câmera. tamanho = (tx, ty, tz)."""
    for k, (rotulo, e) in enumerate((("x", (1, 0, 0)), ("y", (0, 1, 0)), ("z", (0, 0, 1)))):
        ponta = tuple(sum(R[i][j] * e[j] * tamanho[k] for j in range(3)) for i in range(3))
        x, y = projetar(ponta, D)
        ax.plot([0, x], [0, y], color="#555555", linewidth=1.0, alpha=0.7, zorder=5)
        ax.text(x, y, rotulo, color="#333333", fontsize=9, ha="center", va="center", zorder=6)


def desenhar_autovetores_3d(ax, R, D, A, tamanho):
    """Retas verdes pela origem nas direções dos autovetores reais de A (3x3)."""
    for v in direcoes_invariantes(A):
        pa = tuple(sum(R[i][j] * v[j] * tamanho for j in range(3)) for i in range(3))
        pb = tuple(-c for c in pa)
        (x1, y1), (x2, y2) = projetar(pa, D), projetar(pb, D)
        ax.plot([x1, x2], [y1, y2], color=COR_AUTOVETOR, linewidth=1.6, zorder=6)


def _painel_3d(ax, obj, R, D, lim, tamanho, titulo, cor, fantasma=None, A=None):
    """
    Desenha um objeto 3D num painel. 'fantasma' (opcional) é outro objeto
    desenhado como silhueta clara ao fundo (o estado inicial); 'A' (opcional) é a
    parte linear cujos autovetores reais serão desenhados em verde.
    """
    if fantasma is not None:
        itens, _ = renderizar_3d(fantasma, R, D, clarear(COR_ORIGINAL, 0.78), sombrear=False)
        ax.add_collection(PolyCollection([it[1] for it in itens],
                                         facecolors=[it[2] for it in itens],
                                         edgecolors=[it[2] for it in itens], linewidths=0.3,
                                         zorder=1.5))
    itens, _ = renderizar_3d(obj, R, D, cor)
    poligonos = [it[1] for it in itens]
    cores = [it[2] for it in itens]
    if obj.borda:
        bordas, largura = [(0.15, 0.15, 0.15, 1.0)] * len(cores), 0.9
    else:
        bordas, largura = cores, 0.35                      # cobre frestas entre faces vizinhas
    ax.add_collection(PolyCollection(poligonos, facecolors=cores, edgecolors=bordas,
                                     linewidths=largura, zorder=3))
    desenhar_eixos_3d(ax, R, D, tamanho)
    if A is not None:
        desenhar_autovetores_3d(ax, R, D, A, max(tamanho))
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)


# ----------------------------------------------------------------------------
# Gráfico estado inicial x estado final
# ----------------------------------------------------------------------------

def grafico_antes_depois(obj, M, titulo, caminho, azimute=AZIMUTE_PADRAO,
                         elevacao=ELEVACAO_PADRAO):
    """
    Gera uma figura com dois painéis (2D ou 3D conforme o objeto):
      - primeiro: objeto original (azul);
      - segundo: objeto transformado (vermelho), original ao fundo, e as direções
        dos autovetores reais (verde). Em 2D mostra também a malha deformada.
    Os painéis ficam lado a lado, ou empilhados quando o objeto é muito largo.
    """
    final = obj.com_vertices(aplicar_matriz(M, obj.V))
    if obj.dim == 2:
        lim = _limites_2d([obj, final], margem=1.5)
        fig, (ax1, ax2) = _criar_figura(lim)
        desenhar_objeto_2d(ax1, obj, COR_ORIGINAL)
        configurar_eixos_2d(ax1, lim, "Estado inicial")
        ax1.grid(True, linewidth=0.3)
        _painel_2d(ax2, obj, M, lim, "Estado final (malha deformada, autovetores em verde)")
    else:
        R, D, lim, tam = _geometria_3d([obj, final], azimute, elevacao)
        fig, (ax1, ax2) = _criar_figura(lim)
        _painel_3d(ax1, obj, R, D, lim, tam, "Estado inicial", COR_ORIGINAL)
        _painel_3d(ax2, final, R, D, lim, tam,
                   "Estado final (original ao fundo, autovetores em verde)",
                   COR_FINAL, fantasma=obj, A=parte_linear(M))
    fig.suptitle(titulo, fontsize=13)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


def grafico_ordem(obj, passoA, passoB, caminho, azimute=AZIMUTE_PADRAO,
                  elevacao=ELEVACAO_PADRAO):
    """
    Mostra que o produto de matrizes NÃO é comutativo: compara A depois B
    com B depois A. passoA e passoB são pares (tipo, parâmetros) de transformações.
    """
    M_ab, _ = compor([passoA, passoB])          # A primeiro, depois B  -> B·A
    M_ba, _ = compor([passoB, passoA])          # B primeiro, depois A  -> A·B
    r1 = obj.com_vertices(aplicar_matriz(M_ab, obj.V))
    r2 = obj.com_vertices(aplicar_matriz(M_ba, obj.V))
    rotulos = ("A depois B  (matriz B·A)", "B depois A  (matriz A·B)")
    if obj.dim == 2:
        lim = _limites_2d([obj, r1, r2], margem=1.5)
        fig, (ax1, ax2) = _criar_figura(lim)
        for ax, res, rot in ((ax1, r1, rotulos[0]), (ax2, r2, rotulos[1])):
            desenhar_objeto_2d(ax, obj, COR_ORIGINAL, fantasma=True)
            desenhar_objeto_2d(ax, res, COR_FINAL)
            configurar_eixos_2d(ax, lim, rot)
            ax.grid(True, linewidth=0.3)
    else:
        R, D, lim, tam = _geometria_3d([obj, r1, r2], azimute, elevacao)
        fig, (ax1, ax2) = _criar_figura(lim)
        for ax, res, rot in ((ax1, r1, rotulos[0]), (ax2, r2, rotulos[1])):
            _painel_3d(ax, res, R, D, lim, tam, rot, COR_FINAL, fantasma=obj)
    fig.suptitle("Ordem importa: o produto de matrizes não é comutativo", fontsize=13)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


# ----------------------------------------------------------------------------
# Animação GIF com painel de matriz / determinante / autovalores
# ----------------------------------------------------------------------------

def _texto_painel(M, dim):
    """Texto do painel lateral: matriz composta, determinante e autovalores da parte linear."""
    A = parte_linear(M)
    det = determinante(A)
    linhas_autov = "\n".join(f"  λ = {formatar_numero(l, 3)}" for l in autovalores(A))
    return ("Matriz composta M(t)\n"
            f"{formatar_matriz(M, 2)}\n\n"
            f"det(parte linear) = {det:.3f}\n"
            f"({orientacao(det)})\n\n"
            f"Autovalores:\n{linhas_autov}")


def desenhar_quadro(obj, M, geometria, t, rotulo, dpi=80):
    """
    Desenha um quadro da animação e devolve a imagem (PIL).
    'geometria' = ('2d', lim) ou ('3d', R, D, lim, tamanho_eixos), calculada uma vez para todos os quadros.
    """
    fig = plt.figure(figsize=(9, 4.6))
    ax = fig.add_axes([0.04, 0.08, 0.56, 0.84])       # área do desenho
    ax_txt = fig.add_axes([0.62, 0.08, 0.36, 0.84])   # painel de texto
    ax_txt.axis("off")
    atual = obj.com_vertices(aplicar_matriz(M, obj.V))
    titulo = f"{rotulo}  (t = {t:.2f})"
    if geometria[0] == "2d":
        lim = geometria[1]
        desenhar_grade(ax, M, lim)
        desenhar_objeto_2d(ax, obj, COR_ORIGINAL, fantasma=True)
        desenhar_objeto_2d(ax, atual, COR_FINAL)
        desenhar_autovetores_2d(ax, M, lim)
        configurar_eixos_2d(ax, lim, titulo)
    else:
        _, R, D, lim, tam = geometria
        _painel_3d(ax, atual, R, D, lim, tam, titulo, COR_FINAL, fantasma=obj,
                   A=parte_linear(M))
    ax_txt.text(0.0, 1.0, _texto_painel(M, obj.dim), va="top", ha="left",
                family="monospace", fontsize=9.5 if obj.dim == 2 else 8.5)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("P", palette=Image.ADAPTIVE)


def gerar_gif(obj, sequencia, caminho, rotulo=None, quadros=48, ms_por_quadro=60,
              azimute=AZIMUTE_PADRAO, elevacao=ELEVACAO_PADRAO):
    """
    Gera o GIF. A animação vai da identidade até a sequência completa de
    transformações e volta (ida e volta suave), formando um laço contínuo.
    Cada parâmetro é interpolado do valor neutro ao valor final (ver
    interpolar_sequencia em transformacoes.py).
    """
    rotulo = rotulo or obj.nome
    # 1) Calcula a matriz composta de cada quadro.
    ts, matrizes = [], []
    for i in range(quadros):
        u = i / quadros                              # progresso de 0 a 1
        fase = 1 - abs(2 * u - 1)                    # 0 -> 1 -> 0 (ida e volta)
        t = (1 - math.cos(math.pi * fase)) / 2       # suaviza início e fim
        M, _ = compor(interpolar_sequencia(sequencia, t))
        ts.append(t)
        matrizes.append(M)
    # 2) Geometria FIXA que cobre todos os quadros (a câmera não se mexe).
    todos = [obj] + [obj.com_vertices(aplicar_matriz(M, obj.V)) for M in matrizes]
    if obj.dim == 2:
        geometria = ("2d", _limites_2d(todos, margem=2.0))
    else:
        geometria = ("3d",) + _geometria_3d(todos, azimute, elevacao)
    # 3) Desenha os quadros e salva o GIF.
    imagens = [desenhar_quadro(obj, M, geometria, t, rotulo) for t, M in zip(ts, matrizes)]
    imagens[0].save(caminho, save_all=True, append_images=imagens[1:],
                    duration=ms_por_quadro, loop=0, disposal=2)
