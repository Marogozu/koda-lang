from src import Lexer, Parser
from src.semanticAnalyzer import SemanticAnalyzer

# este archivo es un orquestrador mas simple que toda la interfaz de flask
# sirve para probar parte por parte todos las fases de compilacion

print("Koda compiler: Loading file \"main.kd\" \n\n")

src = ""


try:
    with open("main.kd") as f:
        src = f.read()

except:
    #cualquier error
    print("Ocurrio un error al tratar de leer el archivo fuente")
    print("se usara el src: 'int x = 10;'\n\n")
    src = "int x = 10;"

#a partir de aqui en teoria ya deberiamos tener el archivo en la variable src

tokens = Lexer(src=src)
ast = Parser(tokens).parse()
analyzer = SemanticAnalyzer()
ast.accept(analyzer)