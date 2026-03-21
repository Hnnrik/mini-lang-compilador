class CodeGenerator:
    def __init__(self):
        self.code = []
        self.indent_level = 0

    def emit(self, line):
        indent = "    " * self.indent_level
        self.code.append(indent + line)

    def generate(self, node):
        self.visit(node)
        return "\n".join(self.code)

    def visit(self, node):
        if node is None:
            return

        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise Exception(f"Nó não suportado: {type(node)}")

    # =========================

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Block(self, node):
        self.indent_level += 1
        for stmt in node.statements:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_VarDecl(self, node):
        expr = self.visit_expression(node.expression)
        self.emit(f"{node.name} = {expr}")

    def visit_Assignment(self, node):
        expr = self.visit_expression(node.expression)
        self.emit(f"{node.name} = {expr}")

    def visit_PrintStmt(self, node):
        expr = self.visit_expression(node.expr)
        self.emit(f"print({expr})")

    def visit_IfStmt(self, node):
        cond = self.visit_expression(node.condition)
        self.emit(f"if {cond}:")
        self.visit(node.then_block)

        if node.else_block:
            self.emit("else:")
            self.visit(node.else_block)

    def visit_WhileStmt(self, node):
        cond = self.visit_expression(node.condition)
        self.emit(f"while {cond}:")
        self.visit(node.body)

    def visit_FunctionDecl(self, node):
        params = ", ".join(name for name, _ in node.params)
        self.emit(f"def {node.name}({params}):")
        self.visit(node.body)

    def visit_ReturnStmt(self, node):
        expr = self.visit_expression(node.expression)
        self.emit(f"return {expr}")

    def visit_expression(self, expr):
        if expr is None:
            return ""

        if expr.__class__.__name__ == "BinaryOp":
            left = self.visit_expression(expr.left)
            right = self.visit_expression(expr.right)
            return f"({left} {expr.op} {right})"

        elif expr.__class__.__name__ == "UnaryOp":
            operand = self.visit_expression(expr.operand)
            if expr.op == "not":
                return f"(not {operand})"
            return f"({expr.op}{operand})"

        elif expr.__class__.__name__ == "Literal":
            if expr.lit_type == "string":
                return f'"{expr.value}"'
            return str(expr.value)

        elif expr.__class__.__name__ == "Identifier":
            return expr.name

        elif expr.__class__.__name__ == "CallExpr":
            args = ", ".join(self.visit_expression(a) for a in expr.arguments)
            return f"{expr.name}({args})"

        else:
            raise Exception(f"Expressão não suportada: {type(expr)}")