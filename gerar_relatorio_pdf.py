"""
gerar_relatorio_pdf.py
----------------------
Gera o relatório em PDF (Relatorio_Transformacoes_Lineares.pdf) com:
capa, folha de rosto, teoria (com exemplos de aplicação), aplicação em Sistemas
de Informação, implementação, execução do código, casos de teste (entrada /
saída esperada / saída obtida) e explicação dos resultados.

As tabelas dos testes são montadas a partir da saída REAL de testes.py, e as
figuras vêm de gerar_figuras.py. Requer: reportlab (só para montar o PDF).

Execute (depois de gerar_figuras.py e main.py --demo):
    python gerar_relatorio_pdf.py
"""

import os
import subprocess
import sys
from xml.sax.saxutils import escape

import matplotlib
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

SAIDA_PDF = "Relatorio_Transformacoes_Lineares.pdf"
FIG = os.path.join("saida", "figuras")

AUTORES = ["Giovanna Dantas de Souza", "Júlia Santana dos Santos",
           "Lucas Vinícius Barbosa da Silva"]
TITULO = "Transformações Lineares e Composição Gráfica em 2D e 3D"
SUBTITULO = ("Matrizes de rotação, escala, cisalhamento e translação homogênea aplicadas a "
             "qualquer palavra digitada, em plano e em espaço")

# ----------------------------------------------------------------------------
# Fontes (DejaVu acompanha o Matplotlib e tem θ, λ, ·, ×, ±, √ etc.)
# ----------------------------------------------------------------------------
_dir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
for nome, arq in (("Serif", "DejaVuSerif.ttf"), ("Serif-Bold", "DejaVuSerif-Bold.ttf"),
                  ("Serif-Italic", "DejaVuSerif-Italic.ttf"),
                  ("Serif-BoldItalic", "DejaVuSerif-BoldItalic.ttf"),
                  ("Mono", "DejaVuSansMono.ttf"), ("Mono-Bold", "DejaVuSansMono-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(nome, os.path.join(_dir, arq)))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-Italic", boldItalic="Serif-BoldItalic")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-Bold",
                              italic="Mono", boldItalic="Mono-Bold")

# ----------------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------------
CORPO = ParagraphStyle("corpo", fontName="Serif", fontSize=10.5, leading=15,
                       alignment=TA_JUSTIFY, spaceAfter=6)
H1 = ParagraphStyle("h1", fontName="Serif-Bold", fontSize=14.5, leading=18,
                    spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1b3a5c"))
H2 = ParagraphStyle("h2", fontName="Serif-Bold", fontSize=11.5, leading=15,
                    spaceBefore=9, spaceAfter=4, textColor=colors.HexColor("#1b3a5c"))
LEGENDA = ParagraphStyle("legenda", fontName="Serif-Italic", fontSize=9, leading=12,
                         alignment=TA_CENTER, spaceAfter=10, textColor=colors.HexColor("#333333"))
EQ = ParagraphStyle("eq", parent=CORPO, alignment=TA_CENTER, fontSize=11, spaceBefore=3,
                    spaceAfter=7)
CELULA = ParagraphStyle("celula", fontName="Serif", fontSize=8.3, leading=10.5,
                        alignment=TA_LEFT)
CELULA_B = ParagraphStyle("celula_b", parent=CELULA, fontName="Serif-Bold")
CELULA_M = ParagraphStyle("celula_m", parent=CELULA, fontName="Mono", fontSize=7.4, leading=9.4)
CAPA = ParagraphStyle("capa", fontName="Serif-Bold", fontSize=12, leading=16, alignment=TA_CENTER)
CAPA_G = ParagraphStyle("capa_g", fontName="Serif-Bold", fontSize=19, leading=24,
                        alignment=TA_CENTER)
CAPA_N = ParagraphStyle("capa_n", fontName="Serif", fontSize=11.5, leading=16,
                        alignment=TA_CENTER)
BULLET = ParagraphStyle("bullet", parent=CORPO, leftIndent=14, bulletIndent=2, spaceAfter=3)
COR_TAB = colors.HexColor("#1b3a5c")


def P(texto, estilo=CORPO):
    """Parágrafo (aceita marcação <b>, <i>, <sub>, <super>)."""
    return Paragraph(texto, estilo)


def bullets(itens):
    """Lista de marcadores."""
    return [Paragraph(t, BULLET, bulletText="•") for t in itens]


def fmt(x):
    """Número no padrão brasileiro: 6, 0,333 (textos simbólicos passam sem mudar)."""
    if isinstance(x, str):
        return x
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.3f}".replace(".", ",")


