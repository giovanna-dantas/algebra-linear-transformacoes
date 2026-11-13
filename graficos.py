"""
graficos.py
-----------
Gráficos (Matplotlib) e animação GIF (Pillow).
O Matplotlib é usado SÓ para desenhar; todos os cálculos de álgebra linear
(produto de matrizes, determinante, autovalores) vêm de matrizes.py e
transformacoes.py.
"""

import io
import math

import matplotlib
matplotlib.use("Agg")                 # backend sem janela (gera só arquivos)
import matplotlib.pyplot as plt
from PIL import Image

from matrizes import (determinante, autovalores_2x2, autovetor_2x2,
                      formatar_matriz, formatar_numero, EPS)
from transformacoes import (aplicar, parte_linear, rotacao, escala,
                            cisalhamento, translacao, compor)

COR_ORIGINAL = "#1f77b4"     # azul
COR_FINAL = "#d62728"        # vermelho


# ----------------------------------------------------------------------------
# Funções auxiliares de desenho
# ----------------------------------------------------------------------------

def limites_dos_objetos(lista_de_objetos, margem=1.0):
    """Menor retângulo (xmin, xmax, ymin, ymax) que contém todos os objetos."""
    xs, ys = [], []
    for contornos in lista_de_objetos:
        for contorno in contornos:
            for (x, y) in contorno:
                xs.append(x)
                ys.append(y)
    return min(xs) - margem, max(xs) + margem, min(ys) - margem, max(ys) + margem


def limites_quadrados(lim):
    """Torna o retângulo de limites um quadrado (para manter escala 1:1)."""
    xmin, xmax, ymin, ymax = lim
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    meio = max(xmax - xmin, ymax - ymin) / 2
    return cx - meio, cx + meio, cy - meio, cy + meio


def desenhar_objeto(ax, contornos, buracos, cor, preencher=True, tracejado=False):
    """Desenha os contornos de um objeto. Buracos são pintados na cor de fundo."""
    for i, contorno in enumerate(contornos):
        xs = [p[0] for p in contorno] + [contorno[0][0]]   # fecha o polígono
        ys = [p[1] for p in contorno] + [contorno[0][1]]
        eh_buraco = i in buracos
        if preencher:
            ax.fill(xs, ys, color="white" if eh_buraco else cor,
                    alpha=1.0 if eh_buraco else 0.35, linewidth=0, zorder=2)
        estilo = "--" if tracejado else "-"
        ax.plot(xs, ys, estilo, color=cor, linewidth=1.8, zorder=3)


def desenhar_grade(ax, M, lim, cor="#999999"):
    """
    Desenha a malha do plano deformada pela matriz M. Como a transformação é
    afim, cada reta da malha continua reta: basta transformar suas extremidades.
    """
    xmin, xmax, ymin, ymax = lim
    raio = int(max(abs(xmin), abs(xmax), abs(ymin), abs(ymax))) * 3 + 6
    retas = []
    for k in range(-raio, raio + 1):
        retas.append([(k, -raio), (k, raio)])      # reta vertical x = k
        retas.append([(-raio, k), (raio, k)])      # reta horizontal y = k
    for reta in aplicar(M, retas):
        ax.plot([reta[0][0], reta[1][0]], [reta[0][1], reta[1][1]],
                color=cor, linewidth=0.5, alpha=0.6, zorder=1)


def desenhar_autovetores(ax, M, lim):
    """
    Desenha, a partir da origem, as direções dos autovetores REAIS da parte
    linear de M (direções que a transformação mantém, apenas esticando).
    """
    A = parte_linear(M)
    xmin, xmax, ymin, ymax = lim
    comprimento = (xmax - xmin) * 0.45
    for lam in autovalores_2x2(A):
        v = autovetor_2x2(A, lam)
        if v is None:
            continue
        ax.annotate("", xy=(v[0] * comprimento, v[1] * comprimento), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.6), zorder=4)


def configurar_eixos(ax, lim, titulo):
    """Aplica limites, escala 1:1, título e grade de referência."""
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)
    ax.axvline(0, color="black", linewidth=0.6, zorder=1)
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


# ----------------------------------------------------------------------------
# Gráfico estado inicial x estado final
# ----------------------------------------------------------------------------

def grafico_antes_depois(contornos, buracos, M, titulo, caminho):
    """
    Gera uma figura com dois painéis:
      - esquerda: objeto original;
      - direita: objeto transformado (vermelho), original ao fundo (tracejado),
        malha deformada e direções dos autovetores (setas verdes).
    """
    finais = aplicar(M, contornos)
    lim = limites_quadrados(limites_dos_objetos([contornos, finais], margem=1.5))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2))
    # Painel 1: estado inicial.
    desenhar_objeto(ax1, contornos, buracos, COR_ORIGINAL)
    configurar_eixos(ax1, lim, "Estado inicial")
    ax1.grid(True, linewidth=0.3)
    # Painel 2: estado final.
    desenhar_grade(ax2, M, lim)
    desenhar_objeto(ax2, contornos, buracos, COR_ORIGINAL, preencher=False, tracejado=True)
    desenhar_objeto(ax2, finais, buracos, COR_FINAL)
    desenhar_autovetores(ax2, M, lim)
    configurar_eixos(ax2, lim, "Estado final (malha deformada, autovetores em verde)")
    fig.suptitle(titulo, fontsize=13)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


