/*
 * corregido.c
 * ----------------------------------------------------------------------------
 * Versión CORREGIDA del mismo programa (fiel al manual del Módulo 6).
 *
 * Mitigación: se sustituye strcpy() por strcpy_s(), una función segura que
 *   recibe el tamaño del búfer destino y aborta la copia si la entrada no cabe,
 *   evitando el desbordamiento. Un cambio mínimo en el código fuente que, a
 *   nivel de ensamblador, introduce la comprobación de límites que mitiga la
 *   vulnerabilidad.
 *
 * NOTA: strcpy_s() forma parte de las "Annex K / bounds-checking interfaces"
 *   del estándar C11 y está disponible en el toolchain de MinGW/MSVC (Windows),
 *   que es el entorno que usa el manual. En glibc (Linux) no suele estar
 *   disponible: para la práctica en Linux, usa src/vuln_linux.c, donde el
 *   patrón equivalente es snprintf()/strncpy() con tamaño explícito.
 *
 * Compilación (Windows / MinGW), tal como indica el manual:
 *   # 32 bits
 *   gcc -m32 -o corregido.exe corregido.c
 * ----------------------------------------------------------------------------
 */

#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[1000];
    // Uso de función segura
    if (strcpy_s(buffer, sizeof(buffer), input) != 0) {
        printf("Error copiando los datos de entrada.\n");
        return;
    }
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