def matriz(M, tam=10):
    """Matriz desenhada com colchetes (tabela com bordas esquerda e direita)."""
    dados = [[fmt(x) for x in linha] for linha in M]
    t = Table(dados, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Serif"), ("FONTSIZE", (0, 0), (-1, -1), tam),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEBEFORE", (0, 0), (0, -1), 1.1, colors.black),
        ("LINEAFTER", (-1, 0), (-1, -1), 1.1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    return t


def linha_de_matrizes(itens, tam=9.5):
    """Várias matrizes lado a lado, cada uma com um título em cima."""
    cab = [P(f"<b>{t}</b>", ParagraphStyle("t", parent=CELULA, alignment=TA_CENTER, fontSize=9))
           for t, _ in itens]
    corpo = [matriz(M, tam) for _, M in itens]
    t = Table([cab, corpo], hAlign="CENTER")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def figura(arquivo, legenda, largura=16.4 * cm, altura_max=11.5 * cm):
    """Imagem proporcional (limitada em largura e altura) com legenda."""
    caminho = os.path.join(FIG, arquivo) if not os.path.isabs(arquivo) else arquivo
    w, h = PILImage.open(caminho).size
    larg = largura
    alt = larg * h / w
    if alt > altura_max:
        alt = altura_max
        larg = alt * w / h
    return KeepTogether([Image(caminho, width=larg, height=alt), P(legenda, LEGENDA)])


def tabela(dados, larguras, cabecalho=True, estilo_celula=CELULA):
    """Tabela com quebra de linha em cada célula (strings viram parágrafos)."""
    linhas = []
    for i, linha in enumerate(dados):
        est = CELULA_B if (cabecalho and i == 0) else estilo_celula
        linhas.append([c if not isinstance(c, str) else Paragraph(c, est) for c in linha])
    t = Table(linhas, colWidths=larguras, repeatRows=1 if cabecalho else 0, hAlign="CENTER")
    estilo = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if cabecalho:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde7f2"))]
    t.setStyle(TableStyle(estilo))
    return t


def codigo(texto, tam=7.6):
    """Bloco de texto monoespaçado."""
    est = ParagraphStyle("cod", fontName="Mono", fontSize=tam, leading=tam + 2.2,
                         backColor=colors.HexColor("#f4f4f4"), borderPadding=5,
                         leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=10)
    return Preformatted(texto, est)


# ----------------------------------------------------------------------------
# Testes: executa testes.py e lê a saída real
# ----------------------------------------------------------------------------

def executar_testes():
    """Roda testes.py e devolve [(titulo_do_caso, [(item, esperado, obtido, ok), ...]), ...]."""
    r = subprocess.run([sys.executable, "testes.py"], capture_output=True, text=True,
                       encoding="utf-8")
    casos, atual, item = [], None, None
    for linha in r.stdout.splitlines():
        if linha.startswith("CASO DE TESTE"):
            atual = (linha.split(":", 1)[1].strip() if ":" in linha else linha, [])
            casos.append(atual)
        elif linha.startswith("RESUMO"):
            break
        elif atual is not None and linha.startswith("    esperado:"):
            item[1] = linha.split(":", 1)[1].strip()
        elif atual is not None and linha.startswith("    obtido"):
            item[2] = linha.split(":", 1)[1].strip()
        elif atual is not None and linha.startswith("    ->"):
            item[3] = "OK" in linha
        elif atual is not None and linha.startswith("  ") and linha.strip():
            item = [linha.strip(), "", "", False]
            atual[1].append(item)
    return casos, r.returncode == 0


def tabela_de_testes(itens):
    """Tabela Item | Esperado | Obtido | Resultado para um caso."""
    dados = [["Verificação", "Saída esperada (à mão)", "Saída obtida (programa)", "Resultado"]]
    for nome, esp, obt, ok in itens:
        dados.append([escape(nome), Paragraph(escape(esp), CELULA_M),
                      Paragraph(escape(obt), CELULA_M),
                      Paragraph("<b>OK</b>" if ok else "<b>FALHOU</b>", CELULA)])
    return tabela(dados, [3.4 * cm, 5.3 * cm, 5.3 * cm, 2.6 * cm])


# ----------------------------------------------------------------------------
# Rodapé com numeração (capa e folha de rosto sem número)
# ----------------------------------------------------------------------------

def rodape(canvas, doc):
    if doc.page > 2:
        canvas.saveState()
        canvas.setFont("Serif", 9)
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.4 * cm, str(doc.page))
        canvas.restoreState()


# ----------------------------------------------------------------------------
# Conteúdo
# ----------------------------------------------------------------------------

def capa():
    e = [Spacer(1, 0.4 * cm),
         P("INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA<br/>DE SÃO PAULO<br/>"
           "CAMPUS SÃO PAULO", CAPA),
         Spacer(1, 2.6 * cm)]
    e += [P(a, CAPA_N) for a in AUTORES]
    e += [Spacer(1, 3.2 * cm), P(TITULO, CAPA_G), Spacer(1, 0.4 * cm),
          P(SUBTITULO, CAPA_N), Spacer(1, 1.6 * cm),
          P("Tema 4 — Transformações Lineares e Composição Gráfica em 2D/3D", CAPA_N),
          Spacer(1, 4.4 * cm), P("São Paulo, SP<br/>2026", CAPA_N), PageBreak()]
    return e


def folha_de_rosto():
    est = ParagraphStyle("nota", parent=CAPA_N, alignment=TA_JUSTIFY, leftIndent=7.5 * cm,
                         fontSize=10.5, leading=14)
    e = [Spacer(1, 0.4 * cm)]
    e += [P(a, CAPA_N) for a in AUTORES]
    e += [Spacer(1, 3.4 * cm), P(TITULO, CAPA_G), Spacer(1, 3.2 * cm),
          P("Trabalho apresentado à disciplina de Vetores, Geometria Analítica e Álgebra "
            "Linear do Instituto Federal de Educação, Ciência e Tecnologia Campus São Paulo "
            "como nota parcial para aprovação na disciplina do bacharelado de Sistemas de "
            "Informação.<br/>Professor: Josceli Maria Tenorio", est),
          Spacer(1, 5.2 * cm), P("São Paulo, SP 2026", CAPA_N), PageBreak()]
    return e


