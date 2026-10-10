#!/usr/bin/env python3
"""
fuzzer.py — Fuzzer básico para el binario vulnerable del laboratorio.
-------------------------------------------------------------------------------
Idea (fase 1 de la metodología, "identificación del fallo"): enviar al binario
cadenas cada vez más largas y detectar a partir de qué longitud deja de
comportarse de forma normal y COLAPSA (crash). Ese umbral marca el inicio del
análisis: confirma que la entrada del usuario puede corromper la memoria.

Aunque el ejemplo es simple, la lógica es la misma que la de un fuzzer serio:
generar entradas, ejecutarlas, observar el comportamiento y registrar el punto
de fallo. Para binarios complejos se usarían AFL++, boofuzz o Radamsa.

Uso:
    python3 fuzzer.py ./build/vuln_linux
    python3 fuzzer.py ./build/vuln_linux --start 50 --step 50 --max 2000

Interpretación:
    - "OK"    -> el binario terminó normalmente (código de salida 0).
    - "CRASH" -> el binario murió por señal (p.ej. SIGSEGV = 139). ¡Fallo!
-------------------------------------------------------------------------------
"""
import argparse
import subprocess
import sys


def run_once(binary: str, length: int) -> int:
    """Ejecuta el binario con una entrada de 'length' bytes ('A'*length).
    Devuelve el returncode (negativo o >128 indica muerte por señal)."""
    payload = b"A" * length
    try:
        proc = subprocess.run(
            [binary, payload.decode("latin-1")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        return -999  # cuelgue: también es un comportamiento anómalo


def is_crash(rc: int) -> bool:
    # En Linux, morir por señal -> returncode negativo (subprocess) o 128+N.
    return rc < 0 or rc >= 128


def main() -> int:
    ap = argparse.ArgumentParser(description="Fuzzer de longitud creciente.")
    ap.add_argument("binary", help="Ruta al binario vulnerable (p.ej. ./build/vuln_linux)")
    ap.add_argument("--start", type=int, default=50, help="Longitud inicial")
    ap.add_argument("--step", type=int, default=50, help="Incremento por iteración")
    ap.add_argument("--max", type=int, default=2000, help="Longitud máxima")
    args = ap.parse_args()

    print(f"[*] Fuzzing {args.binary} desde {args.start} hasta {args.max} "
          f"bytes (paso {args.step})\n")

    first_crash = None
    length = args.start
    while length <= args.max:
        rc = run_once(args.binary, length)
        if is_crash(rc):
            estado = f"CRASH (rc={rc})"
            if first_crash is None:
                first_crash = length
        else:
            estado = f"OK (rc={rc})"
        print(f"[{'!' if is_crash(rc) else '+'}] len={length:<5} -> {estado}")
        length += args.step

    print()
    if first_crash is not None:
        print(f"[+] Primer CRASH observado alrededor de {first_crash} bytes.")
        print(f"[>] Siguiente paso: afinar con find_offset.py para localizar "
              f"el offset exacto que sobrescribe EIP.")
    else:
        print("[-] No se observaron crashes en el rango probado. "
              "Prueba a aumentar --max.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
