"""
main.py
-------
Programa principal: Transformações Lineares e Composição Gráfica em 2D e 3D.

Uso:
    python main.py                      -> modo interativo (você digita o texto e as transformações)
    python main.py --demo               -> demonstração completa com a palavra IFSP
    python main.py --demo "SUA PALAVRA" -> demonstração completa com QUALQUER palavra
    python main.py --texto "Olá" --3d --seq "RY 40; E 1 1.5 1; T 2 0 0" --gif
    python main.py --objeto cubo --seq "RZ 45; E 2 1 1"
"""

import argparse
import math
import os
import re
import sys
import unicodedata

from objetos import obter_objeto
from relatorio import gerar_relatorio
from transformacoes import com_pivo
from graficos import grafico_antes_depois, grafico_ordem, gerar_gif

PASTA_SAIDA = "saida"
TEXTO_PADRAO = "IFSP"

# Sequências usadas na demonstração.
DEMO_2D = [("rotacao", [30]), ("escala", [1.3, 0.8]), ("cisalhamento", [0.5, 0]),
           ("translacao", [2, 1])]
DEMO_3D = [("rotacao_y", [50]), ("rotacao_x", [-25]), ("escala", [1.2, 1.2, 1.2]),
           ("translacao", [3, 2, 0])]


# ----------------------------------------------------------------------------
# Leitura e interpretação dos comandos de transformação
# ----------------------------------------------------------------------------

AJUDA_2D = """  R theta [px py]  -> rotação de theta graus (em torno da origem ou do ponto px py)
  E sx sy [px py]  -> escala (negativo = reflexão); opcionalmente em torno de px py
  C kx ky          -> cisalhamento (x' = x + kx*y ; y' = y + ky*x)
  T tx ty          -> translação
  F x | F y        -> reflexão em relação ao eixo x (ou y)
  (aceita vírgula decimal: 1,5 ; várias por linha separadas por ';'; linha vazia termina)"""

AJUDA_3D = """  RX theta [px py pz]   RY theta [...]   RZ theta [...]  -> rotação em torno do eixo x, y ou z
  RA theta ax ay az [px py pz]   -> rotação em torno do eixo (ax, ay, az)
  E sx sy sz [px py pz]          -> escala (negativo = reflexão)
  C kxy kxz kyx kyz kzx kzy      -> cisalhamento 3D (x' = x + kxy*y + kxz*z ; etc.)
  T tx ty tz                     -> translação
  F xy | F xz | F yz             -> reflexão em relação ao plano indicado
  (aceita vírgula decimal: 1,5 ; várias por linha separadas por ';'; linha vazia termina)"""

# comando -> (tipo interno, nº de parâmetros, aceita pivô?)
COMANDOS_2D = {"R": ("rotacao", 1, True), "E": ("escala", 2, True),
               "C": ("cisalhamento", 2, False), "T": ("translacao", 2, False)}
COMANDOS_3D = {"RX": ("rotacao_x", 1, True), "RY": ("rotacao_y", 1, True),
               "RZ": ("rotacao_z", 1, True), "RA": ("rotacao_eixo", 4, True),
               "E": ("escala", 3, True), "C": ("cisalhamento", 6, False),
               "T": ("translacao", 3, False)}
REFLEXOES_2D = {"X": [1, -1], "Y": [-1, 1]}
REFLEXOES_3D = {"XY": [1, 1, -1], "XZ": [1, -1, 1], "YZ": [-1, 1, 1]}


def ler_numeros(partes):
    """Converte textos em números reais (aceita vírgula decimal). Levanta ValueError."""
    numeros = []
    for p in partes:
        try:
            x = float(p.replace(",", "."))
        except ValueError:
            raise ValueError(f"'{p}' não é um número")
        if not math.isfinite(x) or abs(x) > 1e6:
            raise ValueError(f"valor fora do intervalo aceito: {p}")
        numeros.append(x)
    return numeros


