from src.models.nodes import (
    BlockStmt, BoolLiteral, IfStmt, ProgramNode, VarDecl, Assign, PrintStmt,
    Identifier, NumberLiteral, StringLiteral,
    UnaryOp, BinaryOp, WhileStmt
)
from src.models.token import TokenType
from src.symbolTable import ScopeStack


class SemanticAnalyzer:
    """Analizador semantico que recorre el AST y verifica reglas de alcance y tipos."""

    def __init__(self):
        # Pila de ambitos (cada ambito es una tabla de simbolos propia)
        self.scope_stack = ScopeStack()

    def analyze(self, node: ProgramNode) -> str:
        """Punto de entrada: inicia el analisis desde el nodo raiz."""
        node.analyze(self, self.scope_stack)
        return "--- Analisis semantico finalizado con exito ---"

    # --- Metodos para cada tipo de nodo ---

    def analyze_program(self, node: ProgramNode, scope_stack: ScopeStack) -> None:
        """Analiza una lista de sentencias."""
        for stmt in node.sentences:
            stmt.analyze(self, scope_stack)

    def analyze_number_literal(self, node: NumberLiteral, scope_stack: ScopeStack) -> TokenType:
        """Retorna el tipo del numero: INT si es entero, FLOAT si tiene punto decimal."""
        if isinstance(node.value, float):
            return TokenType.FLOAT
        return TokenType.INT

    def analyze_string_literal(self, node: StringLiteral, scope_stack: ScopeStack) -> TokenType:
        return TokenType.STRING

    def analyze_bool_literal(self, node: BoolLiteral, scope_stack: ScopeStack) -> TokenType:
        return TokenType.BOOL

    def analyze_identifier(self, node: Identifier, scope_stack: ScopeStack) -> TokenType:
        """Busca el identificador en la pila de ambitos."""
        tipo = scope_stack.lookup(node.name)
        if tipo is None:
            raise Exception(f"Error: Variable '{node.name}' no definida (linea {node.line})")
        return tipo

    def analyze_unary_op(self, node: UnaryOp, scope_stack: ScopeStack) -> TokenType:
        """Verifica operadores unarios (por ahora solo '-' )."""
        expr_type = node.expr.analyze(self, scope_stack)
        
        if node.op == TokenType.MINUS:
            
            if expr_type in (TokenType.INT, TokenType.FLOAT):
                return expr_type
            raise Exception(f"Error de tipo: Operador '-' no aplicable a {expr_type} (linea {node.line})")
            
        raise Exception(f"Error: Operador unario {node.op} no soportado (linea {node.line})")

    def analyze_binary_op(self, node: BinaryOp, scope_stack: ScopeStack) -> TokenType:
        """Verifica operadores binarios usando una tabla de reglas."""
        left_type = node.left.analyze(self, scope_stack)
        right_type = node.right.analyze(self, scope_stack)

        rule = self._get_binary_rule(node.op)
        if rule is None:
            raise Exception(f"Error: Operador binario {node.op} no soportado (linea {node.line})")

        return rule(left_type, right_type, node.line)

    def analyze_var_decl(self, node: VarDecl, scope_stack: ScopeStack) -> None:
        """Procesa una declaracion de variable."""
        # 1. Verificar si la variable ya fue declarada en el ambito actual
        if scope_stack.exists_in_current_scope(node.name):
            raise Exception(f"Error semantico: La variable '{node.name}' ya existe en este ambito (linea {node.line})")

        # 2. Si tiene valor inicial, verificar que el tipo coincida
        if node.init:
            actual_type = node.init.analyze(self, scope_stack)
            if actual_type != node.var_type:
                raise Exception(
                    f"Error de tipo: No puedes asignar {actual_type} a {node.var_type} "
                    f"para la variable '{node.name}' (linea {node.line})"
                )

        # 3. Guardar en la tabla de simbolos del ambito actual
        scope_stack.define(node.name, node.var_type)

    def analyze_assign(self, node: Assign, scope_stack: ScopeStack) -> None:
        """Procesa una asignacion."""
        # 1. Verificar que la variable exista
        var_type = scope_stack.lookup(node.name)
        if var_type is None:
            raise Exception(f"Error: Variable '{node.name}' no declarada (linea {node.line})")

        # 2. Verificar que el tipo de la expresion coincida con el de la variable
        expr_type = node.expr.analyze(self, scope_stack)
        if expr_type != var_type:
            raise Exception(
                f"Error de tipo: No puedes asignar {expr_type} a la variable '{node.name}' "
                f"que es de tipo {var_type} (linea {node.line})"
            )

    def analyze_print_stmt(self, node: PrintStmt, scope_stack: ScopeStack) -> None:
        """Verifica que la expresion a imprimir sea valida (no importa el tipo)."""
        node.expr.analyze(self, scope_stack)

    def analyze_block_stmt(self, node: BlockStmt, scope_stack: ScopeStack) -> None:
        """Crea un nuevo ambito y analiza las sentencias del bloque."""
        scope_stack.push_scope()
        for stmt in node.statements:
            stmt.analyze(self, scope_stack)
            
        scope_stack.pop_scope()

    def analyze_if_stmt(self, node: IfStmt, scope_stack: ScopeStack) -> None:
        """Analiza la condicion (debe ser bool) y las ramas."""
        # 1. Analizar la condicion
        cond_type = node.condition.analyze(self, scope_stack)
        if cond_type != TokenType.BOOL:
            raise Exception(
                f"Error semantico: La condicion del 'if' debe ser BOOL, "
                f"pero se encontro {cond_type.name} (linea {node.line})"
            )

        # 2. Analizar la rama then
        node.then_branch.analyze(self, scope_stack)
        ## Deberia existir siquiera una then? creo no

        # 3. Analizar la rama else (si existe)
        if node.else_branch:
            node.else_branch.analyze(self, scope_stack)

    def analyze_while_stmt(self, node: WhileStmt, scope_stack: ScopeStack) -> None:
        """Analiza la condicion (debe ser bool) y el cuerpo."""
        cond_type = node.condition.analyze(self, scope_stack)
        if cond_type != TokenType.BOOL:
            raise Exception(
                f"Error semantico: La condicion del 'while' debe ser BOOL, "
                f"pero se encontro {cond_type.name} (linea {node.line})"
            )
            
        node.body.analyze(self, scope_stack)

    # --- Tabla de reglas para operadores binarios ---

    def _get_binary_rule(self, op: TokenType):
        """Retorna la funcion que implementa la regla de tipos para el operador dado."""
        rules = {
            TokenType.PLUS: self._check_arithmetic,
            TokenType.MINUS: self._check_arithmetic,
            TokenType.MULT: self._check_arithmetic,
            TokenType.DIV: self._check_arithmetic,
            #comparaciones
            TokenType.LT: self._check_comparison,
            TokenType.GT: self._check_comparison,
            TokenType.LTE: self._check_comparison,
            TokenType.GTE: self._check_comparison,
        }
        return rules.get(op)
    
    def _check_comparison(self, left: TokenType, right: TokenType, line: int) -> TokenType:
        """Verifica que se comparen numeros y devuelve siempre BOOL."""
        if left in (TokenType.INT, TokenType.FLOAT) and right in (TokenType.INT, TokenType.FLOAT):
            return TokenType.BOOL # El resultado de 5 > 3 siempre es un booleano
        
        raise Exception(
            f"Error de tipos: No se puede comparar {left.name} con {right.name} (linea {line})"
        )

    def _check_arithmetic(self, left: TokenType, right: TokenType, line: int) -> TokenType:
        """Regla para operaciones aritmeticas: promocion a FLOAT si algún operando es FLOAT."""
        if left in (TokenType.INT, TokenType.FLOAT) and right in (TokenType.INT, TokenType.FLOAT):
            if left == TokenType.FLOAT or right == TokenType.FLOAT:
                return TokenType.FLOAT
            return TokenType.INT
        raise Exception(
            f"Error de tipos: Operacion aritmetica entre {left} y {right} no valida (linea {line})"
        )