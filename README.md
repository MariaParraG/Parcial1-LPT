# Parcial 1 — Lenguajes de Programación

Soluciones a los cinco ejercicios del primer parcial.  
Cada punto está implementado en un archivo independiente con su documentación interna.

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Punto 1 — AFD para movimientos de ajedrez](#punto-1--afd-para-movimientos-de-ajedrez)
- [Punto 2 — AFD para identificadores](#punto-2--afd-para-identificadores)
- [Punto 3 — Calculadora con Flex y Bison](#punto-3--calculadora-con-flex-y-bison)
- [Punto 4 — Comparación de rendimiento](#punto-4--comparación-de-rendimiento)
- [Punto 5 — Fibonacci con ANTLR](#punto-5--fibonacci-con-antlr)

---

## Requisitos

| Herramienta | Versión mínima | Uso |
|---|---|---|
| Python | 3.9+ | Puntos 1, 2, 4, 5 |
| gcc | cualquiera | Puntos 3 y 4 |
| flex | 2.6+ | Punto 3 |
| bison | 3.0+ | Punto 3 |
| Java JRE | 11+ | Punto 5 (ANTLR) |
| antlr4-python3-runtime | 4.13.1 | Punto 5 |

### Instalación rápida (Ubuntu / Debian)

```bash
# Compiladores y herramientas
sudo apt-get install gcc flex bison default-jre

# Runtime de ANTLR para Python
pip install antlr4-python3-runtime==4.13.1
```

---

## Estructura del proyecto

```
parcial1/
├── README.md                          ← Este archivo
│
├── punto1_ajedrez_afd.py              ← Punto 1: AFD movimientos de ajedrez
│
├── punto2_identificadores_afd.py      ← Punto 2: AFD para identificadores
│
├── punto3_calculadora.l               ← Punto 3: Analizador léxico (Flex)
├── punto3_calculadora.y               ← Punto 3: Parser y semántica (Bison)
├── punto3_entrada.txt                 ← Punto 3: Casos de prueba de entrada
│
├── punto4_rendimiento_comparacion.py  ← Punto 4: Benchmark C vs Python
│
├── punto5_Fibonacci.g4                ← Punto 5: Gramática ANTLR4
└── punto5_fibonacci_antlr.py          ← Punto 5: Programa principal Python
```

---

## Punto 1 — AFD para movimientos de ajedrez

**Archivo:** `punto1_ajedrez_afd.py`

### Descripción

Define una expresión regular para el lenguaje de movimientos de ajedrez en notación descriptiva (ej: `p->k4`, `kbp X qn3`) e implementa el AFD correspondiente.

### Expresión regular

```
[pkqrbn]+ (->|X) [pkqrbn]*[1-8]
```

| Parte | Descripción |
|---|---|
| `[pkqrbn]+` | Una o más piezas de origen (peón, rey, reina, torre, alfil, caballo) |
| `(->|X)` | Operador de movimiento (`->`) o captura (`X`) |
| `[pkqrbn]*[1-8]` | Destino: piezas opcionales seguidas del número de fila |

### Estados del AFD

| Estado | Descripción |
|---|---|
| `q0` | Inicial: esperando primer carácter |
| `q1` | Leyendo pieza(s) de origen |
| `q2` | Leído `-` (primer carácter de `->`) |
| `q3` | Leído `->` completo, esperando destino |
| `q4` | Leído `X` (captura), esperando destino |
| `q5` | Leyendo destino |
| `q6` | **Aceptación** |
| `qerr` | Error (trampa) |

### Ejecución

```bash
python punto1_ajedrez_afd.py
```

### Ejemplos de entrada/salida

```
Movimiento: 'p->k4'    → ✅ ACEPTADO
Movimiento: 'kbp X qn3'→ ✅ ACEPTADO
Movimiento: '5->k4'    → ❌ RECHAZADO  (empieza con número)
Movimiento: '->'       → ❌ RECHAZADO  (sin pieza origen)
```

---

## Punto 2 — AFD para identificadores

**Archivo:** `punto2_identificadores_afd.py`

### Descripción

Implementa un AFD para reconocer identificadores válidos según la expresión regular:

```
[A-Za-z][A-Za-z0-9]*
```

El primer carácter debe ser una letra; los siguientes pueden ser letras o dígitos.

### Estados del AFD

| Estado | Descripción |
|---|---|
| `q0` | Inicial: esperando primer carácter |
| `q1` | **Aceptación**: se leyó al menos una letra inicial |
| `qerr` | Error: carácter inválido encontrado |

### Diagrama

```
         letra            letra/dígito
    ──► (q0) ──────────► ((q1)) ◄──┐
          │                         │ letra/dígito
          │ dígito/otro              │
          ▼                         │
        (qerr) ◄─── otro ──────────┘
```

### Ejecución

```bash
python punto2_identificadores_afd.py
```

### Pruebas incluidas

| Cadena | Resultado esperado | Resultado AFD |
|---|---|---|
| `variable` | ✅ ACEPTA | ✅ ACEPTA |
| `MiVariable` | ✅ ACEPTA | ✅ ACEPTA |
| `X1Y2Z3` | ✅ ACEPTA | ✅ ACEPTA |
| `1variable` | ❌ NO ACEPTA | ❌ NO ACEPTA |
| `mi-var` | ❌ NO ACEPTA | ❌ NO ACEPTA |

---

## Punto 3 — Calculadora con Flex y Bison

**Archivos:** `punto3_calculadora.l`, `punto3_calculadora.y`, `punto3_entrada.txt`

### Descripción

Calculadora en C que evalúa expresiones aritméticas y calcula raíces cuadradas de números reales. La raíz cuadrada se implementa con el **método numérico de Newton-Raphson**. La entrada es un archivo de texto y la salida es por consola.

### Método Newton-Raphson

Para calcular √N se itera la fórmula:

```
x₀ = N / 2
x_{n+1} = (x_n + N / x_n) / 2
```

La iteración se detiene cuando `|x_{n+1} - x_n| < 1e-10`.

### Gramática soportada

```
expresion → expresion + termino
          | expresion - termino
          | termino

termino   → termino * factor
          | termino / factor
          | factor

factor    → NUMERO
          | ( expresion )
          | - factor              (negación unaria)
          | sqrt( expresion )     (raíz cuadrada)
```

### Compilación y ejecución

```bash
# 1. Generar el scanner
flex punto3_calculadora.l

# 2. Generar el parser
bison -d punto3_calculadora.y

# 3. Compilar
gcc lex.yy.c calculadora.tab.c -o calculadora -lm

# 4. Ejecutar con archivo de entrada
./calculadora < punto3_entrada.txt
```

> **Nota:** renombrar los archivos quitando el prefijo `punto3_` antes de compilar, o ajustar el `#include` en el `.l`.

### Ejemplo de salida

```
[Newton-Raphson] Calculando sqrt(2):
  Iter   x_n                  x_{n+1}              |error|
  ──────────────────────────────────────────────────────
  1      1.0000000000         1.5000000000         5.00e-01
  2      1.5000000000         1.4166666667         8.33e-02
  ...
  Convergió en 7 iteraciones. sqrt(2) ≈ 1.4142135624

══ Resultado: 1.41421
```

---

## Punto 4 — Comparación de rendimiento

**Archivo:** `punto4_rendimiento_comparacion.py`

### Descripción

Compara el rendimiento entre un **lenguaje compilado (C)** y un **lenguaje interpretado (Python)** usando la función de Fibonacci recursiva como benchmark.

Se eligió Fibonacci recursivo porque tiene complejidad O(2ⁿ) y realiza millones de llamadas a función, lo que amplifica la diferencia de rendimiento entre ambos lenguajes.

### ¿Por qué C es más rápido?

| Factor | C (compilado) | Python (interpretado) |
|---|---|---|
| Ejecución | Código máquina nativo | Bytecode vía CPython |
| Llamadas a función | Directas en la pila del sistema | Crean un `frame object` en el heap |
| Tipos | Estáticos, sin boxing | Dinámicos, con boxing de enteros |
| Memoria | Manual, sin GC | Garbage collector |

### Ejecución

```bash
# Requiere gcc instalado para la parte de C
python punto4_rendimiento_comparacion.py
```

### Salida esperada (aproximada)

```
  n    | fib(n)       | C (ms)       | Python (ms)  | Factor
  ─────┼──────────────┼──────────────┼──────────────┼────────
   25  |       75025  |         3.2  |       180.4  |  56.4x
   30  |      832040  |        34.8  |      2012.1  |  57.8x
   35  |     9227465  |       380.1  |     22350.6  |  58.8x
```

---

## Punto 5 — Fibonacci con ANTLR

**Archivos:** `punto5_Fibonacci.g4`, `punto5_fibonacci_antlr.py`

### Descripción

Programa ANTLR4 con lenguaje objetivo Python que reconoce el comando `FIBO(n)` y calcula la secuencia de Fibonacci.

- **Entrada:** `FIBO(20)` (por consola)
- **Salida:** `0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...` (por consola)

### Gramática ANTLR4 (`Fibonacci.g4`)

```antlr
grammar Fibonacci;

programa : comando EOF ;
comando  : FIBO LPAREN numero RPAREN ;
numero   : NUMERO ;

FIBO    : 'FIBO' ;
NUMERO  : [0-9]+ ;
LPAREN  : '(' ;
RPAREN  : ')' ;
WS      : [ \t\n\r]+ -> skip ;
```

### Instalación de ANTLR

```bash
# 1. Descargar el JAR de ANTLR
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar

# 2. Configurar el classpath
export CLASSPATH=".:antlr-4.13.1-complete.jar:$CLASSPATH"

# 3. Instalar el runtime Python
pip install antlr4-python3-runtime==4.13.1
```

### Generar el parser desde la gramática

```bash
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 punto5_Fibonacci.g4
```

Esto genera:

```
FibonacciLexer.py
FibonacciParser.py
FibonacciListener.py
FibonacciVisitor.py
```

### Ejecución

```bash
python punto5_fibonacci_antlr.py
```

El programa entra en **modo interactivo**. Escribir el comando y presionar Enter:

```
>> FIBO(8)
0, 1, 1, 2, 3, 5, 8, 13

>> FIBO(20)
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181

>> salir
```

> **Nota:** si ANTLR no está instalado, el programa usa un parser manual de respaldo que funciona igualmente.

---

*Parcial 1 — Lenguajes de Programación*
