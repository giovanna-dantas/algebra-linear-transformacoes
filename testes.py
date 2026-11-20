"""
testes.py
---------
Casos de teste com ENTRADA e SAÍDA ESPERADA calculadas à mão (a lápis).

  CASOS OBRIGATÓRIOS DO ENUNCIADO
    Caso 1 - quadrado 2D: rotação + escala + translação
    Caso 2 - triângulo 2D: cisalhamento + escala + translação
  CASOS ADICIONAIS (vão além do pedido)
    Caso 3 - cubo 3D (matrizes 4x4, volume, autovalores)
    Caso 4 - texto digitado ("T"): retângulos da fonte, área e caixa envolvente
    Caso 5 - matriz inversa: M⁻¹ calculada à mão e objeto restaurado
    Caso 6 - autovalores 3x3 e rotação em torno de eixo arbitrário (Rodrigues)
    Caso 7 - vetores: produto vetorial, projeção, volume da pirâmide (produto misto)
    Caso 8 - rotação em torno de um pivô e não comutatividade

Execute:  python testes.py
"""

from matrizes import (autovalores_2x2, autovetor_2x2, autovalores, autovetores,
                      determinante, multiplicar, inversa, identidade)
from transformacoes import (compor, aplicar_matriz, parte_linear, rotacao, escala,
                            rotacao_z, rotacao_eixo, com_pivo)
from objetos import (quadrado_unitario, triangulo, cubo, piramide, texto_2d,
                     medida_assinada, volume_assinado, area_assinada, caixa_envolvente)
from vetores import produto_vetorial, produto_escalar, projecao, angulo_entre

TOL = 1e-6   # tolerância para comparar números de ponto flutuante


def iguais(A, B):
    """Compara duas matrizes (ou listas de pontos) elemento a elemento."""
    if len(A) != len(B):
        return False
    for linha_a, linha_b in zip(A, B):
        for a, b in zip(linha_a, linha_b):
            if abs(a - b) > TOL:
                return False
    return True


def arred(x):
    """Arredonda matrizes, tuplas e números para exibição (e troca -0.0 por 0.0)."""
    if isinstance(x, (list, tuple)):
        return type(x)(arred(i) for i in x)
    return round(x, 6) + 0.0


def mostrar(titulo, esperado, obtido, ok):
    """Imprime uma linha de resultado do teste."""
    print(f"  {titulo}")
    print(f"    esperado: {esperado}")
    print(f"    obtido  : {obtido}")
    print(f"    -> {'OK' if ok else 'FALHOU'}")
    return ok


def vertices_finais(M, obj):
    """Aplica M ao objeto e devolve a lista dos vértices finais."""
    return obj.com_vertices(aplicar_matriz(M, obj.V)).vertices()


def teste_1():
    """
    CASO 1 - Quadrado unitário.
    Sequência: rotação de 90°, escala (2, 3), translação (1, 1).
    M = T·E·R  =  [[0,-2,1],[3,0,1],[0,0,1]]
    Vértices esperados: (0,0)->(1,1); (1,0)->(1,4); (1,1)->(-1,4); (0,1)->(-1,1)
    det(A) = 6 ; autovalores = ±i·sqrt(6) (complexos: há rotação).
    """
    print("CASO DE TESTE 1: quadrado, rotação 90°, escala (2,3), translação (1,1)")
    sequencia = [("rotacao", [90]), ("escala", [2, 3]), ("translacao", [1, 1])]
    M, _ = compor(sequencia)
    finais = vertices_finais(M, quadrado_unitario())
    ok = True
    M_esp = [[0, -2, 1], [3, 0, 1], [0, 0, 1]]
    ok &= mostrar("matriz composta M", M_esp, arred(M), iguais(M, M_esp))
    v_esp = [(1, 1), (1, 4), (-1, 4), (-1, 1)]
    ok &= mostrar("vértices finais", v_esp, arred(finais), iguais(finais, v_esp))
    A = parte_linear(M)
    det = determinante(A)
    ok &= mostrar("det(A)", 6.0, round(det, 6), abs(det - 6) < TOL)
    lams = autovalores_2x2(A)
    ok &= mostrar("autovalores (parte imaginária)", "±2.449490 (= sqrt 6)",
                  f"{abs(lams[0].imag):.6f}",
                  isinstance(lams[0], complex) and abs(abs(lams[0].imag) - 6 ** 0.5) < TOL)
    return ok


