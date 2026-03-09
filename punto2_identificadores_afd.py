"""
============================================================================
PARCIAL 1 - Punto 2
Lenguajes de Programación
============================================================================

PROBLEMA:
    Implementar un AFD en Python para la expresión regular de un identificador
    (ID):
        [A-Za-Z][A-Za-z0-9]*

    Nota: la expresión del enunciado tiene un typo en [A-ZA-Z]; se interpreta
    como [A-Za-z] (letras mayúsculas o minúsculas).

EXPRESIÓN REGULAR:
    [A-Za-z][A-Za-z0-9]*

    Descripción:
    - [A-Za-z]    → El primer carácter DEBE ser una letra (mayúscula o minúscula)
    - [A-Za-z0-9]*→ Los siguientes caracteres pueden ser letras o dígitos
                    (cero o más veces)

    Ejemplos válidos:    variable, X, miVar123, _NO (sin _), A1B2
    Ejemplos inválidos:  1abc, 123, _var, @nombre, ""

=============================================================================
AUTÓMATA FINITO DETERMINISTA (AFD)
=============================================================================

    Estados:
      q0   - Estado inicial: esperando el primer carácter
      q1   - Estado de ACEPTACIÓN: se leyó al menos una letra válida
      qerr - Estado de ERROR: carácter inválido encontrado

    Alfabeto: {A-Z, a-z, 0-9, otros}

    Tabla de transiciones:
    ┌─────────┬─────────┬──────────┬──────────┐
    │ Estado  │  letra  │  dígito  │  otro    │
    ├─────────┼─────────┼──────────┼──────────┤
    │   q0    │   q1    │   qerr   │   qerr   │
    │   q1    │   q1    │   q1     │   qerr   │
    │  qerr   │  qerr   │  qerr    │   qerr   │
    └─────────┴─────────┴──────────┴──────────┘

    Estado inicial:     q0
    Estado aceptación:  {q1}

"""

import re

# =============================================================================
# EXPRESIÓN REGULAR DE REFERENCIA
# =============================================================================
REGEX_ID = re.compile(r'^[A-Za-z][A-Za-z0-9]*$')


# =============================================================================
# DEFINICIÓN DEL AFD
# =============================================================================

class Estado:
    """Constantes para los estados del AFD."""
    Q0   = 'q0'    # Inicial: esperando primer carácter
    Q1   = 'q1'    # Aceptación: ID válido en construcción
    QERR = 'qerr'  # Error: carácter no permitido


def clasificar(caracter: str) -> str:
    """
    Clasifica un carácter según las categorías del alfabeto del AFD.

    Args:
        caracter: El carácter a clasificar.

    Returns:
        'letra'  → si es A-Z o a-z
        'digito' → si es 0-9
        'otro'   → cualquier otro símbolo
    """
    if caracter.isalpha():
        return 'letra'
    elif caracter.isdigit():
        return 'digito'
    else:
        return 'otro'


# Tabla de transiciones del AFD: {estado: {categoria: estado_siguiente}}
TRANSICIONES = {
    Estado.Q0: {
        'letra':  Estado.Q1,    # Primer carácter letra → válido, ir a q1
        'digito': Estado.QERR,  # Empieza con dígito → inválido
        'otro':   Estado.QERR,  # Empieza con símbolo → inválido
    },
    Estado.Q1: {
        'letra':  Estado.Q1,    # Letra adicional → sigue siendo válido
        'digito': Estado.Q1,    # Dígito adicional → sigue siendo válido
        'otro':   Estado.QERR,  # Símbolo → inválido
    },
    Estado.QERR: {
        'letra':  Estado.QERR,  # Una vez en error, no hay retorno
        'digito': Estado.QERR,
        'otro':   Estado.QERR,
    },
}

# Conjunto de estados de aceptación
ESTADOS_ACEPTACION = {Estado.Q1}


def ejecutar_afd(cadena: str) -> tuple[bool, list[tuple], str]:
    """
    Ejecuta el AFD sobre una cadena de entrada.

    El AFD procesa carácter por carácter, consultando la tabla de
    transiciones para cada símbolo del alfabeto.

    Args:
        cadena: La cadena a evaluar como posible identificador.

    Returns:
        Tupla con:
        - es_valido (bool): True si la cadena es aceptada
        - historial (list): Lista de tuplas (char, categoría, estado_ant, estado_sig)
        - estado_final (str): El estado en que terminó el AFD
    """
    if len(cadena) == 0:
        return False, [], Estado.Q0

    estado_actual = Estado.Q0
    historial = []

    for char in cadena:
        categoria = clasificar(char)
        estado_anterior = estado_actual
        estado_actual = TRANSICIONES[estado_actual][categoria]
        historial.append((char, categoria, estado_anterior, estado_actual))

        # Optimización: si llegamos a error, podemos parar
        if estado_actual == Estado.QERR:
            break

    es_valido = estado_actual in ESTADOS_ACEPTACION
    return es_valido, historial, estado_actual


