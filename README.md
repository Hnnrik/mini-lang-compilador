# Mini-Lang Compiler

Este projeto implementa um transpilador da linguagem **Mini-Lang** para **Python**.  
O compilador realiza as etapas de análise léxica, sintática, semântica e geração de código.

## Pré‑requisitos

- Python 3.6 ou superior instalado.

## Estrutura do Projeto

- `scanner.py` – Analisador léxico.  
- `parser.py` – Analisador sintático, AST e analisador semântico.  
- `codegen.py` – Gerador de código Python.  
- `compilador.py` – Script principal que orquestra todas as fases.  
- `bnf.txt` – Gramática da linguagem em notação EBNF.

## Como Usar

1. Escreva um programa em Mini-Lang e salve com extensão `.minilang` (ex.: `exemplo.minilang`).

2. Execute o compilador passando o arquivo como argumento:

   ```bash
   python compilador.py exemplo.minilang    

3. Os tokens são printados quando o código é executado.
4. A árvore sintática pode ser acessada no arquivo ast.txt 