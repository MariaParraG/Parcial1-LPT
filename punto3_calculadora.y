/*
=============================================================================
PARCIAL 1 - Punto 3
Lenguajes de Programación
=============================================================================

ARCHIVO: calculadora.y  (Bison - Analizador Sintáctico + Semántico)

DESCRIPCIÓN:
    Este archivo define la gramática y las acciones semánticas de una
    calculadora que evalúa expresiones aritméticas y calcula la raíz cuadrada
    de números reales.

    MÉTODO NEWTON-RAPHSON para √N:
    ─────────────────────────────
    Dado un número N, buscamos x tal que f(x) = x² - N = 0

    Iteración:
        x_{n+1} = x_n - f(x_n)/f'(x_n)
                = x_n - (x_n² - N) / (2·x_n)
                = (x_n + N/x_n) / 2

    Condición de parada: |x_{n+1} - x_n| < ε  (donde ε = 1e-10)

    Ejemplo: √2
      x0 = 2/2 = 1.0
      x1 = (1.0 + 2/1.0) / 2 = 1.5
      x2 = (1.5 + 2/1.5) / 2 ≈ 1.41667
      x3 ≈ 1.41422
      ...converge a 1.41421356...

    GRAMÁTICA (BNF):
    ────────────────
    programa   → programa linea
               | linea

    linea      → expresion NEWLINE
               | NEWLINE

    expresion  → expresion SUMA termino
               | expresion RESTA termino
               | termino

    termino    → termino MULT factor
               | termino DIV factor
               | factor

    factor     → NUMERO
               | LPAREN expresion RPAREN
               | RESTA factor            (negación unaria)
               | SQRT_FUNC LPAREN expresion RPAREN

    COMPILACIÓN:
        flex calculadora.l
        bison -d calculadora.y
        gcc lex.yy.c calculadora.tab.c -o calculadora -lm
        ./calculadora < entrada.txt

=============================================================================
*/

%{
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

/* Prototipo del lexer generado por Flex */
int yylex(void);

/* Función para reportar errores sintácticos */
void yyerror(const char *mensaje);

/* ─────────────────────────────────────────────────────────────────────────
   MÉTODO NUMÉRICO: NEWTON-RAPHSON para raíz cuadrada
   ─────────────────────────────────────────────────────────────────────────
   Calcula √n usando la iteración de Newton-Raphson.

   Parámetros:
     n         - número del que se calcula la raíz (debe ser >= 0)
     tolerancia- criterio de parada (precisión deseada)
     max_iter  - número máximo de iteraciones (para evitar bucle infinito)

   Retorna:
     La raíz cuadrada aproximada de n.
     Retorna -1.0 si n < 0 (número negativo, raíz imaginaria).
*/
double newton_raphson_sqrt(double n, double tolerancia, int max_iter) {
    if (n < 0.0) {
        fprintf(stderr, "[ERROR] No se puede calcular raíz cuadrada de número negativo: %g\n", n);
        return -1.0;
    }
    if (n == 0.0) return 0.0;

    /* Estimación inicial: x0 = n/2 (funciona bien para la mayoría de valores) */
    double x = n / 2.0;
    if (x < 1.0) x = 1.0;  /* Para números < 1, empezar en 1 */

    int iteracion = 0;
    double x_anterior;

    printf("  [Newton-Raphson] Calculando sqrt(%g):\n", n);
    printf("  %-10s %-20s %-20s %-15s\n", "Iter", "x_n", "x_{n+1}", "|error|");
    printf("  %s\n", "─────────────────────────────────────────────────────────");

    do {
        x_anterior = x;
        /* Fórmula de iteración: x_{n+1} = (x_n + n/x_n) / 2 */
        x = (x_anterior + n / x_anterior) / 2.0;
        double error = fabs(x - x_anterior);

        printf("  %-10d %-20.10f %-20.10f %-15.2e\n",
               iteracion + 1, x_anterior, x, error);

        iteracion++;
    } while (fabs(x - x_anterior) > tolerancia && iteracion < max_iter);

    printf("  Convergió en %d iteraciones. sqrt(%g) ≈ %.10f\n\n", iteracion, n, x);
    return x;
}

/* Parámetros del método Newton-Raphson */
#define TOLERANCIA 1e-10
#define MAX_ITER   1000

%}

