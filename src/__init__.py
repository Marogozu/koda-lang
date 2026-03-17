#este archivo se encarga de que main.py pueda importar de forma mas facil
#todos los "modulos" (archivos) para su uso, sin necesidad de que se dicte
#la ruta completa

#ejemplo sin __init__ en src: < from src.lexer import Lexer  >
#ejemplo CON __iniy__ en src: < from src import Lexer >

# Dentro de src/__init__.py
from .lexer import Lexer
from .parser import Parser
from .semanticAnalyzer import SemanticAnalyzer
from .symbolTable import SymbolTable