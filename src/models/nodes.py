# Importacion de future y typing 
# Future para evitar errores de referencia hacia adelante al usar tipos en anotaciones, posponiendo su evaluación.
from __future__ import annotations
# typing para usar tipos opcionales y listas en las anotaciones de tipo, mejorando la claridad del código y facilitando el análisis estático.
from typing import Optional, List
#from src.models.token import TokenType



# --- NODO BASE ---
class Node:
    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    def analyze(self, analyzer, scope_stack):
        """Metodo base que deben implementar las subclases."""
        raise NotImplementedError
        
    def __repr__(self, indent: int = 0) -> str:
        """Genera une representacion del nodo con identaciones y nuevas lineas para mejor lectura."""
        name = self.__class__.__name__
        ignored = {'line', 'column'}
        
        # Obtenemos los atributos y generamos su representación
        items = []
        for k, v in self.__dict__.items():
            if k in ignored:
                continue
            
            # Si el valor es otro Nodo, llamamos su repr con más indentación
            if isinstance(v, Node):
                val_str = v.__repr__(indent + 2)
            # Si es una lista (como en BlockStmt), procesamos cada elemento
            elif isinstance(v, list):
                list_items = []
                for item in v:
                    list_items.append(item.__repr__(indent + 4) if isinstance(item, Node) else repr(item))
                val_str = "[\n" + ",\n".join(list_items) + "\n" + " " * (indent + 2) + "]"
            else:
                val_str = repr(v)
                
            items.append(f"{' ' * (indent + 2)}{k}={val_str}")

        if not items:
            return f"{name}()"
            
        res = f"{name}(\n" + ",\n".join(items) + "\n" + " " * indent + ")"
        return res


class Expression(Node):
    """Las expresiones son fragmentos que valen algo literalmente. Devuelven su tipo al analizar"""
    pass


class Statement(Node):
    """Las sentencias son instrucciones que hacen algo. No devuelven tipo"""
    pass




# --- RAÍZ ---
class ProgramNode(Node):
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.sentences: List[Statement] = []

    def add_node(self, node: Statement):
        self.sentences.append(node)

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_program(self, scope_stack)



# --- LITERALES ---
class LiteralNode(Expression):
    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value


class NumberLiteral(LiteralNode):
    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_number_literal(self, scope_stack)


class StringLiteral(LiteralNode):
    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_string_literal(self, scope_stack)


class BoolLiteral(LiteralNode):
    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_bool_literal(self, scope_stack)



# --- IDENTIFICADORES ---
class Identifier(Expression):
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name

    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_identifier(self, scope_stack)



# --- OPERACIONES ---
class UnaryOp(Expression):
    def __init__(self, op, expr: Expression, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.expr = expr

    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_unary_op(self, scope_stack)


class BinaryOp(Expression):
    def __init__(self, op, left: Expression, right: Expression, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.left = left
        self.right = right

    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_binary_op(self, scope_stack)



# --- SENTENCIAS ---
class VarDecl(Statement):
    """Declaración de variable.

    modifier: TokenType.MOD_GLOBAL | MOD_LOCAL | MOD_AUTO | None
              Proviene de public/extern/static/auto que precede al tipo.
    """
    def __init__(self, var_type, name: str, init: Optional[Expression] = None,
                 line: int = 0, column: int = 0, modifier=None):
        super().__init__(line, column)
        self.modifier = modifier   # None si no hay modificador
        self.var_type = var_type
        self.name = name
        self.init = init

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_var_decl(self, scope_stack)


class Assign(Statement):
    def __init__(self, name: str, expr: Expression,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.expr = expr

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_assign(self, scope_stack)


class PrintStmt(Statement):
    def __init__(self, expr: Expression,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_print_stmt(self, scope_stack)


class BlockStmt(Statement):
    def __init__(self, statements: Optional[List[Statement]] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements if statements is not None else []

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_block_stmt(self, scope_stack)


class IfStmt(Statement):
    def __init__(self, condition: Expression,
                 then_branch: Statement,
                 else_branch: Optional[Statement] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_if_stmt(self, scope_stack)


class WhileStmt(Statement):
    def __init__(self, condition: Expression,
                 body: Statement,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_while_stmt(self, scope_stack)


class DoWhileStmt(Statement):
    """Representa: do { body } while (condition);"""
    def __init__(self, body: Statement,
                 condition: Expression,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.body = body
        self.condition = condition

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_do_while_stmt(self, scope_stack)


class ForStmt(Statement):
    """Representa: for (init; condition; update) { body }
    
    - init:      VarDecl o Assign (puede ser None)
    - condition: Expression (puede ser None => bucle infinito)
    - update:    Assign (puede ser None)
    - body:      Statement
    """
    def __init__(self, init, condition: Optional[Expression],
                 update, body: Statement,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_for_stmt(self, scope_stack)


class ReturnStmt(Statement):
    """Representa: return expr; o return;"""
    def __init__(self, expr: Optional[Expression] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_return_stmt(self, scope_stack)


class BreakStmt(Statement):
    """Representa: break;"""
    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_break_stmt(self, scope_stack)


class PassStmt(Statement):
    """Representa: pass;"""
    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_pass_stmt(self, scope_stack)


class EndStmt(Statement):
    """Representa: end;  — salida/cierre de bloque sin valor de retorno."""
    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_end_stmt(self, scope_stack)


class InputExpr(Expression):
    """Representa: input  (lectura de stdin, usada como expresion en asignaciones)"""
    def analyze(self, analyzer, scope_stack):
        return analyzer.analyze_input_expr(self, scope_stack)


class FuncDecl(Statement):
    """Representa: function/def nombre(params) { body }
    
    - name:   str
    - params: lista de VarDecl (sin inicializador, solo tipo y nombre)
    - body:   BlockStmt
    """
    def __init__(self, name: str, params: List['VarDecl'],
                 body: 'BlockStmt',
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body

    def analyze(self, analyzer, scope_stack):
        analyzer.analyze_func_decl(self, scope_stack)