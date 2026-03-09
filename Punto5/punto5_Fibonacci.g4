/*
 * ==========================================================================
 * PARCIAL 1 - Punto 5
 * Lenguajes de Programación
 * ==========================================================================
 *
 * ARCHIVO: Fibonacci.g4
 * Gramática ANTLR4 para reconocer y evaluar el comando FIBO(n)
 *
 * DESCRIPCIÓN:
 *   Esta gramática define el lenguaje de un solo comando: FIBO(n), donde n
 *   es un número entero no negativo. El programa calcula e imprime los
 *   primeros n términos de la secuencia de Fibonacci.
 *
 * CÓMO USAR:
 *   1. Generar el parser en Python:
 *      java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 Fibonacci.g4
 *
 *   2. Esto genera:
 *      - FibonacciLexer.py
 *      - FibonacciParser.py
 *      - FibonacciListener.py
 *      - FibonacciVisitor.py
 *
 *   3. Ejecutar el programa:
 *      python punto5_fibonacci_antlr.py
 *
 * EJEMPLO:
 *   Entrada: FIBO(8)
 *   Salida:  0, 1, 1, 2, 3, 5, 8, 13
 *
 *   Entrada: FIBO(20)
 *   Salida:  0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377,
 *            610, 987, 1597, 2584, 4181
 * ==========================================================================
 */

grammar Fibonacci;

// ─── REGLAS DEL PARSER ──────────────────────────────────────────────────────

/**
 * programa: Regla raíz del parser.
 * Un programa válido consiste en exactamente un comando FIBO seguido de EOF.
 * El EOF garantiza que no haya tokens extra al final.
 */
programa
    : comando EOF
    ;

/**
 * comando: La instrucción FIBO(n).
 * Reconoce la palabra clave FIBO seguida de un número entre paréntesis.
 * El número indica cuántos términos de la secuencia se deben calcular.
 *
 * Ejemplos válidos: FIBO(0), FIBO(1), FIBO(20), FIBO(100)
 */
comando
    : FIBO LPAREN numero RPAREN
    ;

/**
 * numero: El argumento numérico de FIBO.
 * Se define como regla separada para poder acceder a él fácilmente
 * desde el Visitor/Listener con: ctx.numero().NUMERO().getText()
 */
numero
    : NUMERO
    ;


// ─── REGLAS DEL LEXER (TOKENS) ──────────────────────────────────────────────

/**
 * FIBO: Palabra clave reservada que identifica la función.
 * Solo se acepta en mayúsculas para ser consistente con el enunciado.
 */
FIBO    : 'FIBO' ;

/**
 * NUMERO: Uno o más dígitos decimales.
 * Representa un número entero no negativo.
 */
NUMERO  : [0-9]+ ;

/**
 * LPAREN, RPAREN: Paréntesis de apertura y cierre.
 */
LPAREN  : '(' ;
RPAREN  : ')' ;

/**
 * WS: Espacios en blanco.
 * Se usan -> skip para que el lexer los ignore automáticamente.
 * Esto permite entrada con espacios: FIBO( 20 ) o FIBO (20)
 */
WS      : [ \t\n\r]+ -> skip ;
