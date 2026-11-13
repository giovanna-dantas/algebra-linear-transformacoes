# Transformações Lineares e Composição Gráfica 2D (logo IFSP animado)

Projeto de Álgebra Linear (Tema 4). Python puro para a álgebra linear
(produto de matrizes, determinante, autovalores/autovetores feitos à mão);
Matplotlib e Pillow só desenham gráficos e montam o GIF.

## Como executar

```
pip install -r requirements.txt
python testes.py          # 2 casos de teste (entrada/saída esperada) + 1 extra
python main.py --demo     # gráficos, relatório e GIF do logo em ./saida
python main.py            # modo interativo
python gerar_figuras.py   # gráficos dos casos de teste
```

## Arquivos

- `matrizes.py`: operações de álgebra linear
- `transformacoes.py`: rotação, escala, cisalhamento, translação homogênea, composição
- `objetos.py`: objetos definidos por vértices (inclui o logo em letras de bloco)
- `graficos.py`: gráficos e GIF
- `relatorio.py`: relatório de execução (matrizes intermediárias e composta)
- `main.py`, `testes.py`, `gerar_figuras.py`
- `Relatorio_Transformacoes_Lineares.pdf`: relatório do trabalho
