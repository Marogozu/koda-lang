from src.models.nodes import (
    ProgramNode, VarDecl, Assign, PrintStmt, BlockStmt,
    IfStmt, WhileStmt, DoWhileStmt, ForStmt,
    ReturnStmt, BreakStmt, PassStmt, EndStmt,
    InputExpr, FuncDecl,
    NumberLiteral, StringLiteral, BoolLiteral,
    Identifier, UnaryOp, BinaryOp
)
from src.models.token import TokenType


# Mapeo de TokenType de operador a su simbolo Python
_OP_SYMBOLS = {
    TokenType.PLUS:   "+",
    TokenType.MINUS:  "-",
    TokenType.MULT:   "*",
    TokenType.DIV:    "/",
    TokenType.EQUALS: "==",
    TokenType.LT:     "<",
    TokenType.GT:     ">",
    TokenType.LTE:    "<=",
    TokenType.GTE:    ">=",
}

# Tipos de Koda que en Python se leen con input() y necesitan cast
_TYPE_CAST = {
    TokenType.INT:    "int",
    TokenType.FLOAT:  "float",
    TokenType.DOUBLE: "float",
    TokenType.BOOL:   "bool",
    # STRING y CHAR no necesitan cast, input() ya devuelve str
}
from src.models.nodes import (
    ProgramNode, VarDecl, Assign, PrintStmt, BlockStmt,
    IfStmt, WhileStmt, DoWhileStmt, ForStmt,
    ReturnStmt, BreakStmt, PassStmt, EndStmt,
    InputExpr, FuncDecl,
    NumberLiteral, StringLiteral, BoolLiteral,
    Identifier, UnaryOp, BinaryOp
)
from src.models.token import TokenType


# Mapeo de TokenType de operador a su simbolo Python
_OP_SYMBOLS = {
    TokenType.PLUS:   "+",
    TokenType.MINUS:  "-",
    TokenType.MULT:   "*",
    TokenType.DIV:    "/",
    TokenType.EQUALS: "==",
    TokenType.LT:     "<",
    TokenType.GT:     ">",
    TokenType.LTE:    "<=",
    TokenType.GTE:    ">=",
}

# Tipos de Koda que en Python se leen con input() y necesitan cast
_TYPE_CAST = {
    TokenType.INT:    "int",
    TokenType.FLOAT:  "float",
    TokenType.DOUBLE: "float",
    TokenType.BOOL:   "bool",
    # STRING y CHAR no necesitan cast, input() ya devuelve str
}


