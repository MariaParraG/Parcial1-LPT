# Punto 3 — Calculadora con Flex y Bison

## Descripción

Calculadora que evalúa expresiones aritméticas y calcula raíces cuadradas de números reales usando el **método de Newton-Raphson**.

## Archivos

| Archivo | Descripción |
|---|---|
| `punto3_calculadora.l` | Analizador léxico (Flex) |
| `punto3_calculadora.y` | Analizador sintáctico y semántico (Bison) |
| `punto3_entrada.txt` | Archivo de expresiones de prueba |

## Método Newton-Raphson

Para calcular √N, se itera:

```
x_{n+1} = (x_n + N / x_n) / 2
```

La condición de parada es `|x_{n+1} - x_n| < 1e-10`.

## Tokens reconocidos

| Token | Descripción |
|---|---|
| `NUMERO` | Número real (ej: `3.14`, `100`) |
| `SQRT_FUNC` | Palabra clave `sqrt` (case-insensitive) |
| `+` `-` `*` `/` | Operadores aritméticos |
| `(` `)` | Paréntesis |

## Gramática (simplificada)

```
expresion → expresion + termino
          | expresion - termino
          | termino

termino   → termino * factor
          | termino / factor
          | factor

factor    → NUMERO
          | ( expresion )
          | - factor
          | sqrt( expresion )
```

## Compilación y ejecución

```bash
# 1. Instalar dependencias (Ubuntu/Debian)
sudo apt-get install flex bison gcc

# 2. Renombrar archivos sin el prefijo "punto3_"
cp punto3_calculadora.l calculadora.l
cp punto3_calculadora.y calculadora.y
cp punto3_entrada.txt entrada.txt

# 3. Generar el scanner con Flex
flex calculadora.l
# → Genera: lex.yy.c

# 4. Generar el parser con Bison
bison -d calculadora.y
# → Genera: calculadora.tab.c  y  calculadora.tab.h

# 5. Compilar todo junto
gcc lex.yy.c calculadora.tab.c -o calculadora -lm

# 6. Ejecutar con el archivo de entrada
./calculadora < entrada.txt
```

## Ejemplo de salida esperada

```
╔══════════════════════════════════════════════════╗
║   CALCULADORA CON RAÍZ CUADRADA (Newton-Raphson) ║
╚══════════════════════════════════════════════════╝

  [Newton-Raphson] Calculando sqrt(2):
  Iter       x_n                  x_{n+1}              |error|
  ─────────────────────────────────────────────────────────────
  1          1.0000000000         1.5000000000         5.00e-01
  2          1.5000000000         1.4166666667         8.33e-02
  3          1.4166666667         1.4142156863         2.45e-03
  ...
  Convergió en 7 iteraciones. sqrt(2) ≈ 1.4142135624

  ══ Resultado: 1.41421
```
