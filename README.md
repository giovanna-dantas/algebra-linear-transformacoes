# Transformações Lineares 2D e 3D

Programa em Python para aplicar e visualizar transformações geométricas em objetos bidimensionais e tridimensionais, usando matrizes em coordenadas homogêneas.

## Requisitos

- Python 3.10 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

Abra o terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
```

## Como executar

### Modo interativo

```bash
python main.py
```

Escolha um objeto no menu, informe as transformações desejadas e finalize a sequência com uma linha vazia.

### Demonstração automática

Para executar a demonstração padrão:

```bash
python main.py --demo
```

Para usar outro texto:

```bash
python main.py --demo "Minha Palavra"
```

### Execução com parâmetros

Exemplo usando um cubo:

```bash
python main.py --objeto cubo --seq "RZ 45; E 2 1 1; T 1 0 0"
```

Exemplo transformando um texto em 3D:

```bash
python main.py --texto "Olá" --3d --seq "RY 40; E 1 1.5 1; T 2 0 0" --gif
```

Para ver as opções disponíveis:

```bash
python main.py --help
```

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

## Resultados

Os gráficos e, quando solicitadas, as animações são salvos na pasta `saida/`. O programa também informa no terminal os arquivos produzidos.

## Testes

Para executar os casos de teste:

```bash
python testes.py
```

Os testes verificam operações matriciais, transformações 2D e 3D, matrizes inversas, autovalores e propriedades geométricas.
