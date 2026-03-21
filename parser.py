import sys
from scanner import Scanner, Token

class parserError(Exception):
    pass

class parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position] if self.tokens else None
        self.last_token = None  

    def error(self, message):
        if self.current_token:
            linha = self.current_token.line
        elif self.last_token:
            linha = self.last_token.line
        else:
            linha = "desconhecida"

        raise parserError(f"Erro de sintaxe na linha {linha}: {message}")

    def advance(self):
        if self.current_token:
            self.last_token = self.current_token 

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
                self.error(f"Esperando por '{expected_value}', mas achei esse '{self.current_token.value}'")
            
            consumed_token = self.current_token
            self.advance()
            return consumed_token
        else:
            self.error(f"Esperando por '{expected_type}', mas achei esse '{self.current_token.type}'")
    
    #<program> => <statement> <program> | e
    def parser_program(self):
        statements = []
        while self.current_token is not None and self.current_token.type != "EOF": 
            stmt = self.parser_statement()
            if stmt is not None:
                statements.append(stmt)
        return Program(statements)
    
#<block> => "{" <block_rec> "}"
#<block_rec> => <statement><block_rec> | e

    def parser_block(self):
        self.match("LBRACE")
        statements = []
        while self.current_token is not None and self.current_token.type != "RBRACE":
            stmt = self.parser_statement()
            if stmt is not None:
                statements.append(stmt)
        self.match("RBRACE")
        return Block(statements)
            
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
                node = self.parser_variable_decl()
                self.match("SEMICOLON")
                return node
            elif self.current_token.value == "set":
                node = self.parser_assignment()
                self.match("SEMICOLON")
                return node
            elif self.current_token.value == "print":
                node = self.parser_print_statement()
                self.match("SEMICOLON")
                return node
            elif self.current_token.value == "if":
                return self.parser_if_statement()
            elif self.current_token.value == "while":
                return self.parser_while_statement()
            elif self.current_token.value == "return":
                node = self.parser_return_statement()
                self.match("SEMICOLON")
                return node
            elif self.current_token.value == "def":
                return self.parser_function_decl()
            else:
                self.error(f"Comando não reconhecido: '{self.current_token.value}'")
        elif self.current_token.type == "LBRACE":
            return self.parser_block()
        else:
            self.error(f"Token inesperado: '{self.current_token}'")
#<function-decl> => "def" <identifier> "(" <formal_params_opt> ")" ":" <type> <block>
#<formal_params_opt> => <formal-params> | e
# <variable-decl> => "var" <identifier> ":" <type> "=" <expression>
    def parser_variable_decl(self):
        self.match("KEYWORD", "var")
        token = self.match("IDENTIFIER")
        ident = token.value
        line = token.line

        self.match("COLON")
        var_type = self.parser_type()
        self.match("ASSIGN")
        expr = self.parser_expression()
        return VarDecl(ident, var_type, expr, line=line)

    # <assignment> => "set" <identifier> "=" <expression>
    def parser_assignment(self):
        self.match("KEYWORD", "set")
        token = self.match("IDENTIFIER")
        ident = token.value
        line = token.line

        self.match("ASSIGN")
        expr = self.parser_expression()
        return Assignment(ident, expr, line=line)


    def parser_function_decl(self):
        self.match("KEYWORD", "def")
        name = self.match("IDENTIFIER").value
        self.match("LPAREN")
        params = []
        if self.current_token.type != "RPAREN":
            params = self.parser_formal_params()
        self.match("RPAREN")
        self.match("COLON")
        ret_type = self.parser_type()
        body = self.parser_block()
        return FunctionDecl(name, params, ret_type, body)

# <formal-params> => <formal-param> <formal-param_list>
# <formal-param_list> => "," <formal-param> <formal-param_list> | e
# <formal-param> => <identifier> ":" <type>
    def parser_formal_params(self):
        params = []

        params.append(self.parser_formal_param())
        while self.current_token is not None and self.current_token.type == "COMMA":
            self.match("COMMA")
            params.append(self.parser_formal_param())
        return params 

    def parser_formal_param(self):
        name = self.match("IDENTIFIER").value
        self.match("COLON")
        typ = self.parser_type()
        return (name, typ)
