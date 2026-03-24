# Keyword documentation for Koda language

## PR_CONTROL (Flujo)
`if` / `where`
- **Token:** `IF`
- **Descripción:** Inicia un bloque condicional.
```text
Ejemplo: if (x == 1) { ... }
Ejemplo: where (x == 1) { ... }
```

`else`
- **Token:** `ELSE`
- **Descripción:** Define el bloque alternativo de un condicional.
```text
Ejemplo: else { ... }
```

<!--`switch` / `case`
- **Token:** `SWITCH` / `CASE`
- **Descripción:** Selección múltiple y caso específico a tratar.
```text
Ejemplo: switch (opcion) { case 1: ... }
```-->

`do` / `while`
- **Token:** `DO` / `WHILE`
- **Descripción:** Bucles que se ejecutan mientras se cumpla una condición.
```text
Ejemplo: do { ... } while (x < 10);
```


`for`
- **Token:** `FOR`
- **Descripción:** Estructura para bucles con contador.
```text
Ejemplo: for (int i = 0; i < 10; i++) { ... }
```

`break` / `return` / `pass` / `end`
- **Token:** `BREAK` / `RETURN` / `PASS` / `END` 
- **Descripción:** Controlan el retorno o salida de bloques retornando algun valor o no.
```text
Ejemplo: if (debug) pass; else return x;
Ejemplo: if (debug) return; else pass x;
```

---

## PR_IO (Entrada/Salida)

`out` / `print` / `echo` / `system`
- **Token:** `STDOUT`
- **Descripción:** Impresión en consola, salida estándar o stdout.
```text
Ejemplo: print "Hola"; echo "Mundo"; out x;
```

`input`
- **Token:** `STDIN`
- **Descripción:** Entrada de consola.
```text
Ejemplo: string nombre = input;
```

`open` / `read` / `file`
- **Token:** `FILE_OPEN` / `FILE_READ` / `FILE_HANDLE`
- **Descripción:** Apertura y manejo de archivos.
```text
Ejemplo: file f = open("test.txt"); read(f);
```

---

## PR_DEF (Estructura)

`function` / `def`
- **Token:** `FUNC_DECL`
- **Descripción:** Crea una función definida por el usuario.
```text
Ejemplo: def suma() { ... }
```

`main` / `head`
- **Token:** `ENTRY_P1` / `ENTRY_P2`
- **Descripción:** Funciones definidas por el lenguaje de nivel 1 y nivel 2.
```text
Ejemplo: main() { ... }
```

`new`
- **Token:** `NEW_FUNC`
- **Descripción:** Crea una función de usuario (posible instanciación).
```text
Ejemplo: new function temp() { ... }
```

---

## PR_DATA_TYPE (Tipos y Arrays)

`list` / `array`
- **Token:** `COLLECTION`
- **Descripción:** Creación de arrays o colecciones.
```text
Ejemplo: list l = [1, 2];
```

`int` / `float` / `double` / `char` / `string` / `bool`
- **Token:** `[NOMBRE_MAYUSCULAS]` (Ej: `INT`)
- **Descripción:** Definición de tipos de datos para variables.
```text
Ejemplo: float f = 1.5; bool b = true;
```

`[aA-zZ]` / `[0-9]`
- **Token:** `STRING_LITERAL` / `NUMBER` (Ej: `INT`)
- **Descripción:** Definición de tipos de datos literales.
```text
Ejemplo: print("this is a string literal");
Ejemplo: print(12);
```

`null` / `void`
- **Token:** `EMPTY`
- **Descripción:** Tipo vacío o equivalente a false/0 literal.
```text
Ejemplo: T var = null;
```

---

## PR_VAR_MOD (Modificadores)

`public` / `extern`
- **Token:** `MOD_GLOBAL`
- **Descripción:** Asigna la variable como global.
```text
Ejemplo: public int g = 10;
```

`static`
- **Token:** `MOD_LOCAL`
- **Descripción:** Asigna la variable como local.
```text
Ejemplo: static int l = 5;
```

`auto`
- **Token:** `MOD_AUTO`
- **Descripción:** Identifica contexto para decidir si es local o global.

---

## PR_ARIT (Aritmética)
Operadores para cálculos matemáticos básicos.

