"""
gerar_figuras.py
----------------
Gera as figuras usadas no relatório PDF (pasta saida/figuras/):
  - folha de caracteres da fonte vetorial;
  - gráficos dos casos de teste 1 a 4;
  - demonstrações 2D e 3D e a comparação de ordem das transformações.

Execute:  python gerar_figuras.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from objetos import (quadrado_unitario, triangulo, cubo, texto_2d, texto_3d)
from transformacoes import compor
from graficos import (grafico_antes_depois, grafico_ordem, desenhar_objeto_2d,
                      COR_ORIGINAL)

PASTA = os.path.join("saida", "figuras")


def folha_de_caracteres(caminho):
    """Desenha todos os caracteres da fonte vetorial (mostra que ela é feita só de vértices)."""
    linhas = ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "0123456789 .,:!?",
              "+-=/_'() ÁÀÂÃÄÇ É Õ Ü"]
    fig, eixos = plt.subplots(len(linhas), 1, figsize=(11, 7.5))
    for ax, texto in zip(eixos, linhas):
        obj, _ = texto_2d(texto)
        desenhar_objeto_2d(ax, obj, COR_ORIGINAL)
        ax.set_xlim(min(obj.V[0]) - 1, max(obj.V[0]) + 1)
        ax.set_ylim(min(obj.V[1]) - 1, max(obj.V[1]) + 1)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(caminho, dpi=120)
    plt.close(fig)


def main():
    os.makedirs(PASTA, exist_ok=True)
    p = lambda nome: os.path.join(PASTA, nome)

    folha_de_caracteres(p("fonte.png"))

    # Casos de teste (mesmas sequências de testes.py)
    M, _ = compor([("rotacao", [90]), ("escala", [2, 3]), ("translacao", [1, 1])])
    grafico_antes_depois(quadrado_unitario(), M,
                         "Caso 1: quadrado, R(90°), E(2,3), T(1,1)", p("caso1.png"))
    M, _ = compor([("cisalhamento", [1, 0]), ("escala", [2, 1]), ("translacao", [-1, 2])])
    grafico_antes_depois(triangulo(), M,
                         "Caso 2: triângulo, C(1,0), E(2,1), T(-1,2)", p("caso2.png"))
    M, _ = compor([("rotacao_z", [90]), ("escala", [2, 1, 3]), ("translacao", [1, 2, 3])])
    grafico_antes_depois(cubo(), M,
                         "Caso 3: cubo, Rz(90°), E(2,1,3), T(1,2,3)", p("caso3.png"))
    M, _ = compor([("escala", [2, 3])])
    grafico_antes_depois(texto_2d("T")[0], M, 'Caso 4: texto "T", E(2,3)', p("caso4.png"))

    # Demonstrações com texto digitado
    seq2 = [("rotacao", [30]), ("escala", [1.3, 0.8]), ("cisalhamento", [0.5, 0]),
            ("translacao", [2, 1])]
    seq3 = [("rotacao_y", [50]), ("rotacao_x", [-25]), ("escala", [1.2, 1.2, 1.2]),
            ("translacao", [3, 2, 0])]
    M, _ = compor(seq2)
    grafico_antes_depois(texto_2d("Álgebra Linear")[0], M,
                         'Texto digitado: "Álgebra Linear" (2D)', p("demo2d.png"))
    M, _ = compor(seq3)
    grafico_antes_depois(texto_3d("IFSP")[0], M, 'Texto digitado: "IFSP" (3D)', p("demo3d.png"))
    grafico_ordem(texto_2d("IFSP")[0], ("rotacao", [45]), ("escala", [1.6, 0.6]),
                  p("ordem2d.png"))
    grafico_ordem(texto_3d("IFSP")[0], ("rotacao_y", [45]), ("escala", [1.6, 0.6, 1.0]),
                  p("ordem3d.png"))
    print("Figuras geradas em", PASTA)


if __name__ == "__main__":
    main()