# <while-statement> => "while" "(" <expression> ")" <block>

    def parser_while_statement(self):
        self.match("KEYWORD", "while")
        self.match("LPAREN")
        cond = self.parser_expression()
        self.match("RPAREN")
        body = self.parser_block()
        return WhileStmt(cond, body)

# <if-statement> => "if" "(" <expression> ")" <block> <opt_else>
# <opt_else> => "else" <block> | e

    def parser_if_statement(self):
        self.match("KEYWORD", "if")
        self.match("LPAREN")
        cond = self.parser_expression()
        self.match("RPAREN")
        then_block = self.parser_block()
        else_block = self.parser_opt_else()
        return IfStmt(cond, then_block, else_block)

    def parser_opt_else(self):
        if self.current_token is not None and self.current_token.value == "else":
            self.match("KEYWORD", "else")
            return self.parser_block()
        return None



# <return-statement> => "return" <expression>
    def parser_return_statement(self):
        self.match("KEYWORD", "return")
        expr = self.parser_expression()
        return ReturnStmt(expr)

#<print-statement> => "print" <string-literal>
    def parser_print_statement(self):
        token = self.match("KEYWORD", "print")
        line = token.line
        expr = self.parser_expression()
        return PrintStmt(expr, line=line)

# <type> => "int" | "real" | "bool" | "void"
    def parser_type(self):
        tipos_validos = ["int", "real", "bool", "void"]
        if self.current_token is not None and \
        self.current_token.type == "KEYWORD" and \
        self.current_token.value in tipos_validos:
            
            return self.match("KEYWORD", self.current_token.value).value
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
        left = self.parser_simple_expression()
        while self.current_token is not None and self.current_token.value in ["<", ">", "==", "!=", "<=", ">="]:
            token = self.current_token
            op = token.value
            self.match(self.current_token.type)  
            right = self.parser_simple_expression()
            left = BinaryOp(op, left, right, line=token.line)
        return left

# <simple-expression> => <term> <additive_list>
# <additive_list> => <additive-op> <term> <additive_list> | e
# <additive-op> => "+" | "-" | "or"

# <term> => <factor> { <multiplicative-op> <factor> }

    def parser_simple_expression(self):
        left = self.parser_term()
        while self.current_token is not None and (
            self.current_token.type in ["PLUS", "MINUS"] or 
            (self.current_token.type == "KEYWORD" and self.current_token.value == "or")
        ):

            token = self.current_token
            op = token.value
            self.match(self.current_token.type)
            right = self.parser_term()
            left = BinaryOp(op, left, right, line=token.line)
        return left

    def parser_term(self):
        left = self.parser_factor()
        while self.current_token is not None and (
            self.current_token.type in ["MULT", "DIV"] or 
            (self.current_token.type == "KEYWORD" and self.current_token.value == "and")
        ):
            token = self.current_token
            op = token.value
            self.match(self.current_token.type)
            right = self.parser_factor()
            left = BinaryOp(op, left, right, line=token.line)
        return left


# <factor> => <literal> | <identifier> | <function-call> | <sub-expression> | <unary>
    def parser_factor(self):
        if self.current_token is None:
            self.error("Fim de arquivo inesperado dentro de uma expressao")
            
        #<literal> 
        if self.current_token.type in ["INTEGER", "REAL", "STRING"]:
            token = self.match(self.current_token.type)

            if token.type == "INTEGER":
                return Literal(int(token.value), "int", line=token.line)
            elif token.type == "REAL":
                return Literal(float(token.value), "real", line=token.line)
            elif token.type == "STRING":
                return Literal(token.value, "string", line=token.line)
            
        elif self.current_token.value in ["true", "false"]:
            token = self.match("KEYWORD", self.current_token.value)
            return Literal(True if token.value == "true" else False, "bool", line=token.line)
            
        # <identifier> or <function-call>
        elif self.current_token.type == "IDENTIFIER":
            token = self.match("IDENTIFIER")
            ident = token.value
            line = token.line

            if self.current_token is not None and self.current_token.type == "LPAREN":
                args = self.parser_function_call_tail()
                return CallExpr(ident, args, line=line)
            else:
                return Identifier(ident, line=line)
                
        # <sub-expression> => "(" <expression> ")"
        elif self.current_token.type == "LPAREN":
            self.match("LPAREN")
            expr = self.parser_expression()
            self.match("RPAREN")
            return expr
            
        # <unary> => ("+" | "-" | "not") <expression>
        elif self.current_token.type in ["PLUS", "MINUS"] or \
            (self.current_token.type == "KEYWORD" and self.current_token.value == "not"):
            
            token = self.current_token
            op = token.value
            self.match(self.current_token.type)
            operand = self.parser_factor()
            return UnaryOp(op, operand, line=token.line)
            
        else:
            self.error(f"Fator invalido na expressao: '{self.current_token.value}'")

    def parser_function_call_tail(self):
        self.match("LPAREN")
        args = []
        if self.current_token.type != "RPAREN":
            args.append(self.parser_expression())
            while self.current_token is not None and self.current_token.type == "COMMA":
                self.match("COMMA")
                args.append(self.parser_expression())
        self.match("RPAREN")
        return args