def teste_2():
    """
    CASO 2 - Triângulo (0,0),(2,0),(0,2).
    Sequência: cisalhamento (kx=1, ky=0), escala (2, 1), translação (-1, 2).
    E·H = [[2,2],[0,1]]  ->  M = [[2,2,-1],[0,1,2],[0,0,1]]
    Vértices esperados: (0,0)->(-1,2); (2,0)->(3,2); (0,2)->(3,4)
    det(A) = 2 ; autovalores 2 e 1 ; autovetores (1,0) e (2,-1)/sqrt(5).
    """
    print("CASO DE TESTE 2: triângulo, cisalhamento (1,0), escala (2,1), translação (-1,2)")
    sequencia = [("cisalhamento", [1, 0]), ("escala", [2, 1]), ("translacao", [-1, 2])]
    M, _ = compor(sequencia)
    finais = vertices_finais(M, triangulo())
    ok = True
    M_esp = [[2, 2, -1], [0, 1, 2], [0, 0, 1]]
    ok &= mostrar("matriz composta M", M_esp, arred(M), iguais(M, M_esp))
    v_esp = [(-1, 2), (3, 2), (3, 4)]
    ok &= mostrar("vértices finais", v_esp, arred(finais), iguais(finais, v_esp))
    A = parte_linear(M)
    det = determinante(A)
    ok &= mostrar("det(A)", 2.0, round(det, 6), abs(det - 2) < TOL)
    lams = sorted(autovalores_2x2(A), reverse=True)
    ok &= mostrar("autovalores", [2.0, 1.0], [round(l, 6) for l in lams],
                  abs(lams[0] - 2) < TOL and abs(lams[1] - 1) < TOL)
    # Verifica A·v = λ·v para cada autovetor encontrado (definição de autovetor).
    todos_ok = True
    for lam in lams:
        v = autovetor_2x2(A, lam)
        Av = multiplicar(A, [[v[0]], [v[1]]])
        if abs(Av[0][0] - lam * v[0]) > TOL or abs(Av[1][0] - lam * v[1]) > TOL:
            todos_ok = False
    ok &= mostrar("verificação A·v = λ·v", "verdadeiro", todos_ok, todos_ok)
    return ok


def teste_3():
    """
    CASO 3 - Cubo 3D (aresta 2, centrado na origem).
    Sequência: rotação de 90° em z, escala (2, 1, 3), translação (1, 2, 3).
    Rz(90°): (x, y, z) -> (-y, x, z);  depois (2x, y, 3z);  depois +(1, 2, 3):
        x' = -2y + 1 ,  y' = x + 2 ,  z' = 3z + 3
    M = [[0,-2,0,1],[1,0,0,2],[0,0,3,3],[0,0,0,1]]
    Vértices esperados, na ordem do cubo:
      (-1,-1,-1)->(3,1,0)   (1,-1,-1)->(3,3,0)   (1,1,-1)->(-1,3,0)   (-1,1,-1)->(-1,1,0)
      (-1,-1, 1)->(3,1,6)   (1,-1, 1)->(3,3,6)   (1, 1, 1)->(-1,3,6)  (-1,1, 1)->(-1,1,6)
    det(A) = 0·... = 2·3 = 6  ->  volume 8 vira 48.
    Autovalores de A: 3 e ±i·sqrt(2)  (bloco 2x2 [[0,-2],[1,0]]: λ² + 2 = 0).
    """
    print("CASO DE TESTE 3: cubo 3D, Rz(90°), escala (2,1,3), translação (1,2,3)")
    sequencia = [("rotacao_z", [90]), ("escala", [2, 1, 3]), ("translacao", [1, 2, 3])]
    M, _ = compor(sequencia)
    ok = True
    M_esp = [[0, -2, 0, 1], [1, 0, 0, 2], [0, 0, 3, 3], [0, 0, 0, 1]]
    ok &= mostrar("matriz composta M (4x4)", M_esp, arred(M), iguais(M, M_esp))
    v_esp = [(3, 1, 0), (3, 3, 0), (-1, 3, 0), (-1, 1, 0),
             (3, 1, 6), (3, 3, 6), (-1, 3, 6), (-1, 1, 6)]
    finais = vertices_finais(M, cubo())
    ok &= mostrar("vértices finais", v_esp, arred(finais), iguais(finais, v_esp))
    A = parte_linear(M)
    det = determinante(A)
    ok &= mostrar("det(A)", 6.0, round(det, 6), abs(det - 6) < TOL)
    vol0 = volume_assinado(cubo())
    vol1 = volume_assinado(cubo().com_vertices(aplicar_matriz(M, cubo().V)))
    ok &= mostrar("volume antes -> depois", "8 -> 48", f"{vol0:.6f} -> {vol1:.6f}",
                  abs(vol0 - 8) < TOL and abs(vol1 - 48) < TOL)
    lams = autovalores(A)
    reais = [l for l in lams if not isinstance(l, complex)]
    comp = [l for l in lams if isinstance(l, complex)]
    ok_l = (len(reais) == 1 and abs(reais[0] - 3) < 1e-6 and len(comp) == 2
            and abs(abs(comp[0].imag) - 2 ** 0.5) < 1e-6 and abs(comp[0].real) < 1e-6)
    ok &= mostrar("autovalores", "3 e ±1.414214i",
                  f"{[round(l.real, 6) if not isinstance(l, complex) else (round(l.real, 6) + 0.0, round(l.imag, 6)) for l in lams]}",
                  ok_l)
    return ok


