from src.models.token import TokenType, Token, KEYWORD_ALIASES
from src.tools.splitter import Splitter


def buildToken(row:int, col:int, value:list[str], type:TokenType = TokenType.ID) -> Token :
    """
    Builds a standarized token.
    Lookup order:
      1. KEYWORD_ALIASES  — aliases como where, def, out, echo, array, void, extern
      2. keyword_exists   — keywords canonicos como if, while, int, print ...
      3. type param       — tipo pasado externamente (default ID)
    """

    joined_token_chars = "".join(value)

    # 1. Aliases tienen prioridad sobre keywords canonicos
    alias_type = KEYWORD_ALIASES.get(joined_token_chars)
    if alias_type:
        return Token(alias_type, joined_token_chars, row, col)

    # 2. Keyword canonico
    canonical = TokenType.keyword_exists(joined_token_chars)
    if canonical:
        type = canonical

    return Token(type, joined_token_chars, row, col)

# EJEMPLOS USANDO NUESTRO ALFABETO

#src = """
#int x = 10*2+1;
#print(\"something\");
#print(x);
#if((2*2)=4){
#    print("ejemplo largoooote")
#}
#"""

#ejemplo super simple
#src = "int x =10+2" #notese como llegan a faltar espacios


#ejemplo mas simple 
# (NOTA: use \ para "escapar" el caracter de comilla y que 
# el interpete de python no lo use, sino nosotros)
#src = """
#int x = 10*2+1;
#print(\"something asd\");
#print(x);
#"""









def Lexer(src: str):
    tokens = []
    splitter = Splitter(src)

    while splitter.has_more():
        current_char = splitter.current_char
        start_row = splitter.current_row
        start_col = splitter.current_column
        
        # usar esta lista para construir los tokens
        generatedToken = []

        match current_char:

            # whitespace
            case char if char.isspace():
                # dejar al splitter.next_char() actuar al final
                pass

            # palabras/keywords
            case char if char.isalpha():
                generatedToken.append(current_char)
                
                while splitter.has_more() and splitter.peek_next().isalpha():
                    splitter.next_char()
                    generatedToken.append(splitter.current_char)
                
                tokens.append(buildToken(start_row, start_col, generatedToken))

            # numbers
            case char if char.isdigit():
                generatedToken.append(current_char)

                while splitter.has_more() and splitter.peek_next().isdigit():
                    splitter.next_char()
                    generatedToken.append(splitter.current_char)
                
                tokens.append(buildToken(start_row, start_col, generatedToken, TokenType.NUMBER))

            # strings "..."
            case '"':
                # saltar en DQ de apertura
                splitter.next_char() 
                
                # Consumir hasta encontrar otro DQ o EOF
                while splitter.has_more() and splitter.current_char != '"':
                    generatedToken.append(splitter.current_char)
                    
                    # Si el sig caracter es DQ detenerse (sale del while)
                    if splitter.peek_next() == '"':
                        break
                    splitter.next_char()
                
                # Moverse una vez para llegar al DQ de cierre
                splitter.next_char() 
                
                if splitter.current_char == '"':
                    tokens.append(buildToken(
                        start_row, start_col,
                        generatedToken, 
                        TokenType.STRING_LITERAL
                    ))
                else:
                    print(f"Error: Unclosed string at {start_row}:{start_col}")

            # Simbolos/Operadores o caracteres no reconocidos
            case _:
                
                # Posible simbolo de mas de un char (<=, >=, ==)
                possible_symbol = current_char + splitter.peek_next()
                symbol = TokenType.keyword_exists(possible_symbol)
                if symbol:
                    tokens.append(buildToken(
                        start_row,
                        start_col, 
                        [possible_symbol], 
                        symbol
                    ))
                    # Avanzar el segundo caracter del simbolo doble
                    # para que el next_char() del final del loop no lo reprocese
                    splitter.next_char()
                    
                # Sino busca solo un simbolo simple
                else:
                    symbol = TokenType.keyword_exists(current_char)
                    if symbol:
                        tokens.append(buildToken(
                            start_row,
                            start_col, 
                            [current_char], 
                            symbol
                        ))
                    else:
                        print(f"Unknown character: {current_char} at {start_row}:{start_col}")

        # Esto mueve el puntero una vez por iteracion
        splitter.next_char()

    # Final EOF Token
    tokens.append(buildToken(
        splitter.current_row, 
        1, 
        ["EOF"], 
        TokenType.EOF
    ))
    return tokens