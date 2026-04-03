from src.models.token import TokenType, Token
from src.models.nodes import (
    BlockStmt, IfStmt, ProgramNode, VarDecl, Assign, PrintStmt,
    Identifier, NumberLiteral, StringLiteral, BoolLiteral,
    UnaryOp, BinaryOp, WhileStmt,
    DoWhileStmt, ForStmt, ReturnStmt, BreakStmt, PassStmt,
    InputExpr, FuncDecl
)

PRECEDENCE = {
    # Op aritmeticos
    TokenType.PLUS: 10,
    TokenType.MINUS: 10,
    TokenType.MULT: 20,
    TokenType.DIV: 20,
    # Op relacionales
    TokenType.EQUALS: 4,
    TokenType.LT: 5,
    TokenType.GT: 5,
    TokenType.LTE: 5,
    TokenType.GTE: 5
}

UNARY_OPS = {TokenType.MINUS}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        
        # Mapear TokenType a metodos de parsing
        self._stmt_handlers = {
            TokenType.LBRACE:    self._parse_block,
            TokenType.IF:        self._parse_if,
            TokenType.WHILE:     self._parse_while,
            TokenType.DO:        self._parse_do_while,
            TokenType.FOR:       self._parse_for,
            TokenType.STDOUT:    self._parse_print,
            TokenType.RETURN:    self._parse_return,
            TokenType.BREAK:     self._parse_break,
            TokenType.PASS:      self._parse_pass,
            TokenType.FUNC_DECL: self._parse_func_decl,
            TokenType.ENTRY_P1:  self._parse_func_decl,
            TokenType.ENTRY_P2:  self._parse_func_decl,
        }

    # --- NAVEGACION ---
    def peek(self, offset=0) -> Token:
        i = self.pos + offset
        if i >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[i]

    def advance(self) -> Token:
        tok = self.peek()
        self.pos += 1
        return tok

    def eat(self, expected_type: TokenType) -> Token:
        tok = self.peek()
        if tok.type == expected_type:
            return self.advance()
        raise SyntaxError(
            f"[PARSER] Error en línea {tok.line}, col {tok.column}: "
            f"Se esperaba {expected_type.name} pero llegó {tok.type.name} ({tok.value!r})"
        )

    def at(self, t: TokenType) -> bool:
        return self.peek().type == t

    # --- ENTRADA (programa completo) ---
    def parse(self) -> ProgramNode:
        program = ProgramNode()
        while not self.at(TokenType.EOF):
            program.add_node(self._parse_statement())
        return program

    # --- METODOS PRIVADOS PARA SENTENCIAS ---
    def _parse_statement(self):
        """Punto de entrada para analizar una sentencia."""
        tok = self.peek()
        t = tok.type

        # Sentencias simples manejadas por un diccionario que mapea todo
        handler = self._stmt_handlers.get(t)
        if handler:
            return handler()

        # Declaraciones de variables (tipos)
        if t in (TokenType.BOOL, TokenType.INT, TokenType.FLOAT,
                 TokenType.DOUBLE, TokenType.STRING, TokenType.CHAR,
                 TokenType.COLLECTION, TokenType.EMPTY):
            return self._parse_var_decl()

        # Asignaciones (ID seguido de ASSIGN)
        if t == TokenType.ID and self.peek(1).type == TokenType.ASSIGN:
            return self._parse_assign()

        # Si nada coincide, error
        raise SyntaxError(
            f"[PARSER] Statement invalido en l:{tok.line}, c:{tok.column}: {tok.type.name}"
        )

    def _parse_block(self) -> BlockStmt:
        lbrace = self.eat(TokenType.LBRACE)
        stmts = []
        while not self.at(TokenType.RBRACE):
            if self.at(TokenType.EOF):
                tok = self.peek()
                raise SyntaxError(f"[PARSER] Bloque sin '}}' en l:{tok.line}, c:{tok.column}")
            stmts.append(self._parse_statement())

        self.eat(TokenType.RBRACE)
        return BlockStmt(stmts, lbrace.line, lbrace.column)

    def _parse_if(self) -> IfStmt:
        iftok = self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        cond = self._parse_expression()
        self.eat(TokenType.RPAREN)

        # Should we still call this as a "then" branch?
        then_branch = self._parse_statement()

        else_branch = None
        if self.at(TokenType.ELSE):
            self.eat(TokenType.ELSE)
            else_branch = self._parse_statement()

        return IfStmt(cond, then_branch, else_branch, iftok.line, iftok.column)

    def _parse_while(self) -> WhileStmt:
        w = self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        cond = self._parse_expression()
        self.eat(TokenType.RPAREN)
        body = self._parse_statement()
        return WhileStmt(cond, body, w.line, w.column)

    def _parse_print(self) -> PrintStmt:
        p = self.advance()   # consume STDOUT (print / out / echo / system)
        self.eat(TokenType.LPAREN)
        expr = self._parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return PrintStmt(expr, p.line, p.column)

    def _parse_do_while(self) -> DoWhileStmt:
        do_tok = self.eat(TokenType.DO)
        body = self._parse_statement()
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        cond = self._parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return DoWhileStmt(body, cond, do_tok.line, do_tok.column)

    def _parse_for(self) -> ForStmt:
        """for (init; condition; update) body
        
        - init:   VarDecl o Assign o nada  (hasta primer ';')
        - cond:   Expression o nada        (hasta segundo ';')
        - update: Assign o nada            (hasta ')')
        """
        f = self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)

        # --- init ---
        init = None
        t = self.peek().type
        if t in (TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                 TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                 TokenType.COLLECTION, TokenType.EMPTY):
            init = self._parse_var_decl()          # ya consume el ';'
        elif t == TokenType.ID and self.peek(1).type == TokenType.ASSIGN:
            init = self._parse_assign()            # ya consume el ';'
        else:
            self.eat(TokenType.SEMICOLON)          # ';' vacío

        # --- condition ---
        cond = None
        if not self.at(TokenType.SEMICOLON):
            cond = self._parse_expression()
        self.eat(TokenType.SEMICOLON)

        # --- update ---
        update = None
        if not self.at(TokenType.RPAREN):
            # Reutilizamos la lógica de assign pero sin consumir ';' (no hay ';' aquí)
            idtok = self.eat(TokenType.ID)
            self.eat(TokenType.ASSIGN)
            expr = self._parse_expression()
            # Creamos el nodo Assign manualmente (sin el ';' final)
            update = Assign(idtok.value, expr, idtok.line, idtok.column)

        self.eat(TokenType.RPAREN)
        body = self._parse_statement()
        return ForStmt(init, cond, update, body, f.line, f.column)

    def _parse_return(self) -> ReturnStmt:
        r = self.eat(TokenType.RETURN)
        expr = None
        if not self.at(TokenType.SEMICOLON):
            expr = self._parse_expression()
        self.eat(TokenType.SEMICOLON)
        return ReturnStmt(expr, r.line, r.column)

    def _parse_break(self) -> BreakStmt:
        b = self.eat(TokenType.BREAK)
        self.eat(TokenType.SEMICOLON)
        return BreakStmt(b.line, b.column)

    def _parse_pass(self) -> PassStmt:
        p = self.eat(TokenType.PASS)
        self.eat(TokenType.SEMICOLON)
        return PassStmt(p.line, p.column)

    def _parse_func_decl(self) -> FuncDecl:
        """function/def/main/head nombre(params) { body }
        
        Para ENTRY_P1 (main) y ENTRY_P2 (head) el nombre es opcional:
        se usa el propio keyword como nombre si no hay ID a continuación.
        """
        kw = self.advance()   # consume FUNC_DECL / ENTRY_P1 / ENTRY_P2

        # Nombre de la funcion
        if self.at(TokenType.ID):
            name = self.eat(TokenType.ID).value
        else:
            # main / head sin nombre extra: el keyword es el nombre
            name = kw.value

        self.eat(TokenType.LPAREN)
        params = self._parse_param_list()
        self.eat(TokenType.RPAREN)
        body = self._parse_block()
        return FuncDecl(name, params, body, kw.line, kw.column)

    def _parse_param_list(self) -> list:
        """Lista de parámetros: (tipo nombre, tipo nombre, ...) sin inicializador."""
        params = []
        while not self.at(TokenType.RPAREN):
            if self.at(TokenType.EOF):
                tok = self.peek()
                raise SyntaxError(
                    f"[PARSER] Lista de parámetros sin ')' en l:{tok.line}, c:{tok.column}"
                )
            type_tok = self.advance()
            name_tok = self.eat(TokenType.ID)
            params.append(VarDecl(type_tok.type, name_tok.value, None,
                                  type_tok.line, type_tok.column))
            # Consumir coma separadora si la hay (COMMA aún no implementado, pero dejamos el hook)
            # if self.at(TokenType.COMMA): self.advance()
        return params

    def _parse_var_decl(self) -> VarDecl:
        type_tok = self.advance()
        name_tok = self.eat(TokenType.ID)
        init = None
        if self.at(TokenType.ASSIGN):
            self.eat(TokenType.ASSIGN)
            init = self._parse_expression()

        self.eat(TokenType.SEMICOLON)
        return VarDecl(type_tok.type, name_tok.value, init, type_tok.line, type_tok.column)

    def _parse_assign(self) -> Assign:
        idtok = self.eat(TokenType.ID)
        self.eat(TokenType.ASSIGN)
        expr = self._parse_expression()
        self.eat(TokenType.SEMICOLON)
        return Assign(idtok.value, expr, idtok.line, idtok.column)

    # --- EXPRESIONES ---
    def _parse_expression(self, min_prec: int = 0):
        left = self._parse_unary()
        while self.peek().type in PRECEDENCE:
            op = self.peek()
            prec = PRECEDENCE[op.type]
            if prec < min_prec:
                break
            self.advance()
            right = self._parse_expression(prec + 1)
            left = BinaryOp(op.type, left, right, op.line, op.column)
        return left

    def _parse_unary(self):
        tok = self.peek()
        if tok.type in UNARY_OPS:
            op = self.advance()
            expr = self._parse_unary()
            return UnaryOp(op.type, expr, op.line, op.column)

        return self._parse_primary()

    def _parse_primary(self):
        tok = self.peek()
        if tok.type == TokenType.NUMBER:
            num_tok = self.advance()
            txt = num_tok.value
            val = float(txt) if "." in txt else int(txt)
            return NumberLiteral(val, num_tok.line, num_tok.column)
            
        if tok.type == TokenType.TRUE or tok.type == TokenType.FALSE:
            s = self.advance()
            return BoolLiteral(s.value, s.line, s.column)

        if tok.type == TokenType.STDIN:
            s = self.advance()
            return InputExpr(s.line, s.column)

        if tok.type == TokenType.STRING_LITERAL:
            s = self.advance()
            return StringLiteral(s.value, s.line, s.column)

        if tok.type == TokenType.ID:
            i = self.advance()
            return Identifier(i.value, i.line, i.column)

        if tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self._parse_expression()
            self.eat(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"[PARSER] Expresión inválida en l:{tok.line}, c:{tok.column}: {tok.type.name}")