def teste_4():
    """
    CASO 4 - Texto digitado: a letra "T" (a fonte aceita QUALQUER texto).
    O 'T' tem 2 traços: a barra (3 de comprimento) e a haste (5 de comprimento),
    espessura 0,9, com tampas quadradas de 0,45 nas pontas:
        barra: (3 + 0,9) x 0,9 = 3,51      haste: (5 + 0,9) x 0,9 = 5,31
        área total = 8,82 ; 2 retângulos -> 8 vértices
    Caixa envolvente do desenho: 3,9 de largura x 5,9 de altura, centralizada na origem:
        x em [-1,95; 1,95]   y em [-2,95; 2,95]
    Com escala (2, 3): det = 6 -> área 6 x 8,82 = 52,92, caixa 7,8 x 17,7 e a barra
    fica com vértices (-3,9; 6,15), (3,9; 6,15), (3,9; 8,85), (-3,9; 8,85).
    Também: minúsculas e maiúsculas geram o mesmo desenho.
    """
    print('CASO DE TESTE 4: texto digitado "T", escala (2,3)')
    obj, desconhecidos = texto_2d("T")
    ok = True
    ok &= mostrar("nº de vértices e retângulos", "8 vértices, 2 retângulos",
                  f"{obj.n_vertices()} vértices, {len(obj.faces)} retângulos",
                  obj.n_vertices() == 8 and len(obj.faces) == 2)
    a0 = area_assinada(obj)
    ok &= mostrar("área (soma dos retângulos)", 8.82, round(a0, 6), abs(a0 - 8.82) < TOL)
    cx, cy = caixa_envolvente(obj)
    ok &= mostrar("caixa envolvente", "x[-1.95,1.95] y[-2.95,2.95]",
                  f"x[{cx[0]:.2f},{cx[1]:.2f}] y[{cy[0]:.2f},{cy[1]:.2f}]",
                  abs(cx[0] + 1.95) < TOL and abs(cx[1] - 1.95) < TOL
                  and abs(cy[0] + 2.95) < TOL and abs(cy[1] - 2.95) < TOL)
    M, _ = compor([("escala", [2, 3])])
    final = obj.com_vertices(aplicar_matriz(M, obj.V))
    a1 = area_assinada(final)
    ok &= mostrar("área após escala (2,3)", 52.92, round(a1, 6), abs(a1 - 52.92) < TOL)
    barra = [final.vertice(i) for i in range(4)]
    barra_esp = [(-3.9, 6.15), (3.9, 6.15), (3.9, 8.85), (-3.9, 8.85)]
    ok &= mostrar("vértices da barra do T", barra_esp, arred(barra), iguais(barra, barra_esp))
    ok &= mostrar("sem distinção entre minúsculas e maiúsculas", "mesma matriz de vértices",
                  "iguais" if iguais(texto_2d("ola")[0].V, texto_2d("OLA")[0].V) else "diferentes",
                  iguais(texto_2d("ola")[0].V, texto_2d("OLA")[0].V))
    ok &= mostrar("acento acrescenta traço (Ã tem mais vértices que A)", "sim",
                  "sim" if texto_2d("Ã")[0].n_vertices() > texto_2d("A")[0].n_vertices() else "não",
                  texto_2d("Ã")[0].n_vertices() > texto_2d("A")[0].n_vertices())
    return ok