class ASTNode:
    def __init__(self, line=None):
        self.line = line

    def to_dict(self):
        return {"tipo": self.__class__.__name__}

    def print_ast(self, indent=0):              
        print(" " * indent + repr(self))

    def __repr__(self):                         
        return f"<{self.__class__.__name__}>"


class Program(ASTNode):
    def __init__(self, statements, line=None):
        super().__init__(line)
        self.statements = statements

    def print_ast(self, indent=0):              
        print(" " * indent + "| [program]")
        for stmt in self.statements:
            stmt.print_ast(indent + 2)


class Block(ASTNode):
    def __init__(self, statements, line=None):
        super().__init__(line)
        self.statements = statements

    def print_ast(self, indent=0):              
        print(" " * indent + "| [block] {")
        for stmt in self.statements:
            stmt.print_ast(indent + 2)
        print(" " * indent + "| }")


class VarDecl(ASTNode):
    def __init__(self, name, var_type, expression, line=None):
        super().__init__(line)
        self.name = name
        self.var_type = var_type
        self.expression = expression

    def print_ast(self, indent=0):              
        print(" " * indent + f"| [variable decl] : ")
        print(" " * indent + "  | [name] " + self.name)
        print(" " * indent + "  | [type] " + self.var_type)
        self.expression.print_ast(indent + 2)


class Assignment(ASTNode):
    def __init__(self, name, expression, line=None):
        super().__init__(line)
        self.name = name
        self.expression = expression

    def print_ast(self, indent=0):            
        print(" " * indent + f"| [assignment] =")
        print(" " * indent + "  | [name] " + self.name)
        self.expression.print_ast(indent + 2)


class PrintStmt(ASTNode):
    def __init__(self, expr, line=None):
        super().__init__(line)
        self.expr = expr

    def print_ast(self, indent=0):              
        print(" " * indent + "| print")
        self.expr.print_ast(indent + 2)


class IfStmt(ASTNode):
    def __init__(self, condition, then_block, else_block=None, line=None):
        super().__init__(line)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def print_ast(self, indent=0):            
        print(" " * indent + "| if (")
        self.condition.print_ast(indent + 2)
        print(" " * indent + "| ) {")
        self.then_block.print_ast(indent + 2)
        print(" " * indent + "| }")
        if self.else_block:
            print(" " * (indent) + "| else {")
            self.else_block.print_ast(indent + 2)
            print(" " * (indent) + "| }")


class WhileStmt(ASTNode):
    def __init__(self, condition, body, line=None):
        super().__init__(line)
        self.condition = condition
        self.body = body

    def print_ast(self, indent=0):              
        print(" " * indent + "| while")
        print(" " * (indent + 2) + "| [condition]")
        self.condition.print_ast(indent + 4)
        print(" " * (indent + 2) + "| [code]")
        self.body.print_ast(indent + 4)


class ReturnStmt(ASTNode):
    def __init__(self, expression, line=None):
        super().__init__(line)
        self.expression = expression

    def print_ast(self, indent=0):              
        print(" " * indent + "| return")
        self.expression.print_ast(indent + 2)


class FunctionDecl(ASTNode):
    def __init__(self, name, params, return_type, body, line=None):
        super().__init__(line)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def print_ast(self, indent=0):              
        params_str = ", ".join(f"{n}: {t}" for n, t in self.params)
        print(" " * indent + f"| [function decl]: {self.name}({params_str}) -> {self.return_type}")
        self.body.print_ast(indent + 2)