def secao_introducao():
    e = [P("1. Introdução e objetivos", H1),
         P("Este trabalho implementa, em Python 3 e <b>sem NumPy nem qualquer pacote que resolva "
           "a álgebra linear</b>, um programa de <b>transformações lineares e composição gráfica "
           "em 2D e 3D</b>. Um objeto é modelado por uma <b>matriz de coordenadas de vértices</b>; "
           "o usuário informa uma sequência de transformações (rotação, escala, cisalhamento, "
           "translação); o programa calcula a <b>matriz composta</b> por multiplicação matricial, "
           "aplica-a ao objeto, desenha o estado inicial e o final e gera um relatório com as "
           "matrizes intermediárias e a matriz final."),
         P("O programa trabalha com <b>qualquer palavra ou frase digitada no terminal</b>: uma "
           "fonte vetorial própria converte cada caractere em polígonos (vértices), de modo que "
           "o texto vira um objeto como outro qualquer, em 2D ou extrudado em 3D. Os cálculos "
           "matemáticos (produto de matrizes, determinante, inversa, autovalores, produtos "
           "escalar, vetorial e misto) estão escritos explicitamente no código; o Matplotlib e o "
           "Pillow são usados apenas para <i>desenhar</i> polígonos já calculados."),
         P("Além do que o enunciado pede, o projeto inclui:", CORPO)]
    e += bullets([
        "<b>Qualquer texto digitado</b> (letras, números, pontuação e acentos), no lugar do logo fixo;",
        "<b>3D completo</b> com matrizes homogêneas 4×4, rotações em x, y, z e em torno de eixo "
        "arbitrário (fórmula de Rodrigues) e cisalhamento 3D;",
        "<b>renderizador 3D próprio</b> (câmera por rotações, perspectiva, faces visíveis pelo produto "
        "vetorial, iluminação pelo produto escalar);",
        "<b>matriz inversa</b> por Gauss-Jordan, com verificação M·M<super>-1</super> = I e recuperação do "
        "objeto original;",
        "verificação de que <b>det(A) × área (ou volume) antes = área (ou volume) depois</b>;",
        "<b>autovalores e autovetores 2×2 e 3×3</b>, desenhados nos gráficos;",
        "rotação e escala <b>em torno de um ponto qualquer</b> (pivô);",
        "<b>GIFs animados</b> em 2D e 3D e <b>8 casos de teste</b> com saídas calculadas à mão.",
    ])
    req = [["Requisito", "Onde é atendido"],
           ["Modelar o objeto por matriz de coordenadas de vértices", "objetos.py: classe Objeto (matriz V de ordem n × N; cada coluna é um vértice)"],
           ["Aplicar sequência de transformações customizadas (θ, sx, sy, cisalhamento)", "main.py (entrada) e transformacoes.py (matrizes)"],
           ["Matriz resultante por multiplicação das individuais", "transformacoes.compor() com matrizes.multiplicar()"],
           ["Representações gráficas do estado inicial e final", "graficos.py (2D e 3D, GIF animado)"],
           ["Relatório com matrizes intermediárias e composta final", "relatorio.py (arquivo .txt) e este PDF"],
           ["Código com funções básicas, funções separadas e comentários", "7 módulos; nenhum pacote resolve a álgebra linear"],
           ["Relatório PDF: capa, teoria, aplicação, execução e explicação", "Este documento"],
           ["2 casos de teste com entrada e saída esperada", "Seção 6 (casos 1 e 2 obrigatórios + 6 adicionais)"]]
    e += [Spacer(1, 4), tabela(req, [7.4 * cm, 9.2 * cm])]
    return e


