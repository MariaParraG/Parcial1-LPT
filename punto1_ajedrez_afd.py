"""
============================================================================
PARCIAL 1 - Punto 1
Lenguajes de Programación
============================================================================

PROBLEMA:
    Definir una expresión regular para el lenguaje de movimientos de ajedrez
    (ej: p->k4, kbp X qn) e implementar el AFD correspondiente en Python.

EXPRESIÓN REGULAR:
    La notación algebraica descriptiva de ajedrez incluye:
    - Pieza que se mueve: p (peón), k (rey/king), q (reina/queen),
      r (torre/rook), b (alfil/bishop), n (caballo/knight)
    - Combinaciones de piezas: kbp (king-bishop-pawn), etc.
    - Operador de movimiento: -> (se mueve a)
    - Operador de captura: X
    - Destino: pieza destino o casilla (letra + número, ej: k4, qn, e5)

    Expresión Regular (simplificada):
        [pkqrbn]+ (->|X) [pkqrbn]*[1-8]?

    Esto captura:
      - Una o más letras de pieza al inicio
      - Seguido de '->' (movimiento) o 'X' (captura)
      - Seguido de pieza(s) destino o casilla

    Ejemplos válidos:
      p->k4   (peón se mueve a k4)
      kbp X qn (king-bishop-pawn captura queen-knight)
      r->e5   (torre se mueve a e5)
      q X r   (reina captura torre)

=============================================================================
AUTÓMATA FINITO DETERMINISTA (AFD)
=============================================================================

    Estados:
      q0 - Estado inicial: esperando pieza origen
      q1 - Leyendo pieza(s) origen (una o más letras válidas)
      q2 - Leído '-' (primer carácter del operador de movimiento)
      q3 - Leído '->' (operador movimiento completo), esperando destino
      q4 - Leído 'X' (operador captura), esperando destino
      q5 - Leyendo destino (letras de pieza o casilla)
      q6 - Estado de ACEPTACIÓN (movimiento completo)
      qerr - Estado de ERROR (cadena inválida)

    Alfabeto: {p, k, q, r, b, n, -, >, X, 1-8, espacio}

    Tabla de transiciones:
    ┌───────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
    │ Estado│pieza │  -   │  >   │  X   │ 1-8  │space │otros │      │      │
    ├───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
    │  q0   │  q1  │ qerr │ qerr │ qerr │ qerr │  q0  │ qerr │      │      │
    │  q1   │  q1  │  q2  │ qerr │  q4  │ qerr │  q1* │ qerr │      │      │
    │  q2   │ qerr │ qerr │  q3  │ qerr │ qerr │ qerr │ qerr │      │      │
    │  q3   │  q5  │ qerr │ qerr │ qerr │  q5  │  q3* │ qerr │      │      │
    │  q4   │  q5  │ qerr │ qerr │ qerr │  q5  │  q4* │ qerr │      │      │
    │  q5   │  q5  │ qerr │ qerr │ qerr │  q6  │ qerr │ qerr │      │      │
    │  q6   │ qerr │ qerr │ qerr │ qerr │ qerr │ qerr │ qerr │      │      │
    └───────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
    * espacio permitido como separador entre tokens

"""

import re

# =============================================================================
# IMPLEMENTACIÓN MEDIANTE EXPRESIÓN REGULAR
# =============================================================================

# Piezas válidas de ajedrez (minúsculas)
PIEZAS = r'[pkqrbn]'

# Expresión regular completa para un movimiento de ajedrez
# Permite espacios opcionales alrededor de los operadores
REGEX_AJEDREZ = re.compile(
    r'^'
    r'(' + PIEZAS + r'+)'      # Grupo 1: Una o más piezas origen
    r'\s*'                      # Espacios opcionales
    r'(->|X)'                   # Grupo 2: Operador (movimiento o captura)
    r'\s*'                      # Espacios opcionales
    r'(' + PIEZAS + r'*[1-8])' # Grupo 3: Destino (pieza(s) + número de fila)
    r'$',
    re.IGNORECASE
)


# =============================================================================
# IMPLEMENTACIÓN DEL AFD
# =============================================================================

