KEYWORDS = {
    "var", "set", "def", "if", "else",
    "while", "return", "print",
    "int", "real", "bool", "void",
    "true", "false", "and", "or", "not"
}


class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"<{self.type}, {self.value}> (L{self.line})"


class LexerError(Exception):
    pass


class Scanner:

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.current_char = source[0] if source else None

    def advance(self):
        if self.current_char == "\n":
            self.line += 1

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

    def skip_comment(self):
        # Comentário //
        if self.current_char == "/" and self.peek() == "/":
            while self.current_char is not None and self.current_char != "\n":
                self.advance()

        # Comentário #
        elif self.current_char == "#":
            while self.current_char is not None and self.current_char != "\n":
                self.advance()

    def identifier(self):
        result = ""

        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == "_")):
            result += self.current_char
            self.advance()

        if result in KEYWORDS:
            return Token("KEYWORD", result, self.line)
        return Token("IDENTIFIER", result, self.line)

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

        if result.endswith("."):
            raise LexerError(f"Número real inválido na linha {self.line}")

        if is_real:
            return Token("REAL", result, self.line)
        return Token("INTEGER", result, self.line)

    def string(self):
        result = ""
        self.advance()  

        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()

        if self.current_char is None:
            raise LexerError(f"String não fechada (linha {self.line})")

        self.advance()  # fecha "

        return Token("STRING", result, self.line)

    def get_tokens(self):
        tokens = []

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()

            elif (self.current_char == "/" and self.peek() in ["/"]) \
                    or self.current_char == "#":
                self.skip_comment()

            elif self.current_char.isalpha() or self.current_char == "_":
                tokens.append(self.identifier())

            elif self.current_char.isdigit():
                tokens.append(self.number())

            elif self.current_char == '"':
                tokens.append(self.string())

            # Operadores compostos
            elif self.current_char == "=" and self.peek() == "=":
                tokens.append(Token("EQ", "==", self.line))
                self.advance()
                self.advance()

            elif self.current_char == "!" and self.peek() == "=":
                tokens.append(Token("NEQ", "!=", self.line))
                self.advance()
                self.advance()

            elif self.current_char == "<" and self.peek() == "=":
                tokens.append(Token("LTE", "<=", self.line))
                self.advance()
                self.advance()

            elif self.current_char == ">" and self.peek() == "=":
                tokens.append(Token("GTE", ">=", self.line))
                self.advance()
                self.advance()

            # Operadores simples
            elif self.current_char == "=":
                tokens.append(Token("ASSIGN", "=", self.line))
                self.advance()

            elif self.current_char == "<":
                tokens.append(Token("LT", "<", self.line  ))
                self.advance()

            elif self.current_char == ">":
                tokens.append(Token("GT", ">", self.line  ))
                self.advance()

            elif self.current_char == "+":
                tokens.append(Token("PLUS", "+", self.line  ))
                self.advance()

            elif self.current_char == "-":
                tokens.append(Token("MINUS", "-", self.line  ))
                self.advance()

            elif self.current_char == "*":
                tokens.append(Token("MULT", "*", self.line  ))
                self.advance()

            elif self.current_char == "/":
                tokens.append(Token("DIV", "/", self.line  ))
                self.advance()

            elif self.current_char == ":":
                tokens.append(Token("COLON", ":", self.line  ))
                self.advance()

            elif self.current_char == ";":
                tokens.append(Token("SEMICOLON", ";", self.line  ))
                self.advance()

            elif self.current_char == "(":
                tokens.append(Token("LPAREN", "(", self.line  ))
                self.advance()

            elif self.current_char == ")":
                tokens.append(Token("RPAREN", ")", self.line  ))
                self.advance()

            elif self.current_char == "{":
                tokens.append(Token("LBRACE", "{", self.line  ))
                self.advance()

            elif self.current_char == "}":
                tokens.append(Token("RBRACE", "}", self.line  ))
                self.advance()

            elif self.current_char == ",":
                tokens.append(Token("COMMA", ",", self.line  ))
                self.advance()

            else:
                raise LexerError(
                    f"Caractere inválido '{self.current_char}' "
                    f"(linha {self.line})"
                )

        tokens.append(Token("EOF", None, self.line  ))
        return tokens
    

def main():
        filename = "text.txt"

        try:
            with open(filename, "r", encoding="utf-8") as file:
                source_code = file.read()

            scanner = Scanner(source_code)
            tokens = scanner.get_tokens()

            for token in tokens:
                print(token)

        except FileNotFoundError:
            print("Arquivo não encontrado.")
        except LexerError as e:
            print("Erro léxico:", e)


if __name__ == "__main__":
    main()