def interpretar_comando(texto, dim):
    """
    Interpreta UM comando (ex.: 'R 45', 'E 2 1.5 3 4') e devolve a lista de passos
    [(tipo, parâmetros), ...]. Com pivô, um comando vira 3 passos (T(-p), op, T(p)).
    Levanta ValueError com uma mensagem clara se o comando for inválido.
    """
    m = re.match(r"^\s*([A-Za-z]+)\s*(.*)$", texto)
    if not m:
        raise ValueError("comando vazio ou inválido")
    letra, resto = m.group(1).upper(), m.group(2).split()
    if letra == "F":
        if len(resto) != 1:
            raise ValueError("use F seguido de " + ("x ou y" if dim == 2 else "xy, xz ou yz"))
        tabela = REFLEXOES_2D if dim == 2 else REFLEXOES_3D
        chave = resto[0].upper()
        if chave not in tabela:
            raise ValueError("reflexão inválida; opções: " + ", ".join(k.lower() for k in tabela))
        return [("escala", [float(v) for v in tabela[chave]])]
    tabela = COMANDOS_2D if dim == 2 else COMANDOS_3D
    if letra not in tabela:
        raise ValueError(f"comando '{letra}' inválido para {dim}D")
    tipo, n_parametros, aceita_pivo = tabela[letra]
    numeros = ler_numeros(resto)
    if len(numeros) == n_parametros:
        return [(tipo, numeros)]
    if aceita_pivo and len(numeros) == n_parametros + dim:
        return com_pivo(tipo, numeros[:n_parametros], numeros[n_parametros:])
    esperado = f"{n_parametros} número(s)" + (f" (+ {dim} do pivô)" if aceita_pivo else "")
    raise ValueError(f"'{letra}' espera {esperado}")


def interpretar_sequencia(texto, dim):
    """Interpreta vários comandos separados por ';' e devolve a lista de passos."""
    passos = []
    for pedaco in texto.split(";"):
        if pedaco.strip():
            passos += interpretar_comando(pedaco, dim)
    if not passos:
        raise ValueError("nenhuma transformação informada")
    return passos


# ----------------------------------------------------------------------------
# Entrada interativa
# ----------------------------------------------------------------------------

