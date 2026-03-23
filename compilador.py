import sys
from scanner import Scanner, LexerError
from parser import parser, parserError, SemanticAnalyzer, print_ast

from codegen import CodeGenerator


def compile_source(source_code):
    #Scanner


    scanner = Scanner(source_code)
    tokens = scanner.get_tokens()


    #Parser
    myparser = parser(tokens)

    ast = myparser.parser_program()
    print_ast(ast)


    #Análise semântica
    sem = SemanticAnalyzer()
    sem.visit(ast)


    if sem.errors:
        return None
    #Geração de código
    generator = CodeGenerator()
    python_code = generator.generate(ast)

    return python_code


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Uso: python compilador.py <arquivo.minilang>")
        sys.exit(1)

    filename = sys.argv[1]

    try:

        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()
        output = compile_source(source_code)

        if output:
            print("\n=== CÓDIGO GERADO ===\n")
            print(output)
            output_file = filename.replace(".minilang", ".py")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
   
            print(f"\nArquivo gerado: {output_file}")

    except FileNotFoundError: 
        print(f"Erro: O arquivo '{filename}' não foi encontrado.") 


    except LexerError as e:
        print(e)

    except parserError as e:
        print(e)
    except Exception as e:
        print(e)