def secao_teoria():
    e = [P("2. Fundamentação teórica", H1)]
    # 2.1
    e += [P("2.1 Objeto como matriz de vértices", H2),
          P("Um objeto com N vértices em R<super>n</super> (n = 2 no plano, n = 3 no espaço) é "
            "representado pela matriz <b>V</b> de ordem n × N, em que cada <b>coluna</b> é o vetor de "
            "posição de um vértice. Uma lista de faces (índices de colunas) diz quais vértices "
            "formam cada polígono. Por exemplo, o quadrado unitário é:"),
          matriz([[0, 1, 1, 0], [0, 0, 1, 1]]),
          P("Transformar o objeto é multiplicar: V′ = A·V. A mesma matriz age sobre todos os "
            "vértices de uma só vez, e as faces não mudam.")]
    # 2.2
    e += [P("2.2 Transformações lineares no plano", H2),
          P("Uma transformação T é <b>linear</b> se T(u + v) = T(u) + T(v) e T(k·u) = k·T(u). Toda "
            "transformação linear de R<super>2</super> é dada por uma matriz 2×2. As três do "
            "trabalho são (θ em graus, sx e sy fatores de escala, kx e ky constantes de "
            "cisalhamento):"),
          linha_de_matrizes([("Rotação R(θ)", [["cos θ", "−sen θ"], ["sen θ", "cos θ"]]),
                             ("Escala E(sx, sy)", [["sx", "0"], ["0", "sy"]]),
                             ("Cisalhamento C(kx, ky)", [["1", "kx"], ["ky", "1"]])]),
          P("Exemplo: R(90°) leva (1, 0) em (0, 1); E(2, 3) leva (1, 1) em (2, 3); C(1, 0) leva "
            "(x, y) em (x + y, y), deslizando as linhas horizontais. Um fator negativo na escala "
            "produz uma <b>reflexão</b>: E(1, −1) espelha o objeto em relação ao eixo x.")]
    # 2.3
    e += [P("2.3 Coordenadas homogêneas e translação", H2),
          P("A translação por t = (tx, ty) <b>não é linear</b>, pois move a origem. Para tratá-la como "
            "produto de matrizes, acrescenta-se uma coordenada 1 a cada ponto: (x, y) → (x, y, 1)<super>T</super>. "
            "Com isso, todas as transformações do plano viram matrizes 3×3 que se compõem por "
            "multiplicação; no espaço, matrizes 4×4:"),
          linha_de_matrizes([("Forma geral 2D (3×3)", [["a", "b", "tx"], ["c", "d", "ty"], ["0", "0", "1"]]),
                             ("Translação 3D (4×4)", [["1", "0", "0", "tx"], ["0", "1", "0", "ty"],
                                                      ["0", "0", "1", "tz"], ["0", "0", "0", "1"]])]),
          P("O bloco A (parte linear) contém rotação, escala e cisalhamento; a última coluna "
            "contém a translação t. Na prática, é a mesma estrutura que o CSS usa em "
            "matrix(a, b, c, d, tx, ty), onde (a, b) forma a primeira coluna e (c, d) a segunda.")]
    # 2.4
    e += [P("2.4 Composição e não comutatividade", H2),
          P("Se as transformações T<sub>1</sub>, T<sub>2</sub>, …, T<sub>n</sub> são aplicadas "
            "<b>nessa ordem</b> a um ponto p (vetor coluna), então p′ = T<sub>n</sub>(…(T<sub>2</sub>"
            "(T<sub>1</sub>·p))…), isto é:"),
          P("<b>M = T<sub>n</sub> · … · T<sub>2</sub> · T<sub>1</sub></b>", EQ),
          P("A primeira transformação aplicada fica <b>mais à direita</b>. O produto de matrizes é "
            "associativo, mas <b>não comutativo</b>: em geral M<sub>1</sub>·M<sub>2</sub> ≠ "
            "M<sub>2</sub>·M<sub>1</sub>. Exemplo (Caso 1): rotação de 90°, depois escala (2, 3), "
            "depois translação (1, 1). Como E·R = [[0, −2], [3, 0]], a matriz composta é:"),
          linha_de_matrizes([("T(1,1)", [[1, 0, 1], [0, 1, 1], [0, 0, 1]]),
                             ("E(2,3)", [[2, 0, 0], [0, 3, 0], [0, 0, 1]]),
                             ("R(90°)", [[0, -1, 0], [1, 0, 0], [0, 0, 1]]),
                             ("M = T·E·R", [[0, -2, 1], [3, 0, 1], [0, 0, 1]])], 9),
          P("O programa guarda cada matriz individual e cada matriz <b>acumulada</b> "
            "(M<sub>k</sub> = T<sub>k</sub>·M<sub>k−1</sub>), que aparecem no relatório de execução.")]
    # 2.5
    e += [P("2.5 Transformações em 3D", H2),
          P("No espaço, a rotação ocorre em torno de um eixo (regra da mão direita). Os blocos 3×3 "
            "das rotações em torno de x, y e z são:"),
          linha_de_matrizes([("R<sub>x</sub>(θ)", [["1", "0", "0"], ["0", "cos θ", "−sen θ"], ["0", "sen θ", "cos θ"]]),
                             ("R<sub>y</sub>(θ)", [["cos θ", "0", "sen θ"], ["0", "1", "0"], ["−sen θ", "0", "cos θ"]]),
                             ("R<sub>z</sub>(θ)", [["cos θ", "−sen θ", "0"], ["sen θ", "cos θ", "0"], ["0", "0", "1"]])], 9),
          P("Para um eixo arbitrário de direção unitária k = (k<sub>x</sub>, k<sub>y</sub>, k<sub>z</sub>), "
            "vale a <b>fórmula de Rodrigues</b>:"),
          P("R = cos θ · I + sen θ · [k]<sub>×</sub> + (1 − cos θ) · k·k<super>T</super>, "
            "com [k]<sub>×</sub> = [[0, −k<sub>z</sub>, k<sub>y</sub>], [k<sub>z</sub>, 0, −k<sub>x</sub>], "
            "[−k<sub>y</sub>, k<sub>x</sub>, 0]]", EQ),
          P("O cisalhamento 3D tem seis constantes (x′ = x + k<sub>xy</sub>·y + k<sub>xz</sub>·z, e "
            "analogamente em y e z) e a escala 3D tem três fatores. Para girar ou escalar em torno de "
            "um <b>pivô</b> p qualquer (e não da origem), usa-se M = T(p)·Op·T(−p): leva-se o pivô à "
            "origem, aplica-se a operação e traz-se o pivô de volta.")]
    # 2.6
    e += [P("2.6 Determinante: variação de área e de volume", H2),
          P("O determinante da parte linear A é o <b>fator pelo qual áreas (2D) ou volumes (3D) são "
            "multiplicados</b>: |det A| é o fator de escala e o sinal indica a orientação (det &lt; 0 "
            "significa que houve reflexão). Como a última linha de M é (0, …, 0, 1), det M = det A. "
            "O programa calcula o determinante por <b>expansão de cofatores</b> (Laplace). No Caso 1, "
            "det A = det [[0, −2], [3, 0]] = 0·0 − (−2)·3 = 6: o quadrado de área 1 vira uma figura "
            "de área 6. O programa confere isso calculando a área final pela fórmula do cadarço (2D) "
            "e o volume pelo produto misto (3D).")]
    # 2.7
    e += [P("2.7 Matriz inversa", H2),
          P("Desfazer a transformação é aplicar M<super>-1</super>. O programa a calcula por "
            "<b>eliminação de Gauss-Jordan</b> sobre [M | I], com pivoteamento parcial. Em forma de "
            "blocos, M<super>-1</super> = [[A<super>-1</super>, −A<super>-1</super>·t], [0, 1]]. Pela "
            "propriedade da inversa do produto:"),
          P("<b>M<super>-1</super> = T<sub>1</sub><super>-1</super> · T<sub>2</sub><super>-1</super> · … · "
            "T<sub>n</sub><super>-1</super></b>", EQ),
          P("(as inversas aparecem na ordem contrária). O programa verifica M·M<super>-1</super> = I, "
            "confere as duas formas de obter M<super>-1</super> e aplica M<super>-1</super> ao objeto final "
            "para recuperar o original. Se det = 0 (por exemplo, escala com fator 0, que achata o "
            "objeto), a matriz não tem inversa e o programa avisa.")]
    # 2.8
    e += [P("2.8 Autovalores e autovetores", H2),
          P("Um vetor v ≠ 0 é <b>autovetor</b> de A com <b>autovalor</b> λ se A·v = λ·v: a transformação "
            "apenas estica ou encolhe v, sem mudar sua direção. Os autovalores são as raízes da "
            "equação característica det(A − λI) = 0. Para 2×2 ela é λ² − tr(A)·λ + det(A) = 0 "
            "(Bhaskara). Para 3×3 é uma cúbica λ³ − tr(A)·λ² + c<sub>1</sub>·λ − det(A) = 0, em que "
            "c<sub>1</sub> é a soma dos menores principais 2×2; o programa acha uma raiz real por "
            "bisseção, reduz o grau (deflação) e resolve a quadrática restante. Para cada λ real, os "
            "autovetores são as soluções de (A − λI)·v = 0, obtidas por escalonamento (espaço nulo)."),
          P("<b>Interpretação:</b> autovalores reais indicam direções invariantes (desenhadas em verde "
            "nos gráficos); autovalores complexos indicam rotação, pois nenhuma direção real é "
            "mantida (no 3D, a rotação tem como eixo o autovetor de λ = 1). Exemplo (Caso 2): "
            "A = [[2, 2], [0, 1]] tem λ = 2 e λ = 1, com autovetores (1, 0) e (2, −1)/√5.")]
    # 2.9
    e += [P("2.9 Produtos de vetores usados no projeto", H2)]
    tab = [["Operação", "Fórmula", "Uso no código"],
           ["Produto escalar", "u·v = u<sub>1</sub>v<sub>1</sub> + u<sub>2</sub>v<sub>2</sub> + … = |u||v|cos θ",
            "iluminação (cos do ângulo entre a normal e a luz), projeção, ângulo entre vetores, junta dos traços da fonte"],
           ["Norma e vetor unitário", "|u| = √(u·u),  û = u/|u|", "vetor diretor de cada traço, normalização da normal"],
           ["Vetor perpendicular (2D)", "(x, y) → (−y, x)", "espessura do traço: retângulo p ± h·n"],
           ["Produto vetorial", "u × v = (u<sub>2</sub>v<sub>3</sub> − u<sub>3</sub>v<sub>2</sub>, …)",
            "normal de cada face 3D; faces visíveis; eixo de rotação"],
           ["Produto misto", "[u, v, w] = u·(v × w)", "volume de sólidos (soma de tetraedros)"]]
    e += [tabela(tab, [3.4 * cm, 6.0 * cm, 7.2 * cm])]
    return e


