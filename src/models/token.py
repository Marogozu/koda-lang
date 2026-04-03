from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    """
    Estrictamente define los tipos de token existentes
    """

    # PR_CONTROL (Flujo)
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    FOR = "for"
    BREAK = "break"
    RETURN = "return"
    PASS = "pass"
    END = "end"

    # PR_IO (Entrada/Salida)
    STDOUT = "print"        # print es el valor canonico; out/echo/system son aliases
    STDIN = "input"
    FILE_OPEN = "open"
    FILE_READ = "read"
    FILE_HANDLE = "file"

    # PR_DEF (Estructura)
    FUNC_DECL = "function"  # function es el valor canonico; def es alias
    ENTRY_P1 = "main"
    ENTRY_P2 = "head"
    NEW_FUNC = "new"

    # PR_DATA_TYPE (Tipos)
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BOOL = "bool"
    CHAR = "char"
    COLLECTION = "list"     # list es el valor canonico; array es alias
    EMPTY = "null"          # null es el valor canonico; void es alias

    # PR_VAR_MOD (Modificadores)
    MOD_GLOBAL = "public"   # public es el valor canonico; extern es alias
    MOD_LOCAL = "static"
    MOD_AUTO = "auto"

    # PR_ARIT (Aritmetica)
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"

    # PR_REL (Relacionales)
    EQUALS = "=="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="

    # Simbolos y delimitadores
    DOUBLEQUOT = "\""
    ASSIGN = "="
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SEMICOLON = ";"

    # Literales e identificadores
    ID = "ID"
    NUMBER = "NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    TRUE = "true"
    FALSE = "false"
    EOF = "EOF"


    #TODO quizas añadir una optimizacion seria lo justo? un map en vez del bucle
    @classmethod
    def keyword_exists(cls, valor: str):
        """
        Busca si un string pertenece a algun token canonico.
        Para aliases (where->IF, def->FUNC_DECL, etc.) usar KEYWORD_ALIASES primero.
        """
        for item in cls:
            if item.value == valor:
                return item
        return None


# Aliases: palabras que lexicamente son distintas pero mapean al mismo TokenType.
# El lexer debe consultar este dict ANTES de llamar a keyword_exists.
# Formato: { "alias_literal": TokenType }
KEYWORD_ALIASES: dict = {
    # PR_CONTROL
    "where":  TokenType.IF,
    # PR_IO
    "out":    TokenType.STDOUT,
    "echo":   TokenType.STDOUT,
    "system": TokenType.STDOUT,
    # PR_DEF
    "def":    TokenType.FUNC_DECL,
    # PR_DATA_TYPE
    "array":  TokenType.COLLECTION,
    "void":   TokenType.EMPTY,
    # PR_VAR_MOD
    "extern": TokenType.MOD_GLOBAL,
}



@dataclass # define la calse como solamente datos
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        """Esto hace que al hacer print(token) se vea mas profesional en la consola"""
        return f"t:{self.type}, v:{self.value}, row:{self.line}, col:{self.column}"