class SymbolTable:
    def __init__(self):
        self.symbols = {} # Nombre -> Tipo

    def define(self, name, symbol_type):
        self.symbols[name] = symbol_type

    def lookup(self, name):
        return self.symbols.get(name)

    def exists(self, name):
        return name in self.symbols