def entrada(prompt):
    """input() que encerra o programa com educação se o teclado for fechado (Ctrl+D/Ctrl+C)."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrado.")
        sys.exit(0)


def perguntar_sim_nao(prompt):
    """Pergunta [s/N]; devolve True para 's'."""
    return entrada(prompt).strip().lower() in ("s", "sim", "y", "yes")


def escolher_objeto():
    """Menu de objetos. Devolve o objeto (Objeto) já criado."""
    print("Objeto:")
    print("  1) Texto 2D  (QUALQUER palavra ou frase que você digitar)")
    print("  2) Texto 3D  (a mesma palavra, extrudada em volume)")
    print("  3) Quadrado   4) Triângulo   5) Casinha     [2D]")
    print("  6) Cubo       7) Pirâmide                    [3D]")
    opcoes = {"1": "texto", "2": "texto3d", "3": "quadrado", "4": "triangulo",
              "5": "casinha", "6": "cubo", "7": "piramide"}
    while True:
        escolha = entrada("Escolha [1]: ").strip() or "1"
        if escolha in opcoes:
            break
        print("  Opção inválida. Digite um número de 1 a 7.")
    tipo = opcoes[escolha]
    texto = None
    if tipo in ("texto", "texto3d"):
        while True:
            texto = entrada(f"Digite o texto [{TEXTO_PADRAO}]: ").strip() or TEXTO_PADRAO
            try:
                obj, desconhecidos = obter_objeto(tipo, texto)
                break
            except ValueError as erro:
                print(f"  {erro}")
    else:
        obj, desconhecidos = obter_objeto(tipo)
    if desconhecidos:
        print("  Aviso: a fonte não tem " + " ".join(sorted(desconhecidos)) +
              " (desenhado como '?').")
    return obj


def ler_sequencia(dim):
    """Lê do teclado a sequência de transformações (na ordem de aplicação)."""
    print(f"\nDigite as transformações {dim}D, UMA por linha, na ordem de aplicação:")
    print(AJUDA_2D if dim == 2 else AJUDA_3D)
    sequencia = []
    while True:
        linha = entrada(f"T{len(sequencia) + 1}> ").strip()
        if linha == "":
            if sequencia:
                return sequencia
            print("  Informe pelo menos uma transformação.")
            continue
        try:
            sequencia += interpretar_sequencia(linha, dim)
        except ValueError as erro:
            print(f"  Entrada inválida: {erro}")


# ----------------------------------------------------------------------------
# Execução
# ----------------------------------------------------------------------------

def prefixo_de(obj):
    """Nome de arquivo seguro a partir do nome do objeto (sem acentos nem símbolos)."""
    base = unicodedata.normalize("NFKD", obj.nome).encode("ascii", "ignore").decode()
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()[:24] or "objeto"
    return f"{base}_{obj.dim}d"


def executar(obj, sequencia, prefixo, pasta=PASTA_SAIDA, gif=False, imprimir=True):
    """Gera relatório (txt) e gráfico (png), e opcionalmente o GIF, para um objeto e uma sequência."""
    os.makedirs(pasta, exist_ok=True)
    texto, M = gerar_relatorio(obj, sequencia)
    caminho_txt = os.path.join(pasta, f"{prefixo}_relatorio.txt")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    caminho_png = os.path.join(pasta, f"{prefixo}_grafico.png")
    grafico_antes_depois(obj, M, f"Objeto: {obj.nome}", caminho_png)
    if imprimir:
        print(texto)
    gerados = [caminho_txt, caminho_png]
    if gif:
        caminho_gif = os.path.join(pasta, f"{prefixo}_animado.gif")
        print("Gerando GIF animado (pode levar alguns segundos)...")
        gerar_gif(obj, sequencia, caminho_gif)
        gerados.append(caminho_gif)
    print("Arquivos gerados: " + ", ".join(gerados))
    return M


def modo_interativo(pasta):
    """Fluxo completo com entrada do usuário."""
    print("=== Transformações Lineares 2D/3D (coordenadas homogêneas) ===\n")
    while True:
        obj = escolher_objeto()
        sequencia = ler_sequencia(obj.dim)
        gif = perguntar_sim_nao("Gerar também o GIF animado? [s/N]: ")
        executar(obj, sequencia, prefixo_de(obj), pasta, gif)
        if not perguntar_sim_nao("\nFazer outro? [s/N]: "):
            break
        print()


def modo_demo(texto, pasta):
    """
    Demonstração completa com o texto dado: relatório + gráfico em 2D e 3D,
    comparação da ordem das transformações e GIFs animados.
    """
    os.makedirs(pasta, exist_ok=True)
    for dim, tipo, seq, passoA, passoB in (
            (2, "texto", DEMO_2D, ("rotacao", [45]), ("escala", [1.6, 0.6])),
            (3, "texto3d", DEMO_3D, ("rotacao_y", [45]), ("escala", [1.6, 0.6, 1.0]))):
        obj, desconhecidos = obter_objeto(tipo, texto)
        if desconhecidos:
            print("Aviso: a fonte não tem " + " ".join(sorted(desconhecidos)))
        executar(obj, seq, f"demo_{dim}d", pasta, gif=False, imprimir=False)
        grafico_ordem(obj, passoA, passoB, os.path.join(pasta, f"demo_ordem_{dim}d.png"))
        print(f"Gerado: {pasta}/demo_ordem_{dim}d.png")
        gerar_gif(obj, seq, os.path.join(pasta, f"demo_{dim}d_animado.gif"),
                  quadros=48 if dim == 2 else 40)
        print(f"Gerado: {pasta}/demo_{dim}d_animado.gif")


def main():
    ap = argparse.ArgumentParser(description="Transformações lineares 2D/3D com texto digitado.")
    ap.add_argument("--demo", nargs="?", const=TEXTO_PADRAO, metavar="TEXTO",
                    help="demonstração completa (texto opcional; padrão: IFSP)")
    ap.add_argument("--texto", help="texto a transformar (qualquer palavra ou frase)")
    ap.add_argument("--3d", dest="tres_d", action="store_true", help="com --texto: extrudar em 3D")
    ap.add_argument("--objeto", choices=["quadrado", "triangulo", "casinha", "cubo", "piramide"],
                    help="objeto pronto em vez de texto")
    ap.add_argument("--seq", help='transformações separadas por ";", ex.: "R 30; E 2 1; T 1 0"')
    ap.add_argument("--gif", action="store_true", help="gerar também o GIF animado")
    ap.add_argument("--saida", default=PASTA_SAIDA, help="pasta de saída (padrão: saida)")
    args = ap.parse_args()

    if args.demo is not None:
        modo_demo(args.demo, args.saida)
    elif args.texto or args.objeto:
        if args.texto:
            obj, desconhecidos = obter_objeto("texto3d" if args.tres_d else "texto", args.texto)
            if desconhecidos:
                print("Aviso: a fonte não tem " + " ".join(sorted(desconhecidos)))
        else:
            obj, _ = obter_objeto(args.objeto)
        sequencia = (interpretar_sequencia(args.seq, obj.dim) if args.seq
                     else (DEMO_2D if obj.dim == 2 else DEMO_3D))
        executar(obj, sequencia, prefixo_de(obj), args.saida, args.gif)
    else:
        modo_interativo(args.saida)


if __name__ == "__main__":
    try:
        main()
    except ValueError as erro:
        print(f"Erro: {erro}")
        sys.exit(1)
