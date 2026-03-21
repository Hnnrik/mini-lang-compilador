import sys
from scanner import Scanner, LexerError
from parser import parser, parserError, SemanticAnalyzer
from codegen import CodeGenerator


def compile_source(source_code):
    # 1. Scanner
    scanner = Scanner(source_code)
    tokens = scanner.get_tokens()

    # 2. Parser
    myparser = parser(tokens)
    ast = myparser.parser_program()

    # 3. Análise semântica
    sem = SemanticAnalyzer()
    sem.visit(ast)

    if sem.errors:
        return None

    # 4. Geração de código
    generator = CodeGenerator()
    python_code = generator.generate(ast)

    return python_code


if __name__ == "__main__":

    # 🔹 1. Verifica argumento
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.minilang>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        # 🔹 2. Lê arquivo
        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()

        # 🔹 3. Compila
        output = compile_source(source_code)

        if output:
            print("\n=== CÓDIGO GERADO ===\n")
            print(output)

            # 🔹 4. Salva saída
            output_file = filename.replace(".minilang", ".py")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)

            print(f"\nArquivo gerado: {output_file}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{filename}' não foi encontrado.")

    except LexerError as e:
        print("Erro léxico:", e)

    except parserError as e:
        print("Erro sintático:", e)

    except Exception as e:
        print("Erro desconhecido:", e)