def secao_aplicacao():
    e = [P("3. Aplicação em Sistemas de Informação", H1),
         P("Transformações afins são a base da <b>computação gráfica e da interface com o usuário</b>. "
           "Alguns usos reais:"),
         ]
    e += bullets([
        "<b>Web e aplicativos:</b> animações de logotipos, banners e componentes de interface usam "
        "matrizes 2D 3×3 (a função matrix() do CSS) e 3D 4×4 (matrix3d()); girar, ampliar e "
        "mover elementos é compor matrizes.",
        "<b>Jogos e realidade aumentada:</b> cada objeto da cena tem uma <i>matriz de modelo</i> (escala, "
        "rotação e translação); depois vêm a matriz da <i>câmera</i> e a de <i>projeção</i>, exatamente o "
        "pipeline implementado em graficos.py.",
        "<b>Visão computacional e aprendizado de máquina:</b> o aumento de dados (<i>data augmentation</i>) "
        "gira, escala, desloca e cisalha imagens de treino com transformações afins.",
        "<b>CAD, GIS e animação:</b> posicionamento de peças, mapas e personagens por composição de transformações.",
    ])
    e += [P("<b>Problema abordado.</b> Gerar e animar uma <b>identidade visual de texto</b> (logotipo, "
            "título, banner) para <b>qualquer palavra</b>: a entrada é a palavra e a sequência de "
            "transformações; as saídas são a matriz composta, a imagem antes/depois, o GIF "
            "animado e o relatório. O mesmo código atende o texto plano (2D) e o texto com volume (3D), "
            "mostrando que a mesma teoria cobre as duas dimensões.")]
    return e


