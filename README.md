# Transformações Lineares 2D e 3D

Programa em Python para aplicar e visualizar transformações geométricas em objetos bidimensionais e tridimensionais, usando matrizes em coordenadas homogêneas.

---

## Requisitos

- Python 3.10 ou superior
- Bibliotecas listadas em `requirements.txt`

---

## Instalação

Abra o terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
```

---

## Como executar

### Demonstração automática

Para executar a demonstração padrão:

```bash
python main.py --demo
```

Para usar outro texto:

```bash
python main.py --demo "Minha Palavra"
```

### Modo interativo

```bash
python main.py
```

Ao executar, aparecerá um menu semelhante a este:

```text
Objeto:
1) Texto 2D
2) Texto 3D
3) Quadrado
4) Triângulo
5) Casinha
6) Cubo
7) Pirâmide

Escolha [1]:
```

Digite o número correspondente ao objeto desejado e aperte **Enter**.

### Como informar as transformações

Depois de escolher o objeto, digite os comandos de transformação, um por linha.

**Importante:** quando terminar de inserir as transformações, aperte **Enter em uma linha vazia** para finalizar a sequência e executar o processamento.

---

## Exemplos de execução de cada objeto

### 1. Texto 2D

Na primeira tela, digite `1`. Depois, informe a palavra desejada.

Exemplo:

```text
Escolha [1]: 1
Digite o texto [IFSP]: Texto
```

Em seguida, digite as transformações:

```text
R 45
E 2 2
C 0.5 0
T 2 3
```

Aperte **Enter em uma linha vazia** para finalizar.

### 2. Texto 3D

Digite `2` e depois informe a palavra desejada.

Exemplo:

```text
Escolha [1]: 2
Digite o texto [IFSP]: Texto
```

Digite as transformações:

```text
RX 45
RY 30
RZ 60
E 2 2 2
C 0.5 0 0 0 0 0
T 2 3 4
```

Aperte **Enter em uma linha vazia** para finalizar.

### 3. Quadrado

Digite `3` e aplique:

```text
R 45
E 2 2
C 0.5 0
T 2 3
F x
```

Aperte **Enter em uma linha vazia** para finalizar.

### 4. Triângulo

Digite `4` e aplique:

```text
R 45
E 2 2
C 0.5 0
T 2 3
F x
```

Aperte **Enter em uma linha vazia** para finalizar.

### 5. Casinha

Digite `5` e aplique:

```text
R 30
E 1.5 1.5
C 0.3 0
T 2 2
F y
```

Aperte **Enter em uma linha vazia** para finalizar.

### 6. Cubo

Digite `6` e aplique:

```text
RX 45
RY 30
RZ 60
E 2 2 2
C 0.5 0 0 0 0 0
T 2 3 4
```

Aperte **Enter em uma linha vazia** para finalizar.

### 7. Pirâmide

Digite `7` e aplique:

```text
RX 45
RY 30
RZ 60
E 1.5 1.5 1.5
C 0.5 0 0 0 0 0
T 2 3 4
```

Aperte **Enter em uma linha vazia** para finalizar.

---

## Comandos de transformação

Os comandos aceitos dependem da dimensão do objeto:

| Comando | Operação |
|---|---|
| `R ângulo` | Rotação 2D |
| `RX ângulo` | Rotação em torno do eixo X |
| `RY ângulo` | Rotação em torno do eixo Y |
| `RZ ângulo` | Rotação em torno do eixo Z |
| `E sx sy` ou `E sx sy sz` | Escala |
| `C kx ky` | Cisalhamento 2D |
| `T tx ty` ou `T tx ty tz` | Translação |
| `F x`, `F y` | Reflexão 2D |
| `F xy`, `F xz`, `F yz` | Reflexão 3D |

É possível separar várias transformações por ponto e vírgula quando se usa `--seq`. No modo interativo, informe uma transformação por linha.

---

## Resultados

Os gráficos e, quando solicitadas, as animações são salvos na pasta `saida/`. O programa também informa no terminal os arquivos produzidos.

---

## Testes

Para executar os casos de teste:

```bash
python testes.py
```

Os testes verificam operações matriciais, transformações 2D e 3D, matrizes inversas, autovalores e propriedades geométricas.

---

## Resumo dos comandos de execução

| Objetivo | Comando |
|---|---|
| Abrir o programa no modo interativo | `python main.py` |
| Executar a demonstração padrão | `python main.py --demo` |
| Executar a demonstração com outro texto | `python main.py --demo "Minha Palavra"` |
| Executar os testes | `python testes.py` |
| Instalar as dependências | `pip install -r requirements.txt` |
