import sys
from scanner import Scanner, Token

class parserError(Exception):
    pass

class parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position] if self.tokens else None

    def error(self, message):
        linha = self.current_token.line if self.current_token else "EOF"
        raise parserError(f"Erro de sintaxe na linha {linha}: {message}")

    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def match(self, expected_type, expected_value=None):
        if self.current_token is None:
            self.error(f"Fim de arquivo. Esperado: {expected_type}")

        if self.current_token.type == expected_type:
            if expected_value is not None and self.current_token.value != expected_value:
                self.error(f"queria esse '{expected_value}', mas ganhei esse '{self.current_token.value}'")
            
            consumed_token = self.current_token
            self.advance()
            return consumed_token
        else:
            self.error(f"queria esse tipo '{expected_type}', mas achei esse '{self.current_token.type}'")
    
    #<program> => <statement> <program> | e
    def parser_program(self):
        while self.current_token is not None and self.current_token.type != "EOF": 
            self.parser_statement()
    
#<block> => "{" <block_rec> "}"
#<block_rec> => <statement><block_rec> | e

    def parser_block(self):
        self.match("LBRACE")
        while self.current_token is not None and self.current_token.type != "RBRACE":
            self.parser_statement()
        self.match("RBRACE")
            
        #<statement> => <variable-decl> ";"
              #| <assignment> ";"
              #| <print-statement> ";"
              #| <if-statement>
              #| <while-statement>
              #| <return-statement> ";"
              #| <function-decl>
              #| <block>
              
    def parser_statement(self):
        if self.current_token.type == "KEYWORD":
            if self.current_token.value == "var":
                self.parser_variable_decl()
                self.match("SEMICOLON")
            elif self.current_token.value == "set":
                self.parser_assignment()
                self.match("SEMICOLON")
            elif self.current_token.value == "print":
                self.parser_print_statement()
                self.match("SEMICOLON")
            elif self.current_token.value == "if":
                self.parser_if_statement()
            elif self.current_token.value == "while":
                self.parser_while_statement()
            elif self.current_token.value == "return":
                self.parser_return_statement()
                self.match("SEMICOLON")
            elif self.current_token.value == "def":
                self.parser_function_decl()
            else:
                self.error(f"Comando não reconhecido: '{self.current_token.value}'")
        elif self.current_token.type == "LBRACE":
            self.parser_block()
        else:
            self.error(f"Token inesperado: '{self.current_token}'")
#<function-decl> => "def" <identifier> "(" <formal_params_opt> ")" ":" <type> <block>
#<formal_params_opt> => <formal-params> | e
# <variable-decl> => "var" <identifier> ":" <type> "=" <expression>
    def parser_variable_decl(self):
        self.match("KEYWORD", "var")
        self.match("IDENTIFIER")
        self.match("COLON")
        self.parser_type()
        self.match("ASSIGN") 
        self.parser_expression()

    # <assignment> => "set" <identifier> "=" <expression>
    def parser_assignment(self):
        self.match("KEYWORD", "set")
        self.match("IDENTIFIER")
        self.match("ASSIGN")
        self.parser_expression()


    def parser_function_decl(self):
        self.match("KEYWORD", "def")
        self.match("IDENTIFIER")
        self.match("LPAREN")

        if self.current_token.type != "RPAREN":
            self.parser_formal_params()   
        self.match("RPAREN")
        self.match("COLON")
        self.parser_type()
        self.parser_block()

# <formal-params> => <formal-param> <formal-param_list>
# <formal-param_list> => "," <formal-param> <formal-param_list> | e
# <formal-param> => <identifier> ":" <type>
    def parser_formal_params(self):
        self.parser_formal_param()
        
        while self.current_token is not None and self.current_token.type == "COMMA":
            
            self.match("COMMA")          
            self.parser_formal_param()    

    def parser_formal_param(self):
        self.match("IDENTIFIER")
        self.match("COLON")
        self.parser_type()

# <while-statement> => "while" "(" <expression> ")" <block>

    def parser_while_statement(self):
        self.match("KEYWORD", "while")
        self.match("LPAREN")

       
        self.parser_expression() 
        self.match("RPAREN")
        self.parser_block()

# <if-statement> => "if" "(" <expression> ")" <block> <opt_else>
# <opt_else> => "else" <block> | e

    def parser_if_statement(self):
        self.match("KEYWORD", "if")
        self.match("LPAREN")

        
        self.parser_expression() 
        self.match("RPAREN")
        self.parser_block()
        self.parser_opt_else()

    def parser_opt_else(self):
        if self.current_token is not None and self.current_token.value == "else":
            self.match("KEYWORD", "else")
            self.parser_block()