def secao_implementacao():
    e = [P("4. Implementação", H1),
         P("O código está dividido em módulos pequenos, cada um com funções separadas e comentadas. "
           "A tabela mostra a responsabilidade de cada um:")]
    mods = [["Arquivo", "Conteúdo"],
            ["vetores.py", "soma, produto por escalar, produto escalar, norma, normalização, produto vetorial, produto misto, perpendicular 2D, projeção, ângulo"],
            ["matrizes.py", "identidade, produto, transposta, determinante (cofatores), inversa (Gauss-Jordan), autovalores 2×2 e 3×3, autovetores (espaço nulo)"],
            ["transformacoes.py", "matrizes 2D (3×3) e 3D (4×4), Rodrigues, pivô, composição, matriz inversa da sequência, aplicação a V, interpolação para animação"],
            ["fonte.py", "fonte vetorial: caracteres → traços → polígonos (qualquer texto)"],
            ["objetos.py", "classe Objeto (matriz de vértices + faces), quadrado, triângulo, casinha, cubo, pirâmide, texto 2D e 3D, área e volume"],
            ["graficos.py", "gráficos 2D, renderizador 3D, comparação de ordem, GIF animado"],
            ["relatorio.py", "relatório de execução (txt)"],
            ["main.py", "menu interativo, leitura de comandos, opções de linha de comando"],
            ["testes.py", "8 casos de teste com saída esperada calculada à mão"]]
    e += [tabela(mods, [3.4 * cm, 13.2 * cm])]
    e += [P("4.1 Da palavra digitada aos vértices: a fonte vetorial", H2),
          P("Cada caractere é definido por <b>traços</b>: poligonais cujos pontos foram escolhidos numa "
            "caixa de 3 × 5; as curvas (O, S, 2, 3, 8, …) são aproximadas por segmentos calculados com "
            "(cx + rx·cos a, cy + ry·sen a). Cada segmento p → q vira um retângulo com os vetores:"),
          P("d = (q − p)/|q − p|,  n = (−d<sub>y</sub>, d<sub>x</sub>) (normal, n ⊥ d),  "
            "vértices = p ± h·n  e  q ± h·n,  h = espessura/2", EQ),
          P("As pontas são estendidas para os retângulos se encontrarem sem frestas; nas curvas "
            "suaves usa-se junta em esquadria, de extensão h·tan(φ/2) com tan(φ/2) = sen φ/(1 + cos φ), "
            "calculada pelo produto escalar e pelo produto vetorial dos vetores diretores vizinhos; "
            "em ângulos muito agudos (topo do A, fundo do V) usa-se uma junta arredondada. O "
            "texto vira uma lista de polígonos, centralizada na origem, e as letras minúsculas são "
            "desenhadas como maiúsculas; acentos (Á, Ã, Ç, Ü…) são traços extras. Para o 3D, cada "
            "polígono é <b>extrudado</b> em z, formando um prisma (topo, base e laterais)."),
          figura("fonte.png", "Figura 1: todos os caracteres da fonte vetorial, desenhados a partir de vértices.",
                 altura_max=9 * cm)]
    e += [P("4.2 Renderização 3D sem biblioteca 3D", H2),
          P("Em graficos.py, cada quadro 3D passa por estas etapas, todas com álgebra linear:")]
    e += bullets([
        "<b>Câmera:</b> os vértices são girados por R = R<sub>x</sub>(elevação)·R<sub>y</sub>(azimute) (produto de matrizes 3×3).",
        "<b>Perspectiva:</b> (x, y, z) → (x, y)·D/(D − z), com D a distância do observador.",
        "<b>Faces visíveis:</b> normal n = (p<sub>1</sub> − p<sub>0</sub>) × (p<sub>2</sub> − p<sub>1</sub>) (produto vetorial); a face aparece se n·(olho − p<sub>0</sub>) &gt; 0.",
        "<b>Iluminação (Lambert):</b> brilho = ambiente + difusa·máx(0, n·l), com n e l unitários: produto escalar entre a normal e a luz.",
        "<b>Ordem de desenho:</b> algoritmo do pintor (faces mais distantes primeiro).",
    ])
    e += [P("4.3 Funções básicas, sem pacotes de álgebra linear", H2),
          P("Nenhuma função de NumPy, SciPy ou SymPy é usada. Do Python vêm apenas a biblioteca padrão "
            "(math, re, unicodedata, argparse, io, os, sys) e, <b>exclusivamente para desenhar</b>, o "
            "Matplotlib (polígonos e linhas já calculados) e o Pillow (montagem do GIF). Produto de "
            "matrizes, determinante, inversa, autovalores, autovetores e produtos de vetores foram "
            "escritos à mão, com comentários linha a linha.")]
    return e


def secao_execucao():
    e = [P("5. Execução do programa", H1),
         P("Modo interativo (digite a palavra e as transformações no terminal):"),
         codigo("python main.py"),
         P("Demonstração completa com qualquer palavra, e execução direta por linha de comando:"),
         codigo('python main.py --demo "Sua Palavra"\n'
                'python main.py --texto "Olá" --3d --seq "RY 40; E 1 1,5 1; T 2 0 0" --gif\n'
                'python main.py --objeto cubo --seq "RZ 45; E 2 1 1"\n'
                'python testes.py'),
         P("Comandos de transformação (um por linha, na ordem de aplicação; aceita vírgula decimal; "
           "vários por linha separados por «;»):")]
    cmd = [["Comando", "2D", "3D"],
           ["Rotação", "R θ [px py]", "RX θ, RY θ, RZ θ [px py pz]; RA θ ax ay az [px py pz]"],
           ["Escala", "E sx sy [px py]", "E sx sy sz [px py pz]"],
           ["Cisalhamento", "C kx ky", "C kxy kxz kyx kyz kzx kzy"],
           ["Translação", "T tx ty", "T tx ty tz"],
           ["Reflexão", "F x | F y", "F xy | F xz | F yz"]]
    e += [tabela(cmd, [3.0 * cm, 4.2 * cm, 9.4 * cm]), Spacer(1, 6),
          P("Para cada execução o programa grava em <i>saida/</i>: o relatório (_relatorio.txt), o gráfico "
            "antes/depois (_grafico.png) e, se pedido, o GIF animado (_animado.gif). Os GIFs vão da "
            "identidade até a transformação completa e voltam, mostrando a matriz M(t), o "
            "determinante e os autovalores a cada quadro.")]
    return e