`+` (SUM)
- **Token:** `PLUS`
- **Descripción:** Operador de suma.
```text
Ejemplo: int x = 1 + 1;
```

`-` (MINUS)
- **Token:** `MINUS`
- **Descripción:** Operador de resta.
```text
Ejemplo: int x = 1 - 1;
```

`*` (MULT)
- **Token:** `MULT`
- **Descripción:** Operador de multiplicación.
```text
Ejemplo: int x = 1 * 1;
```

`/` (DIV)
- **Token:** `DIV`
- **Descripción:** Operador de division.
```text
Ejemplo: int x = 1 / 1;
```

---

## PR_REL (Relacionales)
Operadores para comparar valores y obtener resultados lógicos/booleanos.

`==` (EQUALS)
- **Token:** `EQUALS`
- **Descripción:** Compara si dos valores son iguales.
```text
Ejemplo: bool x = 1 == 1;
```

`<` (LT)
- **Token:** `LT`
- **Descripción:** Compara si el primer valor es menor que el segundo.
```text
Ejemplo: bool x = 1 < 1;
```

`>` (GT)
- **Token:** `GT`
- **Descripción:** Compara si el primer valor es mayor que el segundo.
```text
Ejemplo: bool x = 1 > 1;
```

`>=` (GTE)
- **Token:** `GTE`
- **Descripción:** Compara si el primero es mayor o igual que el segundo.
```text
Ejemplo: bool x = 1 >= 1;
```

`<=` (LTE)
- **Token:** `LTE`
- **Descripción:** Compara si el primero es menor o igual que el segundo.
```text
Ejemplo: bool x = 1 <= 1;
```

---

## PR_LOGIC (Lógica)
Operaciones lógicas (pendientes de definir a bajo nivel).

`or` (OR)
- **Token:** `---not implemented yet---`
- **Descripción:** Realiza una operación lógica de unión (O).
```text
Ejemplo: if (a or b) { ... }
```

`and` (AND)
- **Token:** `---not implemented yet---`
- **Descripción:** Realiza una operación lógica de intersección (Y).
```text
Ejemplo: if (a and b) { ... }
```

`not` (NOT)
- **Token:** `---not implemented yet---`
- **Descripción:** Realiza una operación lógica de negación (NO).
```text
Ejemplo: if (not a) { ... }
```

---

## PUNCTUATION & ASSIGN
*Signos de puntuación y asignación de valores.*

`,` (COMMA)
- **Token:** `---not implemented yet---`
- **Descripción:** Separa parámetros en funciones o elementos en arrays.
```text
Ejemplo: array arr = [1, 2];
Ejemplo: func yourFunc(param1, param2){ ... }
```

`;` (SEMICOLON)
- **Token:** `SEMICOLON`
- **Descripción:** Indica el final de una sentencia o instrucción.
```text
Ejemplo: x = 10;
```

`"` (DOUBLEQOUT)
- **Token:** `SEMICOLON`
- **Descripción:** Delimita cadenas de texto (strings) y caracteres.
```text
Ejemplo: "any text goes here";
```

<!--`=` (ASSIGN)
- **Token:** `ASSIGN`
- **Descripción:** Asigna un valor a un identificador (ID).
```text
Ejemplo: int x = 10;
```-->

---

## DELIMITERS
Definen el alcance de bloques y parámetros.

`{` (LBRACE)
- **Token:** `LBRACE`
- **Descripción:** Abre un bloque para una definición de función o estructura.
```text
Ejemplo: function suma() { ... 
```

`}` (RBRACE)
- **Token:** `RBRACE`
- **Descripción:** Cierra un bloque de definición.
```text
Ejemplo: ... }
```

`(` (LPAREN)
- **Token:** `LPAREN`
- **Descripción:** Abre un bloque para definir parámetros o agrupar expresiones.
```text
Ejemplo: function suma( ...
```

`)` (RPAREN)
- **Token:** `RPAREN`
- **Descripción:** Cierra el bloque de parámetros o expresiones.
```text
Ejemplo: ... ){ ... }
```

---

## VARIABLE DEFINITION
Identificadores para nombrar elementos en el código.

`<cualquiera>` (ID)
- **Token:** `<cualquiera>`
- **Descripción:** El nombre o identificador que el usuario asigna a una variable o función.
```text
Ejemplo: int x = 10; (donde "x" es el token ID)
```