/* ─────────────────────────────────────────────────────────────────────────
   DECLARACIONES DE TOKENS Y TIPOS
   ───────────────────────────────────────────────────────────────────────── */

/* Tipo semántico de los valores de los tokens */
%union {
    double dval;   /* Valor numérico de punto flotante */
}

/* Declaración de tokens con sus tipos */
%token <dval> NUMERO      /* Número real */
%token        SQRT_FUNC   /* Función sqrt() */
%token        SUMA        /* + */
%token        RESTA       /* - */
%token        MULT        /* * */
%token        DIV         /* / */
%token        LPAREN      /* ( */
%token        RPAREN      /* ) */
%token        NEWLINE     /* \n */

/* Tipo de los no-terminales que producen valores */
%type <dval> expresion termino factor

/* Precedencia y asociatividad de operadores (de menor a mayor precedencia) */
%left  SUMA RESTA
%left  MULT DIV
%right UMINUS   /* Negación unaria: prioridad más alta */

%%

/* ─────────────────────────────────────────────────────────────────────────
   GRAMÁTICA Y ACCIONES SEMÁNTICAS
   ───────────────────────────────────────────────────────────────────────── */

programa:
    programa linea
    | linea
    ;

linea:
    expresion NEWLINE {
        printf("  ══ Resultado: %g\n\n", $1);
    }
    | NEWLINE {
        /* Línea vacía: ignorar */
    }
    | error NEWLINE {
        fprintf(stderr, "[ERROR SINTÁCTICO] Expresión inválida. Se omite la línea.\n\n");
        yyerrok;    /* Recuperación de error */
    }
    ;

expresion:
    expresion SUMA termino {
        $$ = $1 + $3;
        printf("  [Operación] %g + %g = %g\n", $1, $3, $$);
    }
    | expresion RESTA termino {
        $$ = $1 - $3;
        printf("  [Operación] %g - %g = %g\n", $1, $3, $$);
    }
    | termino {
        $$ = $1;
    }
    ;

termino:
    termino MULT factor {
        $$ = $1 * $3;
        printf("  [Operación] %g * %g = %g\n", $1, $3, $$);
    }
    | termino DIV factor {
        if ($3 == 0.0) {
            fprintf(stderr, "[ERROR] División por cero.\n");
            $$ = 0.0;
        } else {
            $$ = $1 / $3;
            printf("  [Operación] %g / %g = %g\n", $1, $3, $$);
        }
    }
    | factor {
        $$ = $1;
    }
    ;

factor:
    NUMERO {
        $$ = $1;
    }
    | LPAREN expresion RPAREN {
        $$ = $2;
    }
    | RESTA factor %prec UMINUS {
        $$ = -$2;
    }
    | SQRT_FUNC LPAREN expresion RPAREN {
        /* Calcular raíz cuadrada usando Newton-Raphson */
        $$ = newton_raphson_sqrt($3, TOLERANCIA, MAX_ITER);
        if ($$ < 0.0) $$ = 0.0;  /* Manejar error: raíz de negativo */
    }
    ;

%%

/* ─────────────────────────────────────────────────────────────────────────
   FUNCIONES AUXILIARES
   ───────────────────────────────────────────────────────────────────────── */

/**
 * yyerror: función requerida por Bison para reportar errores de parseo.
 *
 * @param mensaje Descripción del error encontrado por el parser.
 */
void yyerror(const char *mensaje) {
    fprintf(stderr, "[ERROR DE SINTAXIS] %s\n", mensaje);
}

/**
 * main: Punto de entrada del programa.
 *
 * Lee expresiones desde un archivo de texto (redirigido como stdin),
 * las evalúa y muestra los resultados en consola.
 *
 * Uso: ./calculadora < entrada.txt
 */
int main(void) {
    printf("╔══════════════════════════════════════════════════╗\n");
    printf("║   CALCULADORA CON RAÍZ CUADRADA (Newton-Raphson) ║\n");
    printf("║   Parcial 1 - Punto 3                            ║\n");
    printf("╚══════════════════════════════════════════════════╝\n\n");

    printf("Leyendo expresiones desde stdin (archivo de texto)...\n");
    printf("────────────────────────────────────────────────────\n\n");

    /* Iniciar el análisis sintáctico */
    yyparse();

    printf("────────────────────────────────────────────────────\n");
    printf("Procesamiento completado.\n");

    return 0;
}
