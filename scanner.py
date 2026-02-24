KEYWORDS = {
    "var", "set", "def", "if", "else",
    "while", "return", "print",
    "int", "real", "bool", "void",
    "true", "false", "and", "or", "not"
}


class Scanner:

    def __init__(self, source):

        self.source = source
        self.position = 0
        self.current_char = source[0] if source else None


    def advance(self):

        self.position += 1

        if self.position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.position]


    def peek(self):

        if self.position + 1 >= len(self.source):
            return None

        return self.source[self.position + 1]


    def skip_whitespace(self):

        while self.current_char is not None and self.current_char.isspace():
            self.advance()


    def identifier(self):

        result = ""

        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == "_")):

            result += self.current_char
            self.advance()

        if result in KEYWORDS:
            print(f"<KEYWORD, {result}>")
        else:
            print(f"<IDENTIFIER, {result}>")


    def number(self):

        result = ""
        is_real = False

        while self.current_char is not None and (
                self.current_char.isdigit() or self.current_char == "."):

            if self.current_char == ".":

                if is_real:
                    break

                is_real = True

            result += self.current_char
            self.advance()

        if is_real:
            print(f"<REAL, {result}>")
        else:
            print(f"<INTEGER, {result}>")


    def string(self):

        result = ""
        self.advance()

        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()

        self.advance()

        print(f'<STRING, "{result}">')

    def skip_comment(self):

        # comentário de linha //
        if self.current_char == "/" and self.peek() == "/":

            self.advance()
            self.advance()

            while self.current_char is not None and self.current_char != "\n":
                self.advance()

        # comentário de bloco /* */
        elif self.current_char == "/" and self.peek() == "*":

            self.advance()
            self.advance()

            while self.current_char is not None:

                if self.current_char == "*" and self.peek() == "/":
                    self.advance()
                    self.advance()
                    break

                self.advance()
    def scan(self):

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
            
            elif self.current_char == "/" and (self.peek() == "/" or self.peek() == "*"):
                self.skip_comment()

            elif self.current_char.isalpha() or self.current_char == "_":
                self.identifier()

            elif self.current_char.isdigit():
                self.number()

            elif self.current_char == '"':
                self.string()

            elif self.current_char == "=" and self.peek() == "=":
                print("<EQ, ==>")
                self.advance()
                self.advance()

            elif self.current_char == "!" and self.peek() == "=":
                print("<NEQ, !=>")
                self.advance()
                self.advance()

            elif self.current_char == "<" and self.peek() == "=":
                print("<LTE, <=>")
                self.advance()
                self.advance()

            elif self.current_char == ">" and self.peek() == "=":
                print("<GTE, >=>")
                self.advance()
                self.advance()

            elif self.current_char == "=":
                print("<ASSIGN, =>>")
                self.advance()

            elif self.current_char == ":":
                print("<COLON, :>")
                self.advance()

            elif self.current_char == ";":
                print("<SEMICOLON, ;>")
                self.advance()

            elif self.current_char == "(":
                print("<LPAREN, (>")
                self.advance()

            elif self.current_char == ")":
                print("<RPAREN, )>")
                self.advance()

            elif self.current_char == "{":
                print("<LBRACE, {>")
                self.advance()

            elif self.current_char == "}":
                print("<RBRACE, }>")
                self.advance()

            elif self.current_char == "+":
                print("<PLUS, +>")
                self.advance()

            elif self.current_char == "-":
                print("<MINUS, ->")
                self.advance()

            elif self.current_char == "*":
                print("<MULT, *>")
                self.advance()

            elif self.current_char == "/" :
                print("<DIV, />")
                self.advance()

            elif self.current_char == "<":
                print("<LT, <>")
                self.advance()

            elif self.current_char == ">":
                print("<GT, >>")
                self.advance()

            elif self.current_char == ",":
                print("<COMMA, ,>")
                self.advance()

            else:
                print(f"<UNKNOWN, {self.current_char}>")
                self.advance()

def main():

    import sys

    if len(sys.argv) < 2:
        print("Uso: python scanner.py programa.txt")
        return

    filename = "programa.txt"

    try:

        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()

        scanner = Scanner(source_code)
        scanner.scan()

    except FileNotFoundError:
        print("Arquivo não encontrado.")


main()