def secao_testes(casos, tudo_ok):
    e = [P("6. Testes: entrada, saída esperada e saída obtida", H1),
         P("Cada caso de teste tem a <b>saída esperada calculada à mão</b>, antes de executar o programa, "
           "e a comparação é feita por testes.py com tolerância de 10<super>-6</super>. As tabelas abaixo "
           "reproduzem a saída real de <i>python testes.py</i>. Os casos 1 e 2 são os exigidos pelo "
           "enunciado; os casos 3 a 8 são adicionais. Resultado geral: <b>" +
           ("todos os testes passaram" if tudo_ok else "HÁ FALHAS") + "</b>.")]
    enunciados = {
        1: ("<b>Entrada:</b> quadrado unitário (0,0), (1,0), (1,1), (0,1); sequência R(90°), E(2,3), T(1,1). "
            "<b>À mão:</b> E·R = [[0, −2], [3, 0]] e M = T·E·R = [[0, −2, 1], [3, 0, 1], [0, 0, 1]]; "
            "(1,0) → R → (0,1) → E → (0,3) → T → (1,4); det A = 6; λ² + 6 = 0 → λ = ±i√6."),
        2: ("<b>Entrada:</b> triângulo (0,0), (2,0), (0,2); sequência C(1,0), E(2,1), T(−1,2). "
            "<b>À mão:</b> E·C = [[2, 2], [0, 1]], M = [[2, 2, −1], [0, 1, 2], [0, 0, 1]]; "
            "(2,0) → C → (2,0) → E → (4,0) → T → (3,2); det A = 2; λ = 2 e λ = 1; autovetores (1,0) e (2,−1)/√5."),
        3: ("<b>Entrada:</b> cubo de aresta 2 centrado na origem; sequência Rz(90°), E(2,1,3), T(1,2,3). "
            "<b>À mão:</b> (x, y, z) → (−y, x, z) → (−2y, x, 3z) → (−2y + 1, x + 2, 3z + 3); det A = 2·3 = 6, "
            "volume 8 → 48; o bloco [[0, −2], [1, 0]] dá λ² + 2 = 0."),
        4: ("<b>Entrada:</b> o texto «T» (a fonte aceita qualquer texto); escala (2,3). <b>À mão:</b> barra "
            "(3 + 0,9)·0,9 = 3,51 e haste (5 + 0,9)·0,9 = 5,31, total 8,82; com E(2,3), det = 6 e área 52,92."),
        5: ("<b>Entrada:</b> M do caso 1. <b>À mão:</b> A<super>-1</super> = (1/6)[[0, 2], [−3, 0]] e "
            "−A<super>-1</super>·t = (−1/3, 1/2), logo M<super>-1</super> = [[0, 1/3, −1/3], [−1/2, 0, 1/2], [0, 0, 1]]."),
        6: ("<b>Entrada:</b> diag(2,3,5), Rz(90°) e rotação de 120° em torno de (1,1,1). <b>À mão:</b> autovalores "
            "5, 3, 2; Rz tem λ = 1 e ±i, com eixo (0,0,1); a rotação de 120° em torno de (1,1,1) permuta e<sub>1</sub> → e<sub>2</sub> → "
            "e<sub>3</sub> → e<sub>1</sub>."),
        7: ("<b>Entrada:</b> vetores (1,2,3) e (4,5,6) e a pirâmide de base 2×2 e altura 2. <b>À mão:</b> "
            "(1,2,3) × (4,5,6) = (−3, 6, −3); u·v = 32; volume = (1/3)·4·2 = 8/3."),
        8: ("<b>Entrada:</b> ponto (2,1) girado 90° em torno de (1,1). <b>À mão:</b> T(−1,−1): (1,0); R(90°): (0,1); "
            "T(1,1): (1,2). Além disso, R·E ≠ E·R."),
    }
    figs = {1: ("caso1.png", "Figura 2: Caso 1, quadrado antes e depois (malha deformada à direita)."),
            2: ("caso2.png", "Figura 3: Caso 2, triângulo antes e depois; as setas verdes são os autovetores."),
            3: ("caso3.png", "Figura 4: Caso 3, cubo 3D antes e depois; a reta verde é o autovetor de λ = 3 (eixo z)."),
            4: ("caso4.png", "Figura 5: Caso 4, a letra T digitada antes e depois da escala (2,3).")}
    for i, (titulo, itens) in enumerate(casos, 1):
        obrig = " (obrigatório)" if i <= 2 else ""
        e += [P(f"Caso {i}{obrig}: {escape(titulo.split(': ', 1)[-1] if ': ' in titulo else titulo)}", H2),
              P(enunciados[i]), tabela_de_testes(itens), Spacer(1, 6)]
        if i in figs:
            e += [figura(*figs[i], altura_max=9.2 * cm)]
    return e


