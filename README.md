<div align="center">
  
# MINI-LANG-COMPILADOR
*Compiler Architecture*

![Language](https://img.shields.io/badge/LANGUAGE-MINI--LANG-5e2750?style=for-the-badge)
![Target](https://img.shields.io/badge/TARGET-PYTHON-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Build](https://img.shields.io/badge/BUILD-DEVELOPMENT-black?style=for-the-badge)

</div>

---

## VISÃO GERAL

O objetivo deste projeto é o desenvolvimento prático de um **COMPILADOR** para a linguagem Mini-Lang. O software realiza a leitura de códigos escritos em Mini-Lang e os traduz automaticamente para uma linguagem de alto nível. Onde a linguagem de alto nível escolhida foi o python.

---

## ARQUITETURA

> **1. Análise Léxica (Scanner)**
> Conversão do código-fonte em uma sequência de tokens válidos, ignorando elementos não estruturais como comentários e espaços em branco.

> **2. Análise Sintática (Parser)**
> Validação das regras gramaticais e mapeamento da estrutura do programa em uma Árvore Sintática Abstrata (AST).

> **3. Análise Semântica**
> Análise de coerência lógica, garantindo a declaração prévia de variáveis, consistência de tipagem e respeito aos escopos.

> **4. Geração de Código**
> Transformação da AST em código Python válido, resultando em um script pronto para execução nativa.

---

## COMO EXECUTAR

Executa cada fase de forma individual dentro do seu próprio arquivo.
