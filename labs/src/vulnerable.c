/*
 * vulnerable.c
 * ----------------------------------------------------------------------------
 * Versión DELIBERADAMENTE VULNERABLE (fiel al manual del Módulo 6).
 *
 * Fallo: Stack-Based Buffer Overflow.
 *   La función vulnerable_function() copia la entrada del usuario en un búfer
 *   fijo de la pila con strcpy(), SIN comprobar la longitud. Si la entrada
 *   supera el tamaño del búfer, se sobrescriben datos adyacentes de la pila:
 *   el marco guardado (saved EBP) y, sobre todo, la DIRECCIÓN DE RETORNO,
 *   lo que permite redirigir el flujo de ejecución.
 *
 * Compilación (Windows / MinGW), tal como indica el manual:
 *   # 32 bits, pila ejecutable y sin stack cookies
 *   gcc -m32 -fno-stack-protector -z execstack -o vulnerable.exe vulnerable.c
 *
 * ADVERTENCIA: código educativo. Compilar y ejecutar SOLO en un laboratorio
 * aislado. No usar en producción.
 * ----------------------------------------------------------------------------
 */

#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[1000];
    strcpy(buffer, input);   // No hay verificación de tamaño -> Stack BOF
    printf("Has introducido: %s\n", buffer);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <input>\n", argv[0]);
        return 1;
    }
    vulnerable_function(argv[1]);
    printf("Programa finalizado correctamente.\n");
    return 0;
}