def imprimir_resultado(cadena: str) -> None:
    """
    Imprime el resultado detallado de la evaluación de una cadena por el AFD.

    Muestra:
    - La cadena evaluada
    - Tabla de transiciones paso a paso
    - El estado final y veredicto (ACEPTA / NO ACEPTA)
    - Verificación con la expresión regular

    Args:
        cadena: La cadena a evaluar.
    """
    es_valido, historial, estado_final = ejecutar_afd(cadena)

    print(f"\n{'='*58}")
    display = repr(cadena) if cadena == '' else f"'{cadena}'"
    print(f"  Evaluando: {display}")
    print(f"{'='*58}")

    if not historial:
        print("  ⚠  Cadena vacía → Estado final: q0 → NO ACEPTA")
    else:
        # Encabezado de la tabla de transiciones
        print(f"  {'Paso':<6} {'Char':<8} {'Categoría':<10} {'Est. Ant.':<12} {'Est. Sig.':<12}")
        print(f"  {'-'*50}")

        for i, (char, cat, e_ant, e_sig) in enumerate(historial, 1):
            print(f"  {i:<6} {char:<8} {cat:<10} {e_ant:<12} {e_sig:<12}")

        print(f"\n  Estado inicial:  {Estado.Q0}")
        print(f"  Estado final:    {estado_final}")
        print(f"  Es de aceptación: {'Sí ✅' if estado_final in ESTADOS_ACEPTACION else 'No ❌'}")

    # Verificación con regex
    regex_valido = bool(REGEX_ID.match(cadena))
    veredicto = "✅  ACEPTA" if es_valido else "❌  NO ACEPTA"
    print(f"\n  ▶ VEREDICTO AFD:   {veredicto}")
    print(f"  ▶ VEREDICTO Regex: {'✅  ACEPTA' if regex_valido else '❌  NO ACEPTA'}")
    coincide = "✔ Coinciden" if es_valido == regex_valido else "✘ DISCREPANCIA"
    print(f"  ▶ Consistencia:    {coincide}")


# =============================================================================
# PRUEBAS
# =============================================================================

if __name__ == '__main__':
    print("=" * 58)
    print("  PARCIAL 1 - PUNTO 2")
    print("  AFD para Identificadores (ID)")
    print("=" * 58)

    print("\n>>> EXPRESIÓN REGULAR:")
    print("    [A-Za-z][A-Za-z0-9]*")
    print("""
    Significado:
    - [A-Za-z]     → Primer carácter: obligatoriamente una letra
    - [A-Za-z0-9]* → Resto: letras o dígitos (0 o más veces)
    """)

    print(">>> DIAGRAMA DEL AFD:")
    print("""
         letra            letra/dígito
    ──► (q0) ──────────► ((q1)) ◄──┐
          │                  │      │
          │ dígito/otro       │ otro │
          ▼                  ▼      │
        (qerr) ◄─────────────────  │
          └──────────────── qerr ──┘

    q0   = Estado inicial
    q1   = Estado de ACEPTACIÓN (doble círculo)
    qerr = Estado de error (trampa)
    """)

    # -------------------------------------------------------------------------
    # CASOS DE PRUEBA REQUERIDOS: 3 ACEPTADOS + 2 RECHAZADOS
    # -------------------------------------------------------------------------

    casos_aceptar = [
        ("variable",    "Identificador simple, todas minúsculas"),
        ("MiVariable",  "Identificador mixto, empieza con mayúscula"),
        ("X1Y2Z3",      "Identificador con letras y dígitos alternados"),
    ]

    casos_rechazar = [
        ("1variable",   "Empieza con dígito → INVÁLIDO"),
        ("mi-var",      "Contiene guion '-' → INVÁLIDO"),
    ]

    print("\n" + "=" * 58)
    print("  CASOS QUE DEBEN SER ACEPTADOS (3 pruebas)")
    print("=" * 58)
    for cadena, descripcion in casos_aceptar:
        print(f"\n  [{descripcion}]")
        imprimir_resultado(cadena)

    print("\n" + "=" * 58)
    print("  CASOS QUE NO DEBEN SER ACEPTADOS (2 pruebas)")
    print("=" * 58)
    for cadena, descripcion in casos_rechazar:
        print(f"\n  [{descripcion}]")
        imprimir_resultado(cadena)

    # -------------------------------------------------------------------------
    # RESUMEN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 58)
    print("  RESUMEN DE TODAS LAS PRUEBAS")
    print("=" * 58)
    todos = [(c, d, True) for c, d in casos_aceptar] + \
            [(c, d, False) for c, d in casos_rechazar]

    print(f"\n  {'Cadena':<18} {'Esperado':<14} {'AFD':<14} {'Estado'}")
    print(f"  {'-'*56}")
    for cadena, desc, esperado in todos:
        resultado, _, _ = ejecutar_afd(cadena)
        esperado_str = "ACEPTA     " if esperado else "NO ACEPTA  "
        resultado_str = "ACEPTA     " if resultado else "NO ACEPTA  "
        ok = "✔" if resultado == esperado else "✘ FALLO"
        print(f"  {cadena:<18} {esperado_str:<14} {resultado_str:<14} {ok}")
