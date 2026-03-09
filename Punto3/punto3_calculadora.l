/*
===========================================================================
PARCIAL 1 - Punto 3
Lenguajes de Programación
===========================================================================

ARCHIVO: calculadora.l  (Flex - Analizador Léxico)

DESCRIPCIÓN:
    Este archivo define el analizador léxico (scanner) para una calculadora
    que puede evaluar expresiones aritméticas y calcular la raíz cuadrada
    de números reales usando el método numérico de Newton-Raphson.

    El scanner reconoce los siguientes tokens:
    - Números reales (enteros o decimales, incluyendo negativos)
    - Operadores aritméticos: +, -, *, /
    - Paréntesis: (, )
    - La función SQRT() para raíz cuadrada
    - Saltos de línea (para procesar múltiples expresiones)
    - Espacios en blanco (ignorados)

COMPILACIÓN:
    flex calculadora.l        → genera lex.yy.c
    bison -d calculadora.y    → genera calculadora.tab.c y calculadora.tab.h
    gcc lex.yy.c calculadora.tab.c -o calculadora -lm
    ./calculadora < entrada.txt

=============================================================================
*/

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "calculadora.tab.h"   /* Tokens generados por Bison */

/* Contador de líneas para mensajes de error */
int num_linea = 1;
%}

/* Opciones de Flex */
%option noyywrap
%option yylineno

/* Definiciones de patrones */
DIGITO      [0-9]
ENTERO      {DIGITO}+
REAL        {ENTERO}("."{DIGITO}+)?
ESPACIO     [ \t\r]+

%%

    /* -----------------------------------------------------------------------
       REGLAS DE RECONOCIMIENTO DE TOKENS
       ----------------------------------------------------------------------- */

    /* Números reales (enteros y decimales) */
{REAL}          {
                    yylval.dval = atof(yytext);
                    return NUMERO;
                }

    /* Función raíz cuadrada (insensible a mayúsculas/minúsculas) */
[Ss][Qq][Rr][Tt]    { return SQRT_FUNC; }

    /* Operadores aritméticos */
"+"             { return SUMA; }
"-"             { return RESTA; }
"*"             { return MULT; }
"/"             { return DIV; }

    /* Paréntesis */
"("             { return LPAREN; }
")"             { return RPAREN; }

    /* Salto de línea: señal para evaluar la expresión */
"\n"            {
                    num_linea++;
                    return NEWLINE;
                }

    /* Espacios en blanco: ignorados */
{ESPACIO}       { /* ignorar */ }

    /* Fin de archivo */
<<EOF>>         { return 0; }

    /* Cualquier otro carácter: error léxico */
.               {
                    fprintf(stderr,
                        "[ERROR LÉXICO] Línea %d: carácter desconocido '%s'\n",
                        num_linea, yytext);
                }

%%
