class Splitter:
    def __init__(self, src: str) -> None:
        self.src = list(src)
        self.src_length = len(self.src)
        self.current_position = 0
        self.current_column = 1
        self.current_row = 1
    
    @property
    def current_char(self): # Func que se ejecuta el leer splitter.current_char
        if self.current_position >= self.src_length:
            return "" # Return empty string at EOF
        return self.src[self.current_position]

    def has_more(self) -> bool:
        return self.current_position < self.src_length

    def next_char(self) -> bool:
        """Mueve el puntero. Retorna False si llego al final"""
        if not self.has_more():
            return False
        
        if self.current_char == "\n":
            self.current_row += 1
            self.current_column = 0
        
        self.current_position += 1
        self.current_column += 1
        return True

    def peek_next(self):
        next_idx = self.current_position + 1
        if next_idx >= self.src_length:
            return ""
        return self.src[next_idx]