#!/usr/bin/env python3
"""
find_offset.py — Cálculo del offset exacto que controla EIP (patrón cíclico).
-------------------------------------------------------------------------------
Después de saber *aproximadamente* a qué longitud colapsa el binario (fuzzer.py),
hay que averiguar el offset EXACTO: cuántos bytes hay desde el inicio del búfer
hasta los 4 bytes que caen justo sobre la dirección de retorno (EIP en x86-32).

Técnica: patrón de De Bruijn / "cyclic pattern" (como el pattern_create de
Metasploit o cyclic() de pwntools). Es una cadena en la que cada subsecuencia
de 4 bytes es única. Cuando el binario casca, el valor que haya quedado en EIP
identifica unívocamente su posición dentro del patrón = el offset.

Este script tiene dos modos:

  1) Generar el patrón:
       python3 find_offset.py gen 200

  2) Resolver el offset a partir del valor de EIP capturado en el depurador:
       python3 find_offset.py find 0x6161616b
       python3 find_offset.py find kaaa

Flujo recomendado (con GDB):
  1. patron=$(python3 find_offset.py gen 200)
  2. gdb ./build/vuln_linux
       (gdb) run $patron
       # al cascar, leer EIP:
       (gdb) info registers eip        ->  eip = 0x6161616b  (ejemplo)
  3. python3 find_offset.py find 0x6161616b
       ->  [+] Offset exacto: 72

Si tienes pwntools instalado, internamente puedes validar con:
  cyclic_find(0x6161616b)
-------------------------------------------------------------------------------
"""
import sys
import struct

# Alfabeto y longitudes al estilo pwndbg/pwntools (subsecuencias de 4 únicas).
_ALPHABET = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def de_bruijn(alphabet: bytes = _ALPHABET, n: int = 4):
    """Generador de secuencia de De Bruijn B(k, n)."""
    k = len(alphabet)
    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return bytes(alphabet[i] for i in sequence)


def cyclic(length: int, n: int = 4) -> bytes:
    """Devuelve 'length' bytes de un patrón cíclico con subsecuencias únicas."""
    seq = de_bruijn(n=n)
    if length > len(seq):
        raise ValueError(f"Patron máximo {len(seq)} bytes para n={n}.")
    return seq[:length]


def cyclic_find(value, n: int = 4) -> int:
    """Devuelve el offset de 'value' (int EIP little-endian, o bytes/str) en el patrón."""
    if isinstance(value, int):
        # EIP en x86 es little-endian: 0x6161616b -> b'kaaa'
        subseq = struct.pack("<I", value)
    elif isinstance(value, str):
        subseq = value.encode()
    else:
        subseq = value
    full = de_bruijn(n=n)
    idx = full.find(subseq)
    return idx


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        print("Uso:")
        print("  find_offset.py gen  <longitud>")
        print("  find_offset.py find <eip_hex | subcadena>")
        return 1

    mode = sys.argv[1]

    if mode == "gen":
        length = int(sys.argv[2])
        sys.stdout.write(cyclic(length).decode("latin-1"))
        sys.stdout.write("\n")
        return 0

    if mode == "find":
        arg = sys.argv[2]
        if arg.lower().startswith("0x"):
            value = int(arg, 16)
        elif all(c in "0123456789abcdefABCDEF" for c in arg) and len(arg) == 8:
            value = int(arg, 16)
        else:
            value = arg  # subcadena literal (p.ej. 'kaaa')
        off = cyclic_find(value)
        if off < 0:
            print("[-] No encontrado en el patrón. ¿Seguro que es el valor de EIP?")
            return 2
        print(f"[+] Offset exacto: {off}")
        print(f"[>] Estructura del payload: b'A'*{off} + <4 bytes EIP> + <resto>")
        return 0

    print(f"[-] Modo desconocido: {mode}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
