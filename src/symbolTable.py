class SymbolEntry:
    """Entrada en la tabla de simbolos. Puede representar una variable o una funcion."""
    def __init__(self, symbol_type, modifier=None, is_func=False, params=None, return_type=None):
        self.symbol_type  = symbol_type   # TokenType del tipo de dato (INT, FLOAT, etc.) o None para funciones sin retorno
        self.modifier     = modifier      # TokenType.MOD_GLOBAL | MOD_LOCAL | MOD_AUTO | None
        self.is_func      = is_func       # True si es una funcion declarada con FuncDecl
        self.params       = params or []  # Lista de (nombre, TokenType) para funciones
        self.return_type  = return_type   # Tipo de retorno de la funcion (puede ser None)

    def __repr__(self):
        if self.is_func:
            params_str = ", ".join(f"{n}:{t}" for n, t in self.params)
        return f"SymbolEntry(type={self.symbol_type}, modifier={self.modifier})"


class SymbolTable:
    def __init__(self):
        self.symbols: dict[str, SymbolEntry] = {}

    def define(self, name: str, entry: SymbolEntry):
        self.symbols[name] = entry

    def lookup(self, name: str) -> SymbolEntry | None:
        return self.symbols.get(name)

    def exists(self, name: str) -> bool:
        return name in self.symbols


class ScopeStack:
    def __init__(self):
        self.scopes: list[SymbolTable] = [SymbolTable()]  # ambito global

        # --- Flags de contexto ---
        # Cuantos niveles de bucle (while/for/do-while) estamos dentro.
        # break/pass/end son validos solo cuando _loop_depth > 0.
        self._loop_depth: int = 0

        # Nombre de la funcion activa (None = top-level).
        # return es valido solo cuando _func_name is not None.
        self._func_name: str | None = None

        # Tipo de retorno declarado de la funcion activa.
        self._func_return_type = None

    # --- Scope management ---

    def push_scope(self):
        self.scopes.append(SymbolTable())

    def pop_scope(self):
        if len(self.scopes) == 1:
            raise RuntimeError("No se puede eliminar el ambito global")
        self.scopes.pop()

    # --- Variables ---

    def define(self, name: str, symbol_type, modifier=None):
        """Define una variable en el ambito actual."""
        self.scopes[-1].define(name, SymbolEntry(symbol_type, modifier=modifier))

    def define_func(self, name: str, params: list, return_type=None):
        """Registra una funcion en el ambito actual."""
        entry = SymbolEntry(
            symbol_type=return_type,
            is_func=True,
            params=params,
            return_type=return_type
        )
        self.scopes[-1].define(name, entry)

    def lookup(self, name: str):
        """Devuelve el TokenType de la variable, buscando del scope mas interno al externo."""
        entry = self.lookup_entry(name)
        if entry is None:
            return None
        return entry.symbol_type

    def lookup_entry(self, name: str) -> SymbolEntry | None:
        """Devuelve la SymbolEntry completa (para funciones, modificadores, etc.)."""
        for scope in reversed(self.scopes):
            entry = scope.lookup(name)
            if entry is not None:
                return entry
        return None

    def exists_in_current_scope(self, name: str) -> bool:
        return self.scopes[-1].exists(name)

    # --- Contexto de bucle ---

    def enter_loop(self):
        self._loop_depth += 1

    def exit_loop(self):
        self._loop_depth = max(0, self._loop_depth - 1)

    @property
    def inside_loop(self) -> bool:
        return self._loop_depth > 0

    # --- Contexto de funcion ---

    def enter_func(self, name: str, return_type=None):
        self._func_name = name
        self._func_return_type = return_type

    def exit_func(self):
        self._func_name = None
        self._func_return_type = None

    @property
    def inside_func(self) -> bool:
        return self._func_name is not None

    @property
    def current_func_return_type(self):
        return self._func_return_type