def teste_5():
    """
    CASO 5 - Matriz inversa (Caso 1).
    M = [[0,-2,1],[3,0,1],[0,0,1]]  ->  A = [[0,-2],[3,0]], det(A) = 6
    A⁻¹ = (1/6)·[[0,2],[-3,0]] = [[0,1/3],[-1/2,0]]
    t' = -A⁻¹·t = -[[0,1/3],[-1/2,0]]·(1,1) = (-1/3, 1/2)
    M⁻¹ = [[0,1/3,-1/3],[-1/2,0,1/2],[0,0,1]]
    Além disso, M·M⁻¹ = I e M⁻¹ aplicada ao quadrado final devolve o quadrado original.
    Uma matriz com det = 0 (escala 0) deve ser rejeitada.
    """
    print("CASO DE TESTE 5: matriz inversa do caso 1")
    M, _ = compor([("rotacao", [90]), ("escala", [2, 3]), ("translacao", [1, 1])])
    ok = True
    inv_esp = [[0, 1 / 3, -1 / 3], [-1 / 2, 0, 1 / 2], [0, 0, 1]]
    Minv = inversa(M)
    ok &= mostrar("M⁻¹ (Gauss-Jordan)", arred(inv_esp), arred(Minv), iguais(Minv, inv_esp))
    prod = multiplicar(M, Minv)
    ok &= mostrar("M·M⁻¹", "matriz identidade", arred(prod), iguais(prod, identidade(3)))
    q = quadrado_unitario()
    final = aplicar_matriz(M, q.V)
    volta = aplicar_matriz(Minv, final)
    ok &= mostrar("M⁻¹ aplicada ao objeto final", arred(q.V), arred(volta), iguais(volta, q.V))
    try:
        inversa([[1, 2], [2, 4]])
        rejeitou = False
    except ValueError:
        rejeitou = True
    ok &= mostrar("matriz singular [[1,2],[2,4]] é rejeitada", "ValueError", "ValueError" if rejeitou else "aceitou", rejeitou)
    return ok


