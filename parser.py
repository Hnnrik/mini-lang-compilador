import sys
from scanner import Scanner, Token

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, Token):
        self.Token = Token
        self.position = 0
        self.current_token = self.Token[self.position] if self.Token else None

    def error(self, message):
        linha = self.current_token.line if self.current_token else "EOF"
        raise ParserError(f"Erro de sintaxe na linha {linha}: {message}")

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
            self.parse_formal_params()   
        self.match("RPAREN")
        self.match("COLON")
        self.parse_type()
        self.parse_block()

# <formal-params> => <formal-param> <formal-param_list>
# <formal-param_list> => "," <formal-param> <formal-param_list> | e
# <formal-param> => <identifier> ":" <type>
    def parse_formal_params(self):
        self.parse_formal_param()
        
        while self.current_token is not None and self.current_token.type == "COMMA":
            
            self.match("COMMA")          
            self.parse_formal_param()    

    def parse_formal_param(self):
        self.match("IDENTIFIER")
        self.match("COLON")
        self.parse_type()