# <return-statement> => "return" <expression>
    def parser_return_statement(self):
        self.match("KEYWORD", "return")
        self.parser_expression()

#<print-statement> => "print" <string-literal>
    def parser_print_statement(self):
        self.match("KEYWORD", "print")
        self.parser_expression()

# <type> => "int" | "real" | "bool" | "void"
    def parser_type(self):
        tipos_validos = ["int", "real", "bool", "void"]
        
        if self.current_token is not None and \
           self.current_token.type == "KEYWORD" and \
           self.current_token.value in tipos_validos:
            self.match("KEYWORD", self.current_token.value)
            
        else:
            self.error("Esperado um tipo válido ('int', 'real', 'bool' ou 'void')")


# <string-literal> => " " " <string_char_list> " " "
# <string_char_list> => <string_char> <string_char_list> | e
# <string_char> => <letter> | <digit> | <symbol>
# <symbol> => <any-char-except-quote>
# <digit> => "0" | ... | "9"
# <letter> => "a" | ... | "z" | "A" | ... | "Z"

    def parser_string_literal(self):
        self.match("STRING")

    # <expression> => <simple-expression> { <relational-op> <simple-expression> }
    def parser_expression(self):
        self.parser_simple_expression()
        
        operadores_relacionais = ["<", ">", "==", "!=", "<=", ">="]
        
        while self.current_token is not None and self.current_token.value in operadores_relacionais:
            self.match(self.current_token.type) 
            self.parser_simple_expression()

# <simple-expression> => <term> <additive_list>
# <additive_list> => <additive-op> <term> <additive_list> | e
# <additive-op> => "+" | "-" | "or"

# <term> => <factor> { <multiplicative-op> <factor> }

    def parser_simple_expression(self):
        self.parser_term()
        while self.current_token is not None and (
            self.current_token.type in ["PLUS", "MINUS"] or 
            (self.current_token.type == "KEYWORD" and self.current_token.value == "or")
        ):
            self.match(self.current_token.type) 
            self.parser_term()

    def parser_term(self):
        self.parser_factor()
        while self.current_token is not None and (
            self.current_token.type in ["MULT", "DIV"] or 
            (self.current_token.type == "KEYWORD" and self.current_token.value == "and")
        ):
            self.match(self.current_token.type)
            self.parser_factor()


# <factor> => <literal> | <identifier> | <function-call> | <sub-expression> | <unary>
    def parser_factor(self):
        if self.current_token is None:
            self.error("Fim de arquivo inesperado dentro de uma expressao")
            
        #<literal> 
        if self.current_token.type in ["INTEGER", "REAL", "STRING"]:
            self.match(self.current_token.type)
        elif self.current_token.value in ["true", "false"]:
            self.match("KEYWORD", self.current_token.value)
            
        # <identifier> or <function-call>
        elif self.current_token.type == "IDENTIFIER":
            self.match("IDENTIFIER")
            if self.current_token is not None and self.current_token.type == "LPAREN":
                self.parser_function_call_tail()
                
        # <sub-expression> => "(" <expression> ")"
        elif self.current_token.type == "LPAREN":
            self.match("LPAREN")
            self.parser_expression()
            self.match("RPAREN")
            
        # <unary> => ("+" | "-" | "not") <expression>
        elif self.current_token.type in ["PLUS", "MINUS"] or \
             (self.current_token.type == "KEYWORD" and self.current_token.value == "not"):
            self.match(self.current_token.type)
            self.parser_factor()
            
        else:
            self.error(f"Fator invalido na expressao: '{self.current_token.value}'")

    def parser_function_call_tail(self):
        self.match("LPAREN")
        if self.current_token.type != "RPAREN":
            self.parser_expression()
            while self.current_token is not None and self.current_token.type == "COMMA":
                self.match("COMMA")
                self.parser_expression()
        self.match("RPAREN")

if __name__ == "__main__":
    from scanner import Scanner, LexerError

    teste = """
var a : int = 5;
//isso é um comentario
var resultado : int = 1;

def calcular(n : int) : int {
    if (n > 0) {
        return n * calcular(n - 1);
    }
    return 1;
}

print "Calculando Fatorial de 5:";
set resultado = calcular(x);
print resultado;
     """
    try:
        scanner = Scanner(teste)
        tokens = scanner.get_tokens() 
        
        MYparser = parser(tokens) 
        MYparser.parser_program()
        
        print("O Parser validou o código perfeitamente!")

    except LexerError as e:
        print(f"ERRO NO SCANNER: {e}")
    except parserError as e:
        print(f"ERRO NO PARSER: {e}")
    except Exception as e:
        print(f"ERRO DESCONHECIDO: {e}")
