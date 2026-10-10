/*
 * vuln_linux.c
 * ----------------------------------------------------------------------------
 * Versión adaptada a Linux del Stack Buffer Overflow del manual, pensada para
 * practicar el ciclo completo (fuzzing -> crash -> offset -> control de EIP ->
 * exploit) de forma rápida y limpia con GDB/pwntools.
 *
 * Diferencias intencionadas respecto a vulnerable.c:
 *   - Búfer más pequeño (64 bytes) para alcanzar la dirección de retorno con
 *     entradas cortas y ver el control de EIP sin manejar miles de bytes.
 *   - Incluye una función oculta win() que NUNCA se llama desde el flujo normal.
 *     El objetivo didáctico (ret2win) es sobrescribir la dirección de retorno
 *     para saltar a win(): demuestra control de flujo real sin inyectar
 *     shellcode, de forma 100% reproducible y segura.
 *
 * Compilación (32 bits, sin protecciones, para el laboratorio):
 *   gcc -m32 -fno-stack-protector -no-pie -z execstack -o vuln_linux vuln_linux.c
 *
 *   -m32                -> binario de 32 bits (registro de instrucción = EIP)
 *   -fno-stack-protector-> desactiva stack canaries
 *   -no-pie             -> direcciones fijas (facilita ret2win sin fugas)
 *   -z execstack        -> pila ejecutable (necesario solo para la vía shellcode)
 *
 * ADVERTENCIA: código educativo. Laboratorio aislado únicamente.
 * ----------------------------------------------------------------------------
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

/* Función "objetivo": no se invoca nunca en el flujo legítimo del programa.
 * El reto consiste en desviar la ejecución hasta aquí sobrescribiendo la
 * dirección de retorno guardada en la pila. */
void win(void) {
    printf("\n[+] win() alcanzada: control de flujo conseguido.\n");
    printf("[+] En un escenario real, aqui iria la carga util (shell, RCE...).\n");
    /* Demostración inofensiva de impacto en un entorno controlado: */
    system("/bin/sh");
}

void vulnerable_function(char *input) {
    char buffer[64];
    strcpy(buffer, input);   // Sin control de tamaño -> Stack BOF
    printf("Has introducido: %s\n", buffer);
}

int main(int argc, char *argv[]) {
    /* Pista didáctica: imprime la dirección de win() para el ejercicio ret2win.
     * (En un binario real no tendríamos este regalo; ahí entran los infoleaks). */
    printf("[i] Direccion de win(): %p\n", (void *) &win);

    if (argc != 2) {
        printf("Uso: %s <input>\n", argv[0]);
        return 1;
    }
    vulnerable_function(argv[1]);
    printf("Programa finalizado correctamente.\n");
    return 0;
}
