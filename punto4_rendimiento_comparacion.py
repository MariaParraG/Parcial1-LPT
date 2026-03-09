"""
=============================================================================
PARCIAL 1 - Punto 4
Lenguajes de Programación
=============================================================================

PROBLEMA:
    Comparar el rendimiento entre un lenguaje compilado (C) y un lenguaje
    interpretado (Python), usando una función recursiva.

DESCRIPCIÓN:
    Se implementa la función de Fibonacci recursiva tanto en Python como
    en C. Este script Python:
    1. Ejecuta la versión Python y mide el tiempo.
    2. Compila y ejecuta la versión C, midiendo el tiempo.
    3. Genera una comparación estadística y gráfica de los resultados.

    La función de Fibonacci recursiva es un benchmark clásico porque:
    - Tiene complejidad exponencial O(2^n) → hace MUCHAS llamadas recursivas
    - No tiene efectos secundarios → mide CPU pura, no I/O
    - Es idéntica semánticamente en ambos lenguajes

FUNCIÓN DE FIBONACCI RECURSIVA:
    fib(0) = 0
    fib(1) = 1
    fib(n) = fib(n-1) + fib(n-2)  para n > 1

    Llamadas para fib(35) ≈ 29 millones de llamadas recursivas

=============================================================================
"""

import time
import subprocess
import os
import sys
import textwrap

# =============================================================================
# CÓDIGO C (lenguaje compilado)
# Se escribe a un archivo temporal, se compila y se ejecuta.
# =============================================================================

CODIGO_C = """
/*
 * fibonacci_c.c
 * Implementación recursiva de Fibonacci en C (lenguaje compilado).
 * Compilación: gcc -O0 fibonacci_c.c -o fibonacci_c
 * (Se usa -O0 para desactivar optimizaciones y hacer la comparación justa)
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/**
 * fib: Calcula el n-ésimo número de Fibonacci de forma recursiva.
 * Complejidad temporal: O(2^n)
 * Complejidad espacial: O(n) en la pila de llamadas
 *
 * @param n El índice del número de Fibonacci (n >= 0)
 * @return  El n-ésimo número de Fibonacci
 */
long long fib(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fib(n - 1) + fib(n - 2);
}

int main(int argc, char *argv[]) {
    int n = 35;  /* Valor por defecto */
    if (argc > 1) n = atoi(argv[1]);

    /* Medir tiempo con clock() de alta resolución */
    clock_t inicio = clock();
    long long resultado = fib(n);
    clock_t fin = clock();

    double tiempo_ms = ((double)(fin - inicio) / CLOCKS_PER_SEC) * 1000.0;

    /* Salida en formato CSV para parsear fácilmente desde Python */
    printf("%.4f,%lld\\n", tiempo_ms, resultado);

    return 0;
}
"""

# =============================================================================
# IMPLEMENTACIÓN PYTHON (lenguaje interpretado)
# =============================================================================

