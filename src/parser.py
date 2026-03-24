from src.models.token import TokenType, Token
from src.models.nodes import (
    BlockStmt, IfStmt, ProgramNode, VarDecl, Assign, PrintStmt,
    Identifier, NumberLiteral, StringLiteral, BoolLiteral,
    UnaryOp, BinaryOp, WhileStmt
)

PRECEDENCE = {
    # Op aritmeticos
    TokenType.PLUS: 10,
    TokenType.MINUS: 10,
    TokenType.MULT: 20,
    TokenType.DIV: 20,
    # Op booleanos
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
            TokenType.LBRACE: self._parse_block,
            TokenType.IF: self._parse_if,
            TokenType.WHILE: self._parse_while,
            TokenType.PRINT: self._parse_print,
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
        if t in (TokenType.BOOL, TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE, TokenType.STRING):
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
        p = self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self._parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return PrintStmt(expr, p.line, p.column)

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