# Importacion de future y typing 
# Future para evitar errores de referencia hacia adelante al usar tipos en anotaciones, posponiendo su evaluación.
from __future__ import annotations
# typing para usar tipos opcionales y listas en las anotaciones de tipo, mejorando la claridad del código y facilitando el análisis estático.
from typing import Optional, List



# --- NODO BASE ---
class Node:
    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
    
    # Utilidad creada para el analisis semantico, permite interactuar recursivamente
    # con los metodos dedicados a verificacion de la clase Visitor
    def accept(self, visitor):
        # Genera el nombre del metodo dinamicamente
        method_name = f"visit_{self.__class__.__name__}"
        # Se toma el metodo que genera la posibilidad de visita, sino se espera
        # que este definido un metodo .generic_visit como default call
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)
    
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
    """Fragmentos de codigo que 'valen algo'"""
    pass


class Statement(Node):
    """Instrucciones que 'hacen algo'"""
    pass




# --- RAÍZ ---
class ProgramNode(Node):
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.sentences: List[Statement] = []

    def add_node(self, node: Statement):
        self.sentences.append(node)




# --- LITERALES ---
class LiteralNode(Expression):
    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

class NumberLiteral(LiteralNode):
    pass

class StringLiteral(LiteralNode):
    pass




# --- IDENTIFICADORES ---
class Identifier(Expression):
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name




# --- OPERACIONES ---
class UnaryOp(Expression):
    def __init__(self, op, expr: Expression, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.expr = expr


class BinaryOp(Expression):
    def __init__(self, op, left: Expression, right: Expression, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.left = left
        self.right = right




# --- SENTENCIAS ---
class VarDecl(Statement):
    def __init__(self, var_type, name: str, init: Optional[Expression] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.var_type = var_type
        self.name = name
        self.init = init


class Assign(Statement):
    def __init__(self, name: str, expr: Expression,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.expr = expr


class PrintStmt(Statement):
    def __init__(self, expr: Expression,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr


class BlockStmt(Statement):
    def __init__(self, statements: Optional[List[Statement]] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements if statements is not None else []


class IfStmt(Statement):
    def __init__(self, condition: Expression,
                 then_branch: Statement,
                 else_branch: Optional[Statement] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileStmt(Statement):
    def __init__(self, condition: Expression,
                 body: Statement,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body