"""
testes.py
---------
Dois casos de teste com ENTRADA e SAÍDA ESPERADA calculadas à mão.
Execute:  python testes.py
"""

from matrizes import autovalores_2x2, autovetor_2x2, determinante, multiplicar
from transformacoes import compor, aplicar, parte_linear, rotacao, escala
from objetos import quadrado_unitario, triangulo

TOL = 1e-6   # tolerância para comparar números de ponto flutuante


def iguais(A, B):
    """Compara duas matrizes (ou listas de pontos) elemento a elemento."""
    for linha_a, linha_b in zip(A, B):
        for a, b in zip(linha_a, linha_b):
            if abs(a - b) > TOL:
                return False
    return True


def mostrar(titulo, esperado, obtido, ok):
    """Imprime uma linha de resultado do teste."""
    print(f"  {titulo}")
    print(f"    esperado: {esperado}")
    print(f"    obtido  : {obtido}")
    print(f"    -> {'OK' if ok else 'FALHOU'}")
    return ok


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
    finais = aplicar(M, quadrado_unitario())[0]
    ok = True
    M_esp = [[0, -2, 1], [3, 0, 1], [0, 0, 1]]
    ok &= mostrar("matriz composta M", M_esp,
                  [[round(x, 6) + 0.0 for x in l] for l in M], iguais(M, M_esp))
    v_esp = [(1, 1), (1, 4), (-1, 4), (-1, 1)]
    ok &= mostrar("vértices finais", v_esp,
                  [(round(x, 6) + 0.0, round(y, 6) + 0.0) for x, y in finais],
                  iguais(finais, v_esp))
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
    finais = aplicar(M, triangulo())[0]
    ok = True
    M_esp = [[2, 2, -1], [0, 1, 2], [0, 0, 1]]
    ok &= mostrar("matriz composta M", M_esp,
                  [[round(x, 6) + 0.0 for x in l] for l in M], iguais(M, M_esp))
    v_esp = [(-1, 2), (3, 2), (3, 4)]
    ok &= mostrar("vértices finais", v_esp,
                  [(round(x, 6) + 0.0, round(y, 6) + 0.0) for x, y in finais],
                  iguais(finais, v_esp))
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


def teste_nao_comutatividade():
    """Extra: confirma que R·E é diferente de E·R (ordem importa)."""
    print("EXTRA: R(90°)·E(2,1) é diferente de E(2,1)·R(90°)")
    R, E = rotacao(90), escala(2, 1)
    return mostrar("R·E diferente de E·R", "diferentes", "diferentes",
                   not iguais(multiplicar(R, E), multiplicar(E, R)))


if __name__ == "__main__":
    resultados = [teste_1(), teste_2(), teste_nao_comutatividade()]
    print()
    print("RESULTADO FINAL:", "TODOS OS TESTES PASSARAM" if all(resultados) else "HÁ FALHAS")
