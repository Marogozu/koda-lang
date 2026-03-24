class SymbolTable:
    def __init__(self):
        self.symbols = {} # Nombre -> Tipo

    def define(self, name, symbol_type):
        self.symbols[name] = symbol_type

    def lookup(self, name):
        return self.symbols.get(name)

    def exists(self, name):
        return name in self.symbols


class ScopeStack:
    def __init__(self):
        self.scopes = [SymbolTable()]  # ambito global

    def push_scope(self):
        self.scopes.append(SymbolTable())

    def pop_scope(self):
        if len(self.scopes) == 1:
            raise RuntimeError("No se puede eliminar el ambito global")
        self.scopes.pop()

    def define(self, name, symbol_type):
        # Define en el ambito actual (el iltimo)
        self.scopes[-1].define(name, symbol_type)

    def lookup(self, name):
        # Busca desde el ambito más interno al más externo
        for scope in reversed(self.scopes):
            tipo = scope.lookup(name)
            if tipo is not None:
                return tipo
        return None

    def exists_in_current_scope(self, name):
        return self.scopes[-1].exists(name)