def grafico_ordem(contornos, buracos, tipoA, tipoB, caminho):
    """
    Mostra que o produto de matrizes NÃO é comutativo: compara A depois B
    com B depois A. tipoA e tipoB são pares (nome, parametros) de transformacoes.
    """
    M_ab, _ = compor([tipoA, tipoB])          # A primeiro, depois B  -> B·A
    M_ba, _ = compor([tipoB, tipoA])          # B primeiro, depois A  -> A·B
    r1, r2 = aplicar(M_ab, contornos), aplicar(M_ba, contornos)
    lim = limites_quadrados(limites_dos_objetos([contornos, r1, r2], margem=1.5))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, resultado, M, rotulo in ((ax1, r1, M_ab, "A depois B  (matriz B·A)"),
                                     (ax2, r2, M_ba, "B depois A  (matriz A·B)")):
        desenhar_objeto(ax, contornos, buracos, COR_ORIGINAL, preencher=False, tracejado=True)
        desenhar_objeto(ax, resultado, buracos, COR_FINAL)
        configurar_eixos(ax, lim, rotulo)
        ax.grid(True, linewidth=0.3)
    fig.suptitle("Ordem importa: o produto de matrizes não é comutativo", fontsize=13)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


# ----------------------------------------------------------------------------
# Animação GIF do logo com painel de matriz / determinante / autovalores
# ----------------------------------------------------------------------------

def matriz_no_instante(alvo, t):
    """
    Matriz composta no instante t (0 = identidade, 1 = transformação final).
    Os parâmetros são interpolados linearmente de 'neutro' até o valor-alvo e
    compostos na ordem: rotação, escala, cisalhamento, translação.
    """
    seq = [("rotacao", [alvo["theta"] * t]),
           ("escala", [1 + (alvo["sx"] - 1) * t, 1 + (alvo["sy"] - 1) * t]),
           ("cisalhamento", [alvo["kx"] * t, alvo["ky"] * t]),
           ("translacao", [alvo["tx"] * t, alvo["ty"] * t])]
    M, _ = compor(seq)
    return M


def desenhar_quadro(contornos, buracos, M, lim, t):
    """Desenha um quadro da animação e devolve a imagem (PIL)."""
    A = parte_linear(M)
    det = determinante(A)
    autovalores = autovalores_2x2(A)

    fig = plt.figure(figsize=(9, 4.6))
    ax = fig.add_axes([0.04, 0.08, 0.56, 0.84])       # área do desenho
    ax_txt = fig.add_axes([0.62, 0.08, 0.36, 0.84])   # painel de texto
    ax_txt.axis("off")

    # Desenho: malha deformada, original tracejado e logo transformado.
    desenhar_grade(ax, M, lim)
    desenhar_objeto(ax, contornos, buracos, COR_ORIGINAL, preencher=False, tracejado=True)
    desenhar_objeto(ax, aplicar(M, contornos), buracos, COR_FINAL)
    desenhar_autovetores(ax, M, lim)
    configurar_eixos(ax, lim, f"Logo IFSP  (t = {t:.2f})")

    # Painel de texto: matriz composta, determinante e autovalores.
    sinal = "preserva orientação" if det > EPS else (
        "inverte orientação" if det < -EPS else "achata (det = 0)")
    linhas_autov = "\n".join(f"  λ = {formatar_numero(l, 3)}" for l in autovalores)
    texto = ("Matriz composta M(t)\n"
             f"{formatar_matriz(M, 2)}\n\n"
             f"det(parte linear) = {det:.3f}\n"
             f"({sinal})\n\n"
             f"Autovalores:\n{linhas_autov}")
    ax_txt.text(0.0, 1.0, texto, va="top", ha="left", family="monospace", fontsize=9.5)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=80)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("P", palette=Image.ADAPTIVE)


def gerar_gif(contornos, buracos, alvo, caminho, quadros=48, ms_por_quadro=60):
    """
    Gera o GIF. A animação vai da identidade até a transformação-alvo e volta
    (ida e volta suave), formando um laço contínuo.
    """
    # 1) Calcula a matriz de cada quadro.
    ts, matrizes = [], []
    for i in range(quadros):
        u = i / quadros                              # progresso de 0 a 1
        fase = 1 - abs(2 * u - 1)                    # 0 -> 1 -> 0 (ida e volta)
        t = (1 - math.cos(math.pi * fase)) / 2       # suaviza início e fim
        ts.append(t)
        matrizes.append(matriz_no_instante(alvo, t))
    # 2) Limites FIXOS que cobrem todos os quadros (a câmera não se mexe).
    objetos = [contornos] + [aplicar(M, contornos) for M in matrizes]
    lim = limites_quadrados(limites_dos_objetos(objetos, margem=2.0))
    # 3) Desenha os quadros e salva o GIF.
    imagens = [desenhar_quadro(contornos, buracos, M, lim, t)
               for t, M in zip(ts, matrizes)]
    imagens[0].save(caminho, save_all=True, append_images=imagens[1:],
                    duration=ms_por_quadro, loop=0, disposal=2)
