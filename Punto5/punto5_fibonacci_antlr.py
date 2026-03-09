"""
=============================================================================
PARCIAL 1 - Punto 5
Lenguajes de Programación
=============================================================================

ARCHIVO: punto5_fibonacci_antlr.py

DESCRIPCIÓN:
    Programa ANTLR en Python que calcula la secuencia de Fibonacci de un
    número dado.

    Formato de entrada:  FIBO(20)
    Formato de salida:   0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...

    La entrada y salida son por consola.
    El lenguaje objetivo (target) es Python.

ARCHIVOS ANTLR NECESARIOS:
    - Fibonacci.g4              → Gramática ANTLR
    - FibonacciLexer.py         → Lexer generado (auto-generado por ANTLR)
    - FibonacciParser.py        → Parser generado (auto-generado por ANTLR)
    - FibonacciListener.py      → Listener base generado
    - FibonacciVisitor.py       → Visitor base generado

INSTRUCCIONES DE INSTALACIÓN Y USO:
    1. Instalar Java (requerido por ANTLR):
       sudo apt-get install default-jre

    2. Descargar ANTLR:
       wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
       export CLASSPATH=".:antlr-4.13.1-complete.jar:$CLASSPATH"

    3. Instalar el runtime Python de ANTLR:
       pip install antlr4-python3-runtime==4.13.1

    4. Generar el parser desde la gramática:
       java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 Fibonacci.g4

    5. Ejecutar:
       python punto5_fibonacci_antlr.py

=============================================================================
GRAMÁTICA ANTLR (Fibonacci.g4)
=============================================================================

    grammar Fibonacci;

    // Regla de inicio
    programa : comando EOF ;

    // Comando FIBO(n)
    comando : FIBO LPAREN NUMERO RPAREN ;

    // Tokens
    FIBO   : 'FIBO' ;
    NUMERO : [0-9]+ ;
    LPAREN : '(' ;
    RPAREN : ')' ;
    WS     : [ \\t\\n\\r]+ -> skip ;

=============================================================================
"""

# Intentar importar el runtime de ANTLR
try:
    from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
    from antlr4.error.ErrorListener import ErrorListener
    ANTLR_DISPONIBLE = True
except ImportError:
    ANTLR_DISPONIBLE = False


# =============================================================================
# GRAMÁTICA ANTLR (se guarda en archivo .g4 para usar con la herramienta)
# =============================================================================

GRAMATICA_G4 = """
/*
 * Fibonacci.g4
 * Gramática ANTLR4 para el comando FIBO(n)
 *
 * Genera la secuencia de Fibonacci desde fib(0) hasta fib(n-1).
 *
 * Ejemplo:
 *   Entrada: FIBO(8)
 *   Salida:  0, 1, 1, 2, 3, 5, 8, 13
 */
grammar Fibonacci;

// ─── REGLAS DE PARSER ───────────────────────────────────────────────────────

/* Regla raíz: un programa es exactamente un comando seguido de EOF */
programa
    : comando EOF
    ;

/* Comando: FIBO seguido de un número entre paréntesis */
comando
    : FIBO LPAREN numero RPAREN
    ;

/* Número: capturado como regla para facilitar el acceso en el visitor */
numero
    : NUMERO
    ;

// ─── REGLAS DE LEXER (TOKENS) ───────────────────────────────────────────────

FIBO    : 'FIBO' ;          /* Palabra clave de la función */
NUMERO  : [0-9]+ ;          /* Uno o más dígitos */
LPAREN  : '(' ;             /* Paréntesis izquierdo */
RPAREN  : ')' ;             /* Paréntesis derecho */

/* Espacios en blanco: ignorados (skip) */
WS      : [ \\t\\n\\r]+ -> skip ;

/* Cualquier otro carácter: error */
ERROR_CHAR
    : .  { raise Exception(f"Carácter no reconocido: '{self.text}'") }
    ;
"""


# =============================================================================
# IMPLEMENTACIÓN DEL INTÉRPRETE
# =============================================================================