def fib_python(n: int) -> int:
    """
    Calcula el n-ésimo número de Fibonacci de forma recursiva.
    
    Esta es una implementación RECURSIVA pura, sin memoización,
    para que sea comparable con la versión en C.

    Complejidad temporal: O(2^n)
    Complejidad espacial: O(n) en la pila de llamadas

    Args:
        n: El índice del número de Fibonacci (n >= 0)

    Returns:
        El n-ésimo número de Fibonacci.
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fib_python(n - 1) + fib_python(n - 2)


# =============================================================================
# FUNCIONES DE MEDICIÓN Y COMPARACIÓN
# =============================================================================

def medir_python(n: int, repeticiones: int = 3) -> tuple[float, int]:
    """
    Ejecuta fib_python(n) varias veces y retorna el tiempo promedio.

    Args:
        n:            Índice de Fibonacci a calcular.
        repeticiones: Número de veces a repetir para promediar.

    Returns:
        Tupla (tiempo_promedio_ms, resultado)
    """
    tiempos = []
    resultado = 0
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = fib_python(n)
        fin = time.perf_counter()
        tiempos.append((fin - inicio) * 1000)  # Convertir a milisegundos
    return sum(tiempos) / len(tiempos), resultado


def compilar_c(ruta_fuente: str, ruta_ejecutable: str) -> bool:
    """
    Compila el código C con gcc.

    Args:
        ruta_fuente:     Ruta al archivo .c
        ruta_ejecutable: Ruta donde se guardará el ejecutable compilado

    Returns:
        True si la compilación fue exitosa, False si hubo error.
    """
    try:
        resultado = subprocess.run(
            ['gcc', '-O0', ruta_fuente, '-o', ruta_ejecutable],
            capture_output=True, text=True, timeout=30
        )
        if resultado.returncode != 0:
            print(f"[ERROR DE COMPILACIÓN]\n{resultado.stderr}")
            return False
        return True
    except FileNotFoundError:
        print("[ERROR] gcc no encontrado. Instalar con: sudo apt-get install gcc")
        return False


def medir_c(ruta_ejecutable: str, n: int, repeticiones: int = 3) -> tuple[float, int]:
    """
    Ejecuta el programa C compilado varias veces y retorna el tiempo promedio.

    Args:
        ruta_ejecutable: Ruta al binario C compilado.
        n:               Índice de Fibonacci a calcular.
        repeticiones:    Número de repeticiones.

    Returns:
        Tupla (tiempo_promedio_ms, resultado)
    """
    tiempos = []
    resultado = 0
    for _ in range(repeticiones):
        proc = subprocess.run(
            [ruta_ejecutable, str(n)],
            capture_output=True, text=True, timeout=60
        )
        if proc.returncode != 0:
            print(f"[ERROR DE EJECUCIÓN C]\n{proc.stderr}")
            return -1.0, -1
        partes = proc.stdout.strip().split(',')
        tiempos.append(float(partes[0]))
        resultado = int(partes[1])
    return sum(tiempos) / len(tiempos), resultado


def imprimir_tabla_resultados(resultados: list[dict]) -> None:
    """
    Imprime una tabla formateada con los resultados de la comparación.

    Args:
        resultados: Lista de diccionarios con los resultados por valor de n.
    """
    print(f"\n{'='*72}")
    print(f"  TABLA COMPARATIVA DE RENDIMIENTO: C (compilado) vs Python (interpretado)")
    print(f"{'='*72}")
    print(f"  {'n':>4} | {'fib(n)':>12} | {'C (ms)':>12} | {'Python (ms)':>12} | {'Factor':>8}")
    print(f"  {'-'*4}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*8}")
    for r in resultados:
        n = r['n']
        fib_val = r['resultado']
        t_c = r.get('tiempo_c', -1)
        t_py = r.get('tiempo_python', -1)
        if t_c > 0 and t_py > 0:
            factor = t_py / t_c
            print(f"  {n:>4} | {fib_val:>12} | {t_c:>12.2f} | {t_py:>12.2f} | {factor:>7.1f}x")
        elif t_py > 0:
            print(f"  {n:>4} | {fib_val:>12} | {'N/A':>12} | {t_py:>12.2f} | {'N/A':>8}")


def imprimir_grafica_ascii(resultados: list[dict]) -> None:
    """
    Imprime una gráfica de barras en ASCII para visualizar los tiempos.

    Args:
        resultados: Lista de diccionarios con los resultados.
    """
    print(f"\n{'='*72}")
    print(f"  GRÁFICA DE TIEMPOS (barras ASCII)")
    print(f"  Escala: cada '█' representa un porcentaje relativo del tiempo máximo")
    print(f"{'='*72}")

    max_tiempo = max(
        max(r.get('tiempo_python', 0), r.get('tiempo_c', 0))
        for r in resultados
    )

    ANCHO_BARRA = 40  # Caracteres máximos de la barra

    for r in resultados:
        n = r['n']
        t_c = r.get('tiempo_c', 0)
        t_py = r.get('tiempo_python', 0)

        if max_tiempo > 0:
            barra_c  = int((t_c  / max_tiempo) * ANCHO_BARRA)
            barra_py = int((t_py / max_tiempo) * ANCHO_BARRA)
        else:
            barra_c = barra_py = 0

        print(f"\n  fib({n}):")
        print(f"    C      ({t_c:7.2f} ms) │{'█' * barra_c}")
        print(f"    Python ({t_py:7.2f} ms) │{'█' * barra_py}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == '__main__':

    print("=" * 72)
    print("  PARCIAL 1 - PUNTO 4")
    print("  Comparación de Rendimiento: Lenguaje Compilado (C) vs Interpretado (Python)")
    print("=" * 72)

    print("""
  CONTEXTO:
  ─────────────────────────────────────────────────────────────────────
  Los lenguajes compilados (como C) traducen el código fuente a código
  máquina ANTES de ejecutarse. Esto permite que el procesador ejecute
  las instrucciones directamente, sin intermediario.

  Los lenguajes interpretados (como Python) ejecutan el código a través
  de un intérprete (la máquina virtual CPython), que lee el bytecode
  en tiempo de ejecución. Esto agrega una capa de abstracción que
  introduce overhead (sobrecarga).

  La función de Fibonacci recursiva es ideal para esta comparación
  porque realiza MILLONES de llamadas a función, amplificando la
  diferencia en el costo de cada invocación.

  fib(35) realiza ~29,860,704 llamadas recursivas.
  ─────────────────────────────────────────────────────────────────────
    """)

    # Valores de n a evaluar
    VALORES_N = [25, 30, 35]
    REPETICIONES = 3

    # Crear y compilar el programa C
    ruta_c_fuente = '/tmp/fibonacci_c.c'
    ruta_c_exec   = '/tmp/fibonacci_c'
    with open(ruta_c_fuente, 'w') as f:
        f.write(CODIGO_C)

    c_disponible = compilar_c(ruta_c_fuente, ruta_c_exec)
    if c_disponible:
        print("  ✅ Código C compilado exitosamente.")
    else:
        print("  ⚠  gcc no disponible. Solo se ejecutará la versión Python.")

    # -------------------------------------------------------------------------
    # EJECUTAR BENCHMARKS
    # -------------------------------------------------------------------------
    print(f"\n  Ejecutando benchmarks (n = {VALORES_N})...")
    print(f"  Cada medición se repite {REPETICIONES} veces y se promedia.\n")

    resultados = []

    for n in VALORES_N:
        print(f"  Calculando fib({n})...")
        entrada = {'n': n}

        # Python
        sys.setrecursionlimit(max(10000, 2**n))
        t_py, resultado_py = medir_python(n, REPETICIONES)
        entrada['tiempo_python'] = t_py
        entrada['resultado'] = resultado_py
        print(f"    Python: fib({n}) = {resultado_py}  (tiempo: {t_py:.2f} ms)")

        # C
        if c_disponible:
            t_c, resultado_c = medir_c(ruta_c_exec, n, REPETICIONES)
            if t_c >= 0:
                entrada['tiempo_c'] = t_c
                print(f"    C:      fib({n}) = {resultado_c}  (tiempo: {t_c:.2f} ms)")
                print(f"    Factor de velocidad: Python es {t_py/t_c:.1f}x más lento que C")

        resultados.append(entrada)

    # -------------------------------------------------------------------------
    # MOSTRAR RESULTADOS
    # -------------------------------------------------------------------------
    imprimir_tabla_resultados(resultados)
    imprimir_grafica_ascii(resultados)

    # -------------------------------------------------------------------------
    # CONCLUSIONES
    # -------------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("  CONCLUSIONES")
    print(f"{'='*72}")

    if c_disponible and all('tiempo_c' in r for r in resultados):
        factores = [r['tiempo_python'] / r['tiempo_c'] for r in resultados]
        factor_promedio = sum(factores) / len(factores)
        print(f"""
  1. C es aproximadamente {factor_promedio:.0f}x más rápido que Python para esta tarea.

  2. ¿Por qué C es más rápido?
     - C se compila a código máquina nativo → instrucciones directas al CPU.
     - Python ejecuta a través del intérprete CPython → overhead por llamada.
     - Cada llamada recursiva en Python crea un frame object en el heap,
       mientras que C usa la pila del sistema (más rápido).
     - Python tiene garbage collection, typing dinámico y boxing de enteros.

  3. ¿Cuándo usar cada uno?
     - C:      Sistemas embebidos, kernels, simulaciones numéricas intensivas,
               donde el rendimiento es crítico.
     - Python: Prototipado rápido, scripts, data science, automatización,
               donde la productividad del desarrollador importa más que la velocidad.

  4. Mitigación en Python:
     - PyPy (JIT compiler): reduce la brecha a ~2-5x.
     - NumPy/Cython: delegan el cómputo a C bajo el capó.
     - Memoización: fib(n) con caché es O(n) en ambos lenguajes.
        """)
    else:
        print("""
  1. Python tiene overhead significativo por ser interpretado.
  2. Instala gcc para ver la comparación completa con C.
     Ubuntu/Debian: sudo apt-get install gcc build-essential
        """)

    # Limpiar archivos temporales
    for f in [ruta_c_fuente, ruta_c_exec]:
        if os.path.exists(f):
            os.remove(f)