def secao_demonstracao():
    e = [P("7. Demonstração com palavras digitadas", H1),
         P("A figura 6 mostra o programa com a frase «Álgebra Linear», digitada no terminal (o acento "
           "também é desenhado), no plano; a figura 7, com «IFSP» em 3D. Em ambos os casos o texto foi "
           "convertido em matriz de vértices pela fonte vetorial e transformado pela matriz composta."),
         figura("demo2d.png", "Figura 6: «Álgebra Linear» em 2D: R(30°), E(1,3; 0,8), C(0,5; 0), T(2,1).",
                altura_max=11.5 * cm),
         figura("demo3d.png", "Figura 7: «IFSP» em 3D: Ry(50°), Rx(−25°), E(1,2; 1,2; 1,2), T(3,2,0).",
                altura_max=9.5 * cm)]
    # trecho do relatório de execução real (seções 4 a 6 do demo 3D)
    try:
        with open(os.path.join("saida", "demo_3d_relatorio.txt"), encoding="utf-8") as f:
            texto = f.read()
        ini, fim = texto.index("4) MATRIZ COMPOSTA"), texto.index("7) VÉRTICES")
        e += [P("Trecho do relatório de execução gerado pelo programa para a figura 7 "
                "(matriz composta, determinante, autovalores e matriz inversa):"),
              codigo(texto[ini:fim].rstrip(), tam=7.2)]
    except (OSError, ValueError):
        pass
    e += [figura("ordem2d.png", "Figura 8: a ordem importa em 2D: R(45°) e E(1,6; 0,6) aplicadas em ordens diferentes.",
                 altura_max=10 * cm),
          figura("ordem3d.png", "Figura 9: a ordem importa em 3D: Ry(45°) e E(1,6; 0,6; 1) aplicadas em ordens diferentes.",
                 altura_max=10.5 * cm),
          P("As figuras 8 e 9 mostram a não comutatividade: girar e depois escalar produz um resultado "
            "diferente de escalar e depois girar, pois R·E ≠ E·R.")]
    return e


def secao_conclusao():
    e = [P("8. Explicação dos resultados e conclusão", H1)]
    e += bullets([
        "A matriz composta é o produto das individuais na ordem inversa de aplicação (M = T<sub>n</sub>·…·T<sub>1</sub>). "
        "Os testes confirmam que esse produto reproduz o efeito de aplicar as transformações uma a uma.",
        "A translação só entrou no produto graças às coordenadas homogêneas (matrizes 3×3 e 4×4).",
        "O determinante é o fator de variação de área (2D) ou volume (3D): 6 nos casos 1 e 3, e 2 no caso 2. "
        "Isso foi conferido pela área (cadarço) e pelo volume (produto misto) das figuras finais, e o relatório "
        "de cada execução repete essa verificação.",
        "Os autovalores revelam o comportamento geométrico: complexos quando há rotação e reais quando só há "
        "escala e cisalhamento, com as direções invariantes desenhadas em verde.",
        "A matriz inversa desfaz a transformação: M·M<super>-1</super> = I e M<super>-1</super> aplicada ao objeto final "
        "devolve o original, com erro da ordem de 10<super>-15</super>.",
        "A ordem importa: R·E ≠ E·R, como mostram o caso 8 e as figuras 8 e 9.",
        "A fonte vetorial mostra que um texto qualquer é só uma matriz de vértices, e que as mesmas "
        "transformações valem para letras, polígonos e sólidos.",
    ])
    e += [P("<b>Limitações.</b> A fonte tem letras maiúsculas (as minúsculas são desenhadas como maiúsculas), "
            "algarismos, pontuação comum e acentos do português; outros símbolos aparecem como «?», e o texto "
            "tem no máximo 60 caracteres. O algoritmo do pintor é aproximado quando sólidos se interpenetram (as "
            "letras são prismas sobrepostos), mas, com cores iguais e iluminação por face, o resultado é visualmente correto. "
            "Como extensões possíveis: projeção ortográfica selecionável, câmera interativa, outras fontes "
            "e importação de malhas."),
          P("O trabalho integrou vetores, geometria analítica, matrizes, transformações lineares, determinantes, "
            "inversas e autovalores numa aplicação de Sistemas de Informação, com os conceitos matemáticos "
            "escritos explicitamente no código, e foi além do enunciado ao tratar 3D e texto qualquer.")]
    e += [P("Referências", H1),
          P("FRANCO, Neide Maria Bertoldi. <b>Álgebra Linear</b>. Capítulo 5: Transformações lineares. "
            "São Paulo: Pearson Education do Brasil, 2016. Disponível na Biblioteca Virtual: "
            "https://plataforma.bvirtual.com.br/Leitor/Loader/39451/pdf"),
          P("IME-UNICAMP. <b>Álgebra Linear</b> (material online da Profa. Márcia). Disponível em: "
            "https://www.ime.unicamp.br/~marcia/AlgebraLinear/index.html e "
            "https://www.ime.unicamp.br/~marcia/AlgebraLinear/trans_lineares.html"),
          P("Notas da Aula 10: Transformação linear (material da disciplina).")]
    return e


def main():
    casos, tudo_ok = executar_testes()
    doc = SimpleDocTemplate(SAIDA_PDF, pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                            topMargin=2.2 * cm, bottomMargin=2.2 * cm, title=TITULO,
                            author=", ".join(AUTORES))
    historia = []
    historia += capa() + folha_de_rosto()
    historia += secao_introducao() + secao_teoria() + secao_aplicacao()
    historia += secao_implementacao() + secao_execucao()
    historia += secao_testes(casos, tudo_ok) + secao_demonstracao() + secao_conclusao()
    doc.build(historia, onFirstPage=rodape, onLaterPages=rodape)
    print("PDF gerado:", SAIDA_PDF, f"({len(casos)} casos de teste lidos)")


if __name__ == "__main__":
    main()