class ManejadorErrores:
    """
    Manejador personalizado de errores para el parser ANTLR.
    Reemplaza el comportamiento por defecto que solo imprime en stderr.
    """
    def __init__(self):
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append(
            f"  Error de sintaxis en línea {line}, columna {column}: {msg}"
        )

    def reportAmbiguity(self, *args):
        pass

    def reportAttemptingFullContext(self, *args):
        pass

    def reportContextSensitivity(self, *args):
        pass


def calcular_fibonacci_secuencia(n: int) -> list[int]:
    """
    Calcula la secuencia de Fibonacci desde fib(0) hasta fib(n-1).

    La secuencia se define como:
        fib(0) = 0
        fib(1) = 1
        fib(k) = fib(k-1) + fib(k-2)  para k >= 2

    Se usa el enfoque iterativo para eficiencia, ya que ANTLR ya maneja
    el parsing; el cálculo numérico se hace de forma óptima.

    Args:
        n: Cuántos términos calcular (cantidad de elementos en la secuencia).
           FIBO(8) → 8 términos: 0, 1, 1, 2, 3, 5, 8, 13

    Returns:
        Lista con los primeros n términos de la secuencia de Fibonacci.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]

    secuencia = [0, 1]
    for i in range(2, n):
        secuencia.append(secuencia[i-1] + secuencia[i-2])
    return secuencia


def parsear_y_ejecutar_con_antlr(entrada: str) -> None:
    """
    Usa el parser ANTLR para analizar la entrada y ejecutar el comando FIBO.

    Args:
        entrada: La cadena de entrada (ej: "FIBO(20)").
    """
    if not ANTLR_DISPONIBLE:
        raise ImportError("antlr4-python3-runtime no está instalado")

    try:
        from FibonacciLexer import FibonacciLexer
        from FibonacciParser import FibonacciParser
    except ImportError:
        raise ImportError(
            "Los archivos FibonacciLexer.py y FibonacciParser.py no existen.\n"
            "Genera el parser con: java -jar antlr-4.13.1-complete.jar "
            "-Dlanguage=Python3 Fibonacci.g4"
        )

    # Crear el flujo de caracteres de entrada
    input_stream = InputStream(entrada)

    # Crear el lexer
    lexer = FibonacciLexer(input_stream)
    manejador_err = ManejadorErrores()
    lexer.removeErrorListeners()
    lexer.addErrorListener(manejador_err)

    # Crear el flujo de tokens
    token_stream = CommonTokenStream(lexer)

    # Crear el parser
    parser = FibonacciParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(manejador_err)

    # Parsear a partir de la regla 'programa'
    arbol = parser.programa()

    # Verificar errores
    if manejador_err.errores:
        print("[ERROR DE SINTAXIS]")
        for err in manejador_err.errores:
            print(err)
        return

    # Extraer el número del árbol sintáctico
    n = int(arbol.comando().numero().NUMERO().getText())

    # Calcular y mostrar la secuencia
    secuencia = calcular_fibonacci_secuencia(n)
    print(", ".join(str(x) for x in secuencia))


def parsear_sin_antlr(entrada: str) -> None:
    """
    Implementa un mini-parser manual para FIBO(n) sin depender de ANTLR.
    Se usa como fallback cuando el runtime de ANTLR no está disponible.

    Este parser implementa manualmente la gramática:
        programa → comando EOF
        comando  → 'FIBO' '(' NUMERO ')'

    Args:
        entrada: La cadena de entrada (ej: "FIBO(20)").
    """
    import re

    # Patrón de la gramática: FIBO(numero)
    patron = re.compile(r'^\s*FIBO\s*\(\s*(\d+)\s*\)\s*$')
    match = patron.match(entrada.strip())

    if not match:
        print(f"[ERROR SINTÁCTICO] Formato inválido: '{entrada}'")
        print("  Formato esperado: FIBO(<número>)  Ejemplo: FIBO(20)")
        return

    n = int(match.group(1))

    if n < 0:
        print(f"[ERROR SEMÁNTICO] El argumento debe ser no negativo. Recibido: {n}")
        return

    secuencia = calcular_fibonacci_secuencia(n)
    if secuencia:
        print(", ".join(str(x) for x in secuencia))
    else:
        print("(secuencia vacía)")


def mostrar_tokens(entrada: str) -> None:
    """
    Muestra el análisis léxico de la cadena de entrada (tokenización manual).
    Ilustra lo que el lexer ANTLR haría automáticamente.

    Args:
        entrada: La cadena a tokenizar.
    """
    import re

    TOKEN_PATRON = [
        ('FIBO',   r'FIBO'),
        ('NUMERO', r'\d+'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('WS',     r'[ \t\n\r]+'),
        ('ERROR',  r'.'),
    ]

    patron_combinado = '|'.join(f'(?P<{nombre}>{regex})'
                                 for nombre, regex in TOKEN_PATRON)
    tokens = []
    for m in re.finditer(patron_combinado, entrada):
        tipo = m.lastgroup
        valor = m.group()
        if tipo != 'WS':
            tokens.append((tipo, valor))

    print(f"\n  Análisis léxico de: '{entrada}'")
    print(f"  {'Token':<10} {'Tipo':<10}")
    print(f"  {'-'*22}")
    for tipo, valor in tokens:
        print(f"  {valor:<10} {tipo:<10}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == '__main__':

    # Guardar la gramática en el archivo .g4
    with open('/mnt/user-data/outputs/punto5_Fibonacci.g4', 'w') as f:
        f.write(GRAMATICA_G4)

    print("=" * 60)
    print("  PARCIAL 1 - PUNTO 5")
    print("  ANTLR - Calculadora de Secuencia de Fibonacci")
    print("=" * 60)

    print("""
  GRAMÁTICA ANTLR (Fibonacci.g4):
  ─────────────────────────────────────────────────────
  programa : comando EOF ;
  comando  : FIBO LPAREN numero RPAREN ;
  numero   : NUMERO ;
  FIBO     : 'FIBO' ;
  NUMERO   : [0-9]+ ;
  LPAREN   : '(' ;
  RPAREN   : ')' ;
  WS       : [ \\t\\n\\r]+ -> skip ;
  ─────────────────────────────────────────────────────

  (La gramática se guardó en: punto5_Fibonacci.g4)

  MODO DE EJECUCIÓN:
  {'ANTLR Runtime' if ANTLR_DISPONIBLE else 'Parser manual (ANTLR no disponible)'}
    """)

    print("  Archivos generados por ANTLR desde Fibonacci.g4:")
    print("    FibonacciLexer.py   → Analizador léxico")
    print("    FibonacciParser.py  → Analizador sintáctico")
    print("    FibonacciListener.py→ Listener (patrón observer)")
    print("    FibonacciVisitor.py → Visitor (patrón visitor)")

    print("\n" + "=" * 60)
    print("  CALCULADORA FIBONACCI - Entrada/Salida por Consola")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # MODO INTERACTIVO
    # -------------------------------------------------------------------------
    casos_demo = [
        "FIBO(8)",    # Del enunciado: 0, 1, 1, 2, 3, 5, 8, 13
        "FIBO(20)",   # Del enunciado: 20 términos
        "FIBO(1)",    # Caso borde: un solo término
        "FIBO(0)",    # Caso borde: secuencia vacía
        "FIBO(15)",   # Caso adicional
    ]

    print("\n  Demostraciones automáticas:")
    print("  ─────────────────────────────────────────────────────")
    for caso in casos_demo:
        mostrar_tokens(caso)
        print(f"\n  Entrada:  {caso}")
        print(f"  Salida:   ", end="")
        parsear_sin_antlr(caso)
        print()

    # -------------------------------------------------------------------------
    # MODO INTERACTIVO (usuario escribe el comando)
    # -------------------------------------------------------------------------
    print("=" * 60)
    print("  MODO INTERACTIVO")
    print("  Escriba un comando FIBO(n) o 'salir' para terminar")
    print("=" * 60)

    while True:
        try:
            entrada = input("\n  >> ").strip()
            if entrada.lower() in ('salir', 'exit', 'quit', ''):
                print("  Hasta luego.")
                break

            if ANTLR_DISPONIBLE:
                try:
                    parsear_y_ejecutar_con_antlr(entrada)
                except ImportError as e:
                    print(f"  [Fallback a parser manual] {e}")
                    parsear_sin_antlr(entrada)
            else:
                parsear_sin_antlr(entrada)

        except (EOFError, KeyboardInterrupt):
            print("\n  Hasta luego.")
            break
