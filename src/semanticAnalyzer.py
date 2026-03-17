from src.models.nodes import (
    BlockStmt, IfStmt, ProgramNode, VarDecl, Assign, PrintStmt,
    Identifier, NumberLiteral, StringLiteral,
    UnaryOp, BinaryOp, WhileStmt
)
from src.symbolTable import SymbolTable
from src.models.token import TokenType

class Visitor:
    """Clase base para que todos los analizadores sigan la misma estructura."""
    def generic_visit(self, node):
        raise Exception(f"No se definio visit_{type(node).__name__}")


class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.table = SymbolTable()

    def visit_ProgramNode(self, node):
        for sentence in node.sentences:
            sentence.accept(self)
        print("--- Analisis semantico finalizado con exito ---")

    def visit_VarDecl(self, node):
        # 1. Verificar si la variable ya fue declarada
        if self.table.exists(node.name):
            raise Exception(f"Error Semantico: La variable '{node.name}' ya existe.")

        # 2. Si tiene un valor inicial, verificar que el tipo coincida
        if node.init:
            # RECURSION: Obtenemos el tipo del valor que se le quiere asignar
            actual_type = node.init.accept(self) 
            
            if actual_type != node.var_type:
                raise Exception(f"Error de Tipo: No puedes asignar {actual_type} a {node.var_type} ('{node.name}')")

        # 3. Guardar en la tabla de símbolos
        self.table.define(node.name, node.var_type)

    def visit_Assign(self, node):
        # 1. Verificar si la variable existe
        var_type = self.table.lookup(node.name)
        if not var_type:
            raise Exception(f"Error: La variable '{node.name}' no ha sido declarada.")

        # 2. Verificar que el nuevo valor sea del tipo correcto
        new_value_type = node.expr.accept(self)
        if new_value_type != var_type:
            raise Exception(f"Error: No puedes asignar {new_value_type} a la variable '{node.name}' que es {var_type}")

    def visit_NumberLiteral(self, node):
        # Aquí es donde vinculamos el valor real con el Enum
        if isinstance(node.value, float):
            return TokenType.FLOAT
        return TokenType.INT

    def visit_StringLiteral(self, node):
        return TokenType.STRING

    def visit_Identifier(self, node):
        # Si usamos una variable en una expresión, devolvemos su tipo guardado
        tipo = self.table.lookup(node.name)
        if not tipo:
            raise Exception(f"Error: Uso de variable no definida '{node.name}'")
        return tipo