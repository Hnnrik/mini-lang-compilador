import sys
from scanner import Scanner, Token

class parserError(Exception):
    pass

class parser:
    def __init__(self, Token):
        self.Token = Token
        self.position = 0
        self.current_token = self.Token[self.position] if self.Token else None

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
        while self.current_token is None or self.current_token.type != "RBRACE":
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
                self.parser.while_statement()
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

        if self.current_token.type != "RPAREN":
            self.parser_expression() 
        self.match("RPAREN")
        self.parser_block()

# <if-statement> => "if" "(" <expression> ")" <block> <opt_else>
# <opt_else> => "else" <block> | e

    def parser_if_statement(self):
        self.match("KEYWORD", "if")
        self.match("LPAREN")

        if self.current_token.type != "RPAREN":
            self.parser_expression() 
        self.match("RPAREN")
        self.parser_block()
        self.parser_opt_else()

    def parser_opt_else(self):
        self.match("KEYWORD", "else")
        self.parser_block()



# <return-statement> => "return" <expression>
    def parser_return_statement(self):
        self.match("KEYWORD", "return")
        self.parser_expression()

#<print-statement> => "print" <string-literal>
    def parser_print_statement(self):
        self.match("KEYWORD", "print")
        self.parser_string_literal()

# <type> => "int" | "real" | "bool" | "void"
    def parser_type(self):

# <variable-decl> => "var" <identifier> ":" <type> <expression>
# <assignment> => "set" <identifier> "=" <expression>

# <expression> => <simple-expression> <relational_list>
#<relational_list> => <relational-op> <simple-expression> <relational_list> | e

#<simple-expression> => <term> <additive_list>
#<additive_list> => <additive-op> <term> <additive_list> | e

#<term> => <factor> <multiplicative_list>
#<multiplicative_list> => <multiplicative-op> <factor> <multiplicative_list> | e

#<factor> => <literal> | <identifier> | <function-call> | <sub-expression> | <unary>

#<unary> => <unary_op> <expression_list>
#<unary_op> => "+" | "-" | "not"
#<expression_list> => <expression> <expression_list> | e

#<sub-expression> => "(" <expression> ")"

#<function-call> => <identifier> "(" <opt_actual_params> ")"

#<actual-params> => <expression> <actual-param_list>
#<opt_actual_params> => <actual-params> | e

#<actual-param_list> => "," <expression> <actual-param_list> | e

#<relational-op> => "<" | ">" | "==" | "!=" | "<=" | ">="

#     def parser_relational_op(self):
#         self.match("PLUS") 
        
# #<additive-op> => "+" | "-" | "or"
#<multiplicative-op> => "*" | "/" | "and"

#<identifier> => <id_start> <id_rest_list>
#<id_start> => "_" | <letter>
#<id_rest_list> => <id_rest> <id_rest_list> | e
#<id_rest> => "_" | <letter> | <digit>

#<digit> => "0" | ... | "9"
#<letter> => "a" | ... | "z" | "A" | ... | "Z"

#<literal> => <integer-literal> | <real-literal> | "true" | "false"

#<integer-literal> => <digit> <digit_list>
#<digit_list> => <digit> <digit_list> | e

#<real-literal> => <integer-literal> "." <integer-literal>

#<string-literal> => " " " <string_char_list> " " "
#<string_char_list> => <string_char> <string_char_list> | e
#<string_char> => <letter> | <digit> | <symbol>
#<symbol> => <any-char-except-quote>