class EstadoAFD:
    """Enumeración de los estados del AFD."""
    Q0   = 'q0'    # Estado inicial
    Q1   = 'q1'    # Leyendo pieza(s) origen
    Q2   = 'q2'    # Leído '-'
    Q3   = 'q3'    # Leído '->' completo
    Q4   = 'q4'    # Leído 'X' (captura)
    Q5   = 'q5'    # Leyendo destino
    Q6   = 'q6'    # ACEPTACIÓN
    QERR = 'qerr'  # ERROR


def clasificar_caracter(c: str) -> str:
    """
    Clasifica un carácter en su categoría para el AFD.
    
    Args:
        c: carácter a clasificar
    
    Returns:
        Categoría del carácter
    """
    c_lower = c.lower()
    if c_lower in 'pkqrbn':
        return 'pieza'
    elif c == '-':
        return 'guion'
    elif c == '>':
        return 'mayor'
    elif c.upper() == 'X':
        return 'captura'
    elif c in '12345678':
        return 'numero'
    elif c == ' ':
        return 'espacio'
    else:
        return 'otro'


# Tabla de transiciones del AFD
# Formato: {estado_actual: {categoria_caracter: estado_siguiente}}
TABLA_TRANSICIONES = {
    EstadoAFD.Q0: {
        'pieza':   EstadoAFD.Q1,
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.QERR,
        'espacio': EstadoAFD.Q0,    # Espacios iniciales ignorados
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q1: {
        'pieza':   EstadoAFD.Q1,    # Más letras de pieza origen
        'guion':   EstadoAFD.Q2,    # Inicio de '->'
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.Q4,    # Captura directa con X
        'numero':  EstadoAFD.QERR,
        'espacio': EstadoAFD.Q1,    # Espacio antes de operador
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q2: {
        'pieza':   EstadoAFD.QERR,
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.Q3,    # Completa '->'
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.QERR,
        'espacio': EstadoAFD.QERR,
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q3: {
        'pieza':   EstadoAFD.Q5,    # Empieza a leer destino
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.Q6,    # Número directo como destino
        'espacio': EstadoAFD.Q3,    # Espacio después de '->'
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q4: {
        'pieza':   EstadoAFD.Q5,    # Empieza a leer destino tras captura
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.Q6,    # Número directo como destino
        'espacio': EstadoAFD.Q4,    # Espacio después de 'X'
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q5: {
        'pieza':   EstadoAFD.Q5,    # Más letras en el destino
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.Q6,    # Número de fila: movimiento completo
        'espacio': EstadoAFD.QERR,
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.Q6: {
        'pieza':   EstadoAFD.QERR,
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.QERR,
        'espacio': EstadoAFD.QERR,
        'otro':    EstadoAFD.QERR,
    },
    EstadoAFD.QERR: {
        'pieza':   EstadoAFD.QERR,
        'guion':   EstadoAFD.QERR,
        'mayor':   EstadoAFD.QERR,
        'captura': EstadoAFD.QERR,
        'numero':  EstadoAFD.QERR,
        'espacio': EstadoAFD.QERR,
        'otro':    EstadoAFD.QERR,
    },
}

# Estado de aceptación
ESTADOS_ACEPTACION = {EstadoAFD.Q6}


def afd_ajedrez(cadena: str) -> tuple[bool, list[tuple]]:
    """
    Ejecuta el AFD sobre una cadena de entrada para determinar si
    representa un movimiento de ajedrez válido.

    Args:
        cadena: La cadena de movimiento a evaluar.

    Returns:
        Tupla (es_valido, historial_transiciones)
        - es_valido: True si la cadena es aceptada por el AFD
        - historial_transiciones: Lista de (char, categoria, estado_anterior, estado_nuevo)
    """
    estado_actual = EstadoAFD.Q0
    historial = []

    for char in cadena:
        categoria = clasificar_caracter(char)
        estado_anterior = estado_actual
        estado_actual = TABLA_TRANSICIONES[estado_actual][categoria]
        historial.append((char, categoria, estado_anterior, estado_actual))

        if estado_actual == EstadoAFD.QERR:
            break  # No hay retorno desde el estado de error

    es_valido = estado_actual in ESTADOS_ACEPTACION
    return es_valido, historial


def evaluar_movimiento(movimiento: str, usar_regex: bool = False) -> None:
    """
    Evalúa un movimiento de ajedrez usando el AFD o la regex,
    e imprime el resultado con detalle de las transiciones.

    Args:
        movimiento: La cadena del movimiento a evaluar.
        usar_regex: Si True, usa la expresión regular; si False, usa el AFD.
    """
    print(f"\n{'='*60}")
    print(f"  Movimiento: '{movimiento}'")
    print(f"{'='*60}")

    if usar_regex:
        # Validación con expresión regular
        match = REGEX_AJEDREZ.match(movimiento.strip())
        resultado = "✅ ACEPTADO" if match else "❌ RECHAZADO"
        print(f"  Método: Expresión Regular")
        print(f"  Regex:  {REGEX_AJEDREZ.pattern}")
        print(f"  Resultado: {resultado}")
        if match:
            print(f"  Grupos: origen='{match.group(1)}', "
                  f"operador='{match.group(2)}', destino='{match.group(3)}'")
    else:
        # Validación con AFD
        es_valido, historial = afd_ajedrez(movimiento)
        resultado = "✅ ACEPTADO" if es_valido else "❌ RECHAZADO"
        print(f"  Método: AFD (Autómata Finito Determinista)")
        print(f"  Resultado: {resultado}")
        print(f"\n  Traza de transiciones:")
        print(f"  {'Char':<8} {'Categoría':<12} {'Estado Ant.':<12} {'Estado Sig.':<12}")
        print(f"  {'-'*44}")
        for char, cat, e_ant, e_sig in historial:
            display_char = repr(char) if char == ' ' else char
            print(f"  {display_char:<8} {cat:<12} {e_ant:<12} {e_sig:<12}")
        print(f"\n  Estado final: {historial[-1][3] if historial else EstadoAFD.Q0}")


# =============================================================================
# PRUEBAS
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  PARCIAL 1 - PUNTO 1")
    print("  AFD para Movimientos de Ajedrez")
    print("=" * 60)

    print("\n>>> EXPRESIÓN REGULAR DEFINIDA:")
    print(f"    {REGEX_AJEDREZ.pattern}")
    print("""
    Descripción:
    - [pkqrbn]+  → Una o más piezas origen (p,k,q,r,b,n)
    - \\s*        → Espacios opcionales
    - (->|X)     → Operador: '->' movimiento, 'X' captura
    - \\s*        → Espacios opcionales
    - [pkqrbn]*[1-8] → Destino: pieza(s) opcional(es) + número de fila
    """)

    # -------------------------------------------------------------------------
    # CASOS DE PRUEBA
    # -------------------------------------------------------------------------
    casos_prueba = [
        # (movimiento, descripcion, deberia_aceptar)
        ("p->k4",     "Peón se mueve a k4 (del enunciado)",       True),
        ("kbp X qn3", "King-bishop-pawn captura en qn3 (del enunciado)", True),  # necesita numero
        ("r->e5",     "Torre se mueve a e5",                       True),
        ("q X r3",    "Reina captura torre en fila 3",             True),
        ("n->b3",     "Caballo se mueve a b3",                     True),
        ("kb->qr4",   "King-bishop a queen-rook fila 4",           True),
        ("5->k4",     "INVÁLIDO: empieza con número",              False),
        ("p-->k4",    "INVÁLIDO: doble guion",                     False),
        ("->k4",      "INVÁLIDO: sin pieza origen",                False),
        ("p->",       "INVÁLIDO: sin destino",                     False),
        ("p X",       "INVÁLIDO: captura sin destino",             False),
        ("p->k9",     "INVÁLIDO: fila 9 no existe en ajedrez",     False),
    ]

    print("\n" + "=" * 60)
    print("  PRUEBAS CON AFD")
    print("=" * 60)
    for movimiento, descripcion, esperado in casos_prueba:
        es_valido, _ = afd_ajedrez(movimiento)
        icono = "✅" if es_valido else "❌"
        estado = "ACEPTADO" if es_valido else "RECHAZADO"
        correcto = "✔ correcto" if es_valido == esperado else "✘ FALLO"
        print(f"  {icono} {estado:<12} | {movimiento:<14} | {descripcion} [{correcto}]")

    print("\n" + "=" * 60)
    print("  TRAZA DETALLADA DE CASOS SELECCIONADOS")
    print("=" * 60)

    # Traza detallada de los dos ejemplos del enunciado
    evaluar_movimiento("p->k4")
    evaluar_movimiento("kbp X qn3")
    evaluar_movimiento("5->k4")  # Caso de rechazo