class CodeGenerator:
    """
    Recorre el AST y emite codigo Python equivalente.

    Uso:
        gen  = CodeGenerator()
        code = gen.generate(ast)   # devuelve el string con el codigo Python
    """

    def __init__(self):
        self._indent = 0          # nivel de indentacion actual
        self._lines: list[str] = []  # lineas acumuladas

    # ------------------------------------------------------------------ #
    #  Punto de entrada                                                    #
    # ------------------------------------------------------------------ #

    def generate(self, node: ProgramNode) -> str:
        """Genera el codigo Python completo a partir del AST."""
        self._indent = 0
        self._lines = []
        self._gen_program(node)
        return "\n".join(self._lines)

    # ------------------------------------------------------------------ #
    #  Helpers de escritura                                                #
    # ------------------------------------------------------------------ #

    def _emit(self, line: str = ""):
        """Agrega una linea con la indentacion actual."""
        self._lines.append("    " * self._indent + line)

    def _emit_raw(self, line: str = ""):
        """Agrega una linea sin indentacion (para separadores, etc.)."""
        self._lines.append(line)

    # ------------------------------------------------------------------ #
    #  Dispatch de nodos                                                   #
    # ------------------------------------------------------------------ #

    def _gen_stmt(self, node) -> None:
        """Despacha la generacion de cualquier sentencia."""
        dispatch = {
            ProgramNode:   self._gen_program,
            VarDecl:       self._gen_var_decl,
            Assign:        self._gen_assign,
            PrintStmt:     self._gen_print,
            BlockStmt:     self._gen_block,
            IfStmt:        self._gen_if,
            WhileStmt:     self._gen_while,
            DoWhileStmt:   self._gen_do_while,
            ForStmt:       self._gen_for,
            ReturnStmt:    self._gen_return,
            BreakStmt:     self._gen_break,
            PassStmt:      self._gen_pass,
            EndStmt:       self._gen_end,
            FuncDecl:      self._gen_func_decl,
        }
        handler = dispatch.get(type(node))
        if handler is None:
            raise NotImplementedError(
                f"[CODEGEN] Nodo no soportado: {type(node).__name__} "
                f"(linea {getattr(node, 'line', '?')})"
            )
        handler(node)

    def _gen_expr(self, node) -> str:
        """Devuelve la representacion Python de una expresion como string."""
        dispatch = {
            NumberLiteral: self._expr_number,
            StringLiteral: self._expr_string,
            BoolLiteral:   self._expr_bool,
            Identifier:    self._expr_identifier,
            UnaryOp:       self._expr_unary,
            BinaryOp:      self._expr_binary,
            InputExpr:     self._expr_input,
        }
        handler = dispatch.get(type(node))
        if handler is None:
            raise NotImplementedError(
                f"[CODEGEN] Expresion no soportada: {type(node).__name__} "
                f"(linea {getattr(node, 'line', '?')})"
            )
        return handler(node)

    # ------------------------------------------------------------------ #
    #  Generadores de sentencias                                           #
    # ------------------------------------------------------------------ #

    def _gen_program(self, node: ProgramNode) -> None:
        for stmt in node.sentences:
            self._gen_stmt(stmt)

    def _gen_var_decl(self, node: VarDecl) -> None:
        """
        Koda:   int x = 10;       →  Python: x = 10
        Koda:   int x;            →  Python: x = None
        Koda:   string s = input; →  Python: s = input()
        """
        if node.init is not None:
            # Si el inicializador es un InputExpr, hacer el cast al tipo declarado
            if isinstance(node.init, InputExpr):
                rhs = self._expr_input_typed(node.var_type)
            else:
                rhs = self._gen_expr(node.init)
        else:
            rhs = "None"

        self._emit(f"{node.name} = {rhs}")

    def _gen_assign(self, node: Assign) -> None:
        """Koda: x = expr; → Python: x = expr"""
        # Si la expresion es input, usar input() directamente
        if isinstance(node.expr, InputExpr):
            # No conocemos el tipo aqui, pero el semantico ya lo valido
            rhs = "input()"
        else:
            rhs = self._gen_expr(node.expr)
        self._emit(f"{node.name} = {rhs}")

    def _gen_print(self, node: PrintStmt) -> None:
        """Koda: print(expr); → Python: print(expr)"""
        self._emit(f"print({self._gen_expr(node.expr)})")

    def _gen_block(self, node: BlockStmt) -> None:
        """Un bloque { } sin encabezado propio (usado dentro de if/while/etc)."""
        for stmt in node.statements:
            self._gen_stmt(stmt)

    def _gen_if(self, node: IfStmt) -> None:
        """
        Koda:
            if (cond) { ... } else { ... }
        Python:
            if cond:
                ...
            else:
                ...
        """
        self._emit(f"if {self._gen_expr(node.condition)}:")
        self._indent += 1
        self._gen_stmt(node.then_branch)
        self._indent -= 1

        if node.else_branch is not None:
            self._emit("else:")
            self._indent += 1
            self._gen_stmt(node.else_branch)
            self._indent -= 1

    def _gen_while(self, node: WhileStmt) -> None:
        """
        Koda:   while (cond) { ... }
        Python: while cond:
                    ...
        """
        self._emit(f"while {self._gen_expr(node.condition)}:")
        self._indent += 1
        self._gen_stmt(node.body)
        self._indent -= 1

    def _gen_do_while(self, node: DoWhileStmt) -> None:
        """
        Koda:   do { body } while (cond);
        Python: while True:
                    body
                    if not (cond): break
        Python no tiene do-while nativo, se emula con while True + break.
        """
        self._emit("while True:")
        self._indent += 1
        self._gen_stmt(node.body)
        self._emit(f"if not ({self._gen_expr(node.condition)}): break")
        self._indent -= 1

    def _gen_for(self, node: ForStmt) -> None:
        """
        Koda:   for (int i = 0; i < 10; i = i + 1) { body }
        Python: i = 0
                while i < 10:
                    body
                    i = i + 1

        Python no tiene un for C-style nativo, se emula con while.
        """
        # init (fuera del while)
        if node.init is not None:
            self._gen_stmt(node.init)

        # condicion del while (si no hay condicion, bucle infinito)
        cond = self._gen_expr(node.condition) if node.condition is not None else "True"
        self._emit(f"while {cond}:")
        self._indent += 1

        # body
        self._gen_stmt(node.body)

        # update (al final del cuerpo)
        if node.update is not None:
            self._gen_stmt(node.update)

        self._indent -= 1

    def _gen_return(self, node: ReturnStmt) -> None:
        """Koda: return expr; → Python: return expr"""
        if node.expr is not None:
            self._emit(f"return {self._gen_expr(node.expr)}")
        else:
            self._emit("return")

    def _gen_break(self, node: BreakStmt) -> None:
        self._emit("break")

    def _gen_pass(self, node: PassStmt) -> None:
        self._emit("pass")

    def _gen_end(self, node: EndStmt) -> None:
        # end sin valor de retorno → return sin valor
        self._emit("return")

    def _gen_func_decl(self, node: FuncDecl) -> None:
        """
        Koda:   function suma(int a, int b) { return a + b; }
        Python: def suma(a, b):
                    return a + b

        Para main/head se emite ademas la llamada automatica al final.
        """
        params_str = ", ".join(p.name for p in node.params)
        self._emit(f"def {node.name}({params_str}):")
        self._indent += 1

        if node.body.statements:
            self._gen_block(node.body)
        else:
            self._emit("pass")  # cuerpo vacio requiere pass en Python

        self._indent -= 1
        self._emit_raw("")  # linea en blanco tras la funcion

        # main y head son puntos de entrada — se invocan automaticamente
        if node.name in ("main", "head"):
            self._emit(f"{node.name}()")
            self._emit_raw("")

    # ------------------------------------------------------------------ #
    #  Generadores de expresiones                                          #
    # ------------------------------------------------------------------ #

    def _expr_number(self, node: NumberLiteral) -> str:
        return repr(node.value)

    def _expr_string(self, node: StringLiteral) -> str:
        # repr() agrega las comillas y escapa caracteres especiales
        return repr(node.value)

    def _expr_bool(self, node: BoolLiteral) -> str:
        # Koda usa "true"/"false" en minuscula, Python usa "True"/"False"
        return "True" if str(node.value).lower() == "true" else "False"

    def _expr_identifier(self, node: Identifier) -> str:
        return node.name

    def _expr_unary(self, node: UnaryOp) -> str:
        op = _OP_SYMBOLS.get(node.op, str(node.op))
        return f"{op}{self._gen_expr(node.expr)}"

    def _expr_binary(self, node: BinaryOp) -> str:
        op = _OP_SYMBOLS.get(node.op, str(node.op))
        left  = self._gen_expr(node.left)
        right = self._gen_expr(node.right)
        return f"({left} {op} {right})"

    def _expr_input(self, node: InputExpr) -> str:
        """input sin tipo declarado → input() puro (devuelve str)."""
        return "input()"

    def _expr_input_typed(self, var_type: TokenType) -> str:
        """
        Genera input() con el cast correcto segun el tipo Koda.
        Koda: int x = input;  →  Python: x = int(input())
        """
        cast = _TYPE_CAST.get(var_type)
        if cast:
            return f"{cast}(input())"
        return "input()"