def teste_6():
    """
    CASO 6 - Autovalores 3x3 e rotação em torno de eixo arbitrário.
    a) diag(2,3,5): autovalores 5, 3, 2.
    b) Rz(90°): autovalores 1 e ±i ; autovetor de λ = 1 é o eixo z = (0,0,1).
    c) Rotação de 120° em torno de (1,1,1) leva e1->e2->e3->e1, isto é,
       R = [[0,0,1],[1,0,0],[0,1,0]]  (fórmula de Rodrigues).
    """
    print("CASO DE TESTE 6: autovalores 3x3 e rotação em torno de (1,1,1)")
    ok = True
    lams = autovalores([[2, 0, 0], [0, 3, 0], [0, 0, 5]])
    ok &= mostrar("autovalores de diag(2,3,5)", [5, 3, 2], [round(l, 6) for l in lams],
                  all(abs(a - b) < TOL for a, b in zip(lams, [5, 3, 2])))
    A = parte_linear(rotacao_z(90))
    lz = autovalores(A)
    reais = [l for l in lz if not isinstance(l, complex)]
    comp = [l for l in lz if isinstance(l, complex)]
    ok &= mostrar("autovalores de Rz(90°)", "1 e ±1i",
                  f"real {round(reais[0], 6)}, imag ±{round(abs(comp[0].imag), 6)}",
                  len(reais) == 1 and abs(reais[0] - 1) < TOL and len(comp) == 2
                  and abs(abs(comp[0].imag) - 1) < TOL)
    v = autovetores(A, reais[0])
    ok &= mostrar("autovetor de λ = 1 (eixo de rotação)", "[(0,0,1)]", arred(v),
                  len(v) == 1 and iguais([v[0]], [(0, 0, 1)]))
    R = rotacao_eixo(120, 1, 1, 1)
    esp = [[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
    ok &= mostrar("Rodrigues 120° em torno de (1,1,1)", esp, arred(R), iguais(R, esp))
    return ok


def teste_7():
    """
    CASO 7 - Vetores.
    (1,2,3) × (4,5,6) = (2·6-3·5, 3·4-1·6, 1·5-2·4) = (-3, 6, -3)
    (1,2,3)·(4,5,6) = 4 + 10 + 18 = 32
    proj_(1,0)(3,4) = (3,0) ; ângulo entre (1,0) e (1,1) = 45°
    Volume da pirâmide (base 2x2, altura 2) = (1/3)·4·2 = 8/3 (produto misto).
    """
    print("CASO DE TESTE 7: produto vetorial/escalar, projeção, ângulo e volume da pirâmide")
    ok = True
    pv = produto_vetorial((1, 2, 3), (4, 5, 6))
    ok &= mostrar("(1,2,3) × (4,5,6)", (-3, 6, -3), arred(pv), iguais([pv], [(-3, 6, -3)]))
    pe = produto_escalar((1, 2, 3), (4, 5, 6))
    ok &= mostrar("(1,2,3) · (4,5,6)", 32, pe, abs(pe - 32) < TOL)
    pr = projecao((3, 4), (1, 0))
    ok &= mostrar("projeção de (3,4) sobre (1,0)", (3, 0), arred(pr), iguais([pr], [(3, 0)]))
    ang = angulo_entre((1, 0), (1, 1))
    ok &= mostrar("ângulo entre (1,0) e (1,1)", 45.0, round(ang, 6), abs(ang - 45) < TOL)
    vol = volume_assinado(piramide())
    ok &= mostrar("volume da pirâmide (produto misto)", round(8 / 3, 6), round(vol, 6), abs(vol - 8 / 3) < TOL)
    return ok


def teste_8():
    """
    CASO 8 - Rotação em torno de um pivô e não comutatividade.
    Girar 90° em torno de (1,1) o ponto (2,1):  T(1,1)·R(90°)·T(-1,-1)
        T(-1,-1): (2,1)->(1,0) ; R(90°): (1,0)->(0,1) ; T(1,1): (0,1)->(1,2)
    Além disso R(90°)·E(2,1) é diferente de E(2,1)·R(90°) (a ordem importa).
    """
    print("CASO DE TESTE 8: rotação em torno de pivô e não comutatividade")
    ok = True
    M, _ = compor(com_pivo("rotacao", [90], [1, 1]))
    V = [[2.0], [1.0]]
    r = aplicar_matriz(M, V)
    ok &= mostrar("(2,1) girado 90° em torno de (1,1)", "(1,2)", arred([(r[0][0], r[1][0])]),
                  iguais([(r[0][0], r[1][0])], [(1, 2)]))
    R, E = rotacao(90), escala(2, 1)
    ok &= mostrar("R·E diferente de E·R", "diferentes", "diferentes",
                  not iguais(multiplicar(R, E), multiplicar(E, R)))
    return ok


if __name__ == "__main__":
    nomes = ["Caso 1 (obrigatório)", "Caso 2 (obrigatório)", "Caso 3", "Caso 4",
             "Caso 5", "Caso 6", "Caso 7", "Caso 8"]
    funcoes = [teste_1, teste_2, teste_3, teste_4, teste_5, teste_6, teste_7, teste_8]
    resultados = []
    for f in funcoes:
        resultados.append(f())
        print()
    print("RESUMO:")
    for nome, r in zip(nomes, resultados):
        print(f"  {nome}: {'OK' if r else 'FALHOU'}")
    print()
    print("RESULTADO FINAL:", "TODOS OS TESTES PASSARAM" if all(resultados) else "HÁ FALHAS")
    raise SystemExit(0 if all(resultados) else 1)
