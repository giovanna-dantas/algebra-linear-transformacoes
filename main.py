"""
main.py
-------
Programa principal: Transformações Lineares e Composição Gráfica 2D.

Uso:
    python main.py            -> modo interativo (o usuário escolhe tudo)
    python main.py --demo     -> demonstração automática com o logo IFSP
                                 (gera gráficos, relatório e GIF em ./saida)
"""

import os
import sys

from objetos import obter_objeto
from transformacoes import compor
from relatorio import gerar_relatorio
from graficos import grafico_antes_depois, grafico_ordem, gerar_gif

PASTA_SAIDA = "saida"


def ler_numeros(texto, quantidade):
    """Lê 'quantidade' números reais de uma linha de texto; devolve None se inválido."""
    partes = texto.replace(",", " ").split()
    if len(partes) != quantidade:
        return None
    try:
        return [float(p) for p in partes]
    except ValueError:
        return None


def escolher_objeto():
    """Pergunta qual objeto usar e devolve (nome, contornos, buracos)."""
    print("Objetos disponíveis: quadrado, triangulo, casinha, logo")
    while True:
        nome = input("Escolha o objeto [logo]: ").strip().lower() or "logo"
        try:
            contornos, buracos = obter_objeto(nome)
            return nome, contornos, buracos
        except ValueError:
            print("  Objeto inválido, tente novamente.")


def ler_sequencia():
    """
    Lê do teclado a sequência de transformações (na ordem de aplicação).
    Formatos:  R angulo | E sx sy | C kx ky | T tx ty | (linha vazia termina)
    """
    print("\nDigite as transformações, UMA por linha, na ordem de aplicação:")
    print("  R theta      -> rotação de theta graus")
    print("  E sx sy      -> escala")
    print("  C kx ky      -> cisalhamento (x' = x + kx*y ; y' = y + ky*x)")
    print("  T tx ty      -> translação")
    print("  (linha vazia para terminar)")
    sequencia = []
    while True:
        linha = input(f"T{len(sequencia) + 1}> ").strip()
        if linha == "":
            if sequencia:
                return sequencia
            print("  Informe pelo menos uma transformação.")
            continue
        letra, resto = linha[0].upper(), linha[1:]
        if letra == "R" and ler_numeros(resto, 1):
            sequencia.append(("rotacao", ler_numeros(resto, 1)))
        elif letra == "E" and ler_numeros(resto, 2):
            sequencia.append(("escala", ler_numeros(resto, 2)))
        elif letra == "C" and ler_numeros(resto, 2):
            sequencia.append(("cisalhamento", ler_numeros(resto, 2)))
        elif letra == "T" and ler_numeros(resto, 2):
            sequencia.append(("translacao", ler_numeros(resto, 2)))
        else:
            print("  Entrada inválida. Exemplos: 'R 45', 'E 2 1.5', 'C 1 0', 'T 3 -1'")


def executar(nome, contornos, buracos, sequencia, prefixo):
    """Gera relatório (txt) e gráfico (png) para um objeto e uma sequência."""
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    texto, M = gerar_relatorio(nome, contornos, sequencia)
    caminho_txt = os.path.join(PASTA_SAIDA, f"{prefixo}_relatorio.txt")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    caminho_png = os.path.join(PASTA_SAIDA, f"{prefixo}_grafico.png")
    grafico_antes_depois(contornos, buracos, M,
                         f"Objeto: {nome}", caminho_png)
    print(texto)
    print(f"Arquivos gerados: {caminho_txt} e {caminho_png}")
    return M


def modo_interativo():
    """Fluxo completo com entrada do usuário."""
    print("=== Transformações Lineares 2D (coordenadas homogêneas) ===\n")
    nome, contornos, buracos = escolher_objeto()
    sequencia = ler_sequencia()
    executar(nome, contornos, buracos, sequencia, "interativo")


def modo_demo():
    """Demonstração automática: gráfico, relatório, comparação de ordem e GIF."""
    nome, contornos, buracos = "logo", *obter_objeto("logo")
    # Sequência de exemplo: rotação, escala, cisalhamento, translação.
    sequencia = [("rotacao", [30]), ("escala", [1.3, 0.8]),
                 ("cisalhamento", [0.5, 0]), ("translacao", [2, 1])]
    executar(nome, contornos, buracos, sequencia, "demo_logo")

    # Comparação A·B x B·A (não comutatividade).
    grafico_ordem(contornos, buracos, ("rotacao", [45]), ("escala", [1.6, 0.6]),
                  os.path.join(PASTA_SAIDA, "demo_ordem.png"))
    print("Gerado: saida/demo_ordem.png")

    # GIF animado: da identidade até a transformação-alvo e de volta.
    alvo = {"theta": 60, "sx": 1.4, "sy": 0.8, "kx": 0.6, "ky": 0.0, "tx": 0, "ty": 0}
    gerar_gif(contornos, buracos, alvo, os.path.join(PASTA_SAIDA, "logo_animado.gif"))
    print("Gerado: saida/logo_animado.gif")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        modo_demo()
    else:
        modo_interativo()
