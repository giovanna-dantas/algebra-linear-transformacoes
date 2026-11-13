"""
gerar_figuras.py
----------------
Gera os gráficos dos dois casos de teste (usados no relatório).
Execute:  python gerar_figuras.py
"""

import os

from objetos import quadrado_unitario, triangulo
from transformacoes import compor
from graficos import grafico_antes_depois

PASTA = "saida"


def figura_caso(nome_arquivo, contornos, sequencia, titulo):
    """Compõe a sequência e salva o gráfico antes/depois do caso de teste."""
    M, _ = compor(sequencia)
    grafico_antes_depois(contornos, [], M, titulo, os.path.join(PASTA, nome_arquivo))


if __name__ == "__main__":
    os.makedirs(PASTA, exist_ok=True)
    # Caso 1: quadrado; rotação 90°, escala (2,3), translação (1,1).
    figura_caso("teste1_grafico.png", quadrado_unitario(),
                [("rotacao", [90]), ("escala", [2, 3]), ("translacao", [1, 1])],
                "Caso de teste 1: quadrado")
    # Caso 2: triângulo; cisalhamento (1,0), escala (2,1), translação (-1,2).
    figura_caso("teste2_grafico.png", triangulo(),
                [("cisalhamento", [1, 0]), ("escala", [2, 1]), ("translacao", [-1, 2])],
                "Caso de teste 2: triângulo")
    print("Figuras geradas em", PASTA)
