from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    """
    Estrictamente define los tipos de token existentes
    """

    # Palabras reservadas
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FUNCTION = "function"
    PRINT = "print"
    
    # Tipos de dato
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"

    # Aritmetica
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"

    # Simbolos
    DOUBLEQOUT = "\"" #FIX TYPO its quot not qout
    ASSIGN = "="
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SEMICOLON = ";" 
    
    # Literales e identificadores
    ID = "ID"         # nombres de variables
    NUMBER = "NUMBER" # numero
    STRING_LITERAL = "STRING_LITERAL" # cadena de texto (pero no en una variable)
    EOF = "EOF"       # Fin de archivo (usado en el Parser)


    #TODO quizas añadir una optimizacion seria lo justo? un map en vez del bucle
    @classmethod
    def keyword_exists(cls, valor: str):
        """
        Busca si un string pertenece a algun token estatico.
        """
        for item in cls:
            if item.value == valor:
                return item
        return None



@dataclass # define la calse como solamente datos
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        """Esto hace que al hacer print(token) se vea mas profesional en la consola"""
        return f"t:{self.type}, v:{self.value}, row:{self.line}, col:{self.column}"