class BinaryOp(ASTNode):
    def __init__(self, op, left, right, line=None):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

    def print_ast(self, indent=0):             
        print(" " * indent + f"| [binary op] {self.op}")
        self.left.print_ast(indent + 2)
        self.right.print_ast(indent + 2)


class UnaryOp(ASTNode):
    def __init__(self, op, operand, line=None):
        super().__init__(line)
        self.op = op
        self.operand = operand

    def print_ast(self, indent=0):             
        print(" " * indent + f"| [unary op] {self.op}")
        self.operand.print_ast(indent + 2)


class CallExpr(ASTNode):
    def __init__(self, name, arguments, line=None):
        super().__init__(line)
        self.name = name
        self.arguments = arguments

    def print_ast(self, indent=0):             
        print(" " * indent + f"CallExpr: {self.name}()")
        for i, arg in enumerate(self.arguments):
            print(" " * (indent + 2) + f"arg[{i}]:")
            arg.print_ast(indent + 4)


class Identifier(ASTNode):
    def __init__(self, name, line=None):
        super().__init__(line)
        self.name = name

    def print_ast(self, indent=0):             
        print(" " * indent + f"| [identifier] {self.name}")


class Literal(ASTNode):
    def __init__(self, value, lit_type, line=None):
        super().__init__(line)
        self.value = value
        self.lit_type = lit_type

    def print_ast(self, indent=0):            
        print(" " * indent + f"| [literal] {self.value!r}")

def print_ast(tree):
    """Imprime a AST inteira com indentação."""
    print("\n=== Árvore Sintática Abstrata ===")
    tree.print_ast()
    print("=================================\n")



class Symbol:
    def __init__(self, name, sym_type, kind, line=None): #kind é pra ser  'var' ou 'func'
        self.name = name
        self.type = sym_type
        self.kind = kind
        self.line = line

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = []       
        self.current_function = None  

        self.errors = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def add_symbol(self, name, sym):
        scope = self.scopes[-1]
        if name in scope:
            self.error(f"Símbolo '{name}' já declarado neste escopo", sym.line)
        else:
            scope[name] = sym

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def error(self, msg, line=None):
        self.errors.append(msg)
        if line:
            print(f"Erro semântico na linha {line}: {msg}")
        else:
            print(f"Erro semântico: {msg}")

    def visit_program(self, node):
        self.push_scope()



        for stmt in node.statements:
            self.visit(stmt)
        self.pop_scope()

    def visit_block(self, node):
        self.push_scope()
        for stmt in node.statements:
            self.visit(stmt)
        self.pop_scope()

    def visit_var_decl(self, node):
    
        sym = Symbol(node.name, node.var_type, 'var', line=node.line)
        self.add_symbol(node.name, sym)
    
    
        expr_type = self.visit_expression(node.expression)
        if expr_type != node.var_type:
            self.error(f"Tipo incompatível na inicialização de '{node.name}': esperado {node.var_type}, obtido {expr_type}",node.line)

    def visit_assignment(self, node):
        sym = self.lookup(node.name)
        if sym is None:
            self.error(f"Variável '{node.name}' não declarada", node.line)
        else:
            expr_type = self.visit_expression(node.expression)
            if expr_type != sym.type:
                self.error(f"Atribuição inválida para '{node.name}': esperado {sym.type}, obtido {expr_type}")

    def visit_print_stmt(self, node):
        expr_type = self.visit_expression(node.expr)
        if expr_type not in ("int", "real", "bool", "string"):
            self.error(f"print não pode exibir valor do tipo {expr_type}", node.line)

    def visit_if_stmt(self, node):
        cond_type = self.visit_expression(node.condition)
        if cond_type != "bool":
            self.error(f"Condição do if deve ser booleana, recebeu {cond_type}")
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_while_stmt(self, node):
        cond_type = self.visit_expression(node.condition)
        if cond_type != "bool":
            self.error(f"Condição do while deve ser booleana, recebeu {cond_type}")
        self.visit(node.body)

    def visit_return_stmt(self, node):
        expr_type = self.visit_expression(node.expression)
        if self.current_function is None:
            self.error("return fora de função")
        else:
            expected = self.current_function.type  
            if expr_type != expected:
                self.error(f"Tipo de retorno incompatível: esperado {expected}, obtido {expr_type}")

    def visit_function_decl(self, node):


        sym = Symbol(node.name, node.return_type, 'func')
        sym.params = node.params
        self.add_symbol(node.name, sym)
        self.push_scope()
        for param_name, param_type in node.params:
            param_sym = Symbol(param_name, param_type, 'var')
            self.add_symbol(param_name, param_sym)
        old_func = self.current_function
        self.current_function = sym


        self.visit(node.body)

        self.current_function = old_func
        self.pop_scope()

    def visit_expression(self, expr):
        if isinstance(expr, BinaryOp):
            left = self.visit_expression(expr.left)
            right = self.visit_expression(expr.right)
  
            if expr.op in ["+", "-", "*", "/"]:
                if left in ("int", "real") and right in ("int", "real"):

                    if left == "real" or right == "real":
                        return "real"
                    return "int"
                else:
                    self.error(f"Operador aritmético '{expr.op}' requer operandos numéricos (int/real), recebeu {left} e {right}", expr.line)
                    return "error"
            elif expr.op in ["or", "and"]:
                if left == "bool" and right == "bool":
                    return "bool"
                else:
                    self.error(f"Operador aritmético '{expr.op}' requer operandos numéricos (int/real), recebeu {left} e {right}", expr.line)
                    return "error"
            elif expr.op in ["<", ">", "<=", ">=", "==", "!="]:

                if left in ("int", "real") and right in ("int", "real"):
                    return "bool"
                else:
                    self.error(f"Operador aritmético '{expr.op}' requer operandos numéricos (int/real), recebeu {left} e {right}", expr.line)
                    return "error"
            else:
                self.error(f"Operador desconhecido '{expr.op}'")
                return "error"

        elif isinstance(expr, UnaryOp):
            operand = self.visit_expression(expr.operand)
            if expr.op == "not":
                if operand != "bool":
                    self.error(f"Operador 'not' requer bool, recebeu {operand}", expr.line)
                return "bool"
            elif expr.op in ("+", "-"):
                if operand not in ("int", "real"):
                    self.error(f"Operador unário '{expr.op}' requer numérico, recebeu {operand}", expr.line)
                return operand
            else:
                return "error"

        elif isinstance(expr, Literal):
            return expr.lit_type

        elif isinstance(expr, Identifier):
            sym = self.lookup(expr.name)
            if sym is None:
                self.error(f"Variável '{expr.name}' não declarada", expr.line)
                return "error"
            return sym.type

        elif isinstance(expr, CallExpr):
            sym = self.lookup(expr.name)
            if sym is None:
                self.error(f"Função '{expr.name}' não declarada", expr.line)
                return "error"
            if sym.kind != 'func':
                self.error(f"'{expr.name}' não é uma função", expr.line)
                return "error"

            expected_args = len(sym.params)
            given_args = len(expr.arguments)
            if expected_args != given_args:
                self.error(f"Função '{expr.name}' espera {expected_args} argumentos, recebeu {given_args}", expr.line)
                return "error"

            for (param_name, param_type), arg_expr in zip(sym.params, expr.arguments):
                arg_type = self.visit_expression(arg_expr)
                if arg_type != param_type:
                    self.error(f"Argumento '{param_name}' da função '{expr.name}' espera {param_type}, recebeu {arg_type}", expr.line)
            return sym.type

        else:
            self.error(f"Tipo de nó de expressão desconhecido: {type(expr)}", expr.line)
            return "error"

    def visit(self, node):
        # dispatcher simples
        if isinstance(node, Program):
            self.visit_program(node)
        elif isinstance(node, Block):
            self.visit_block(node)
        elif isinstance(node, VarDecl):
            self.visit_var_decl(node)
        elif isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, PrintStmt):
            self.visit_print_stmt(node)
        elif isinstance(node, IfStmt):
            self.visit_if_stmt(node)
        elif isinstance(node, WhileStmt):
            self.visit_while_stmt(node)
        elif isinstance(node, ReturnStmt):
            self.visit_return_stmt(node)
        elif isinstance(node, FunctionDecl):
            self.visit_function_decl(node)
        else:
            self.error(f"Nó AST desconhecido: {type(node)}")

