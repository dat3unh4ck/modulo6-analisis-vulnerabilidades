# Capturas de pantalla

Las capturas que fui sacando al reproducir el laboratorio. El documento y el
README del laboratorio las referencian con estos nombres:

| Archivo | Qué muestra |
|---------|-------------|
| `01-checksec.png` | Salida de `checksec` sobre `vuln_linux` (sin canary, sin PIE, NX off) |
| `02-ejecucion-normal-vs-crash.png` | Ejecución normal y, a continuación, el `Segmentation fault` |
| `03-fuzzing.png` | Salida de `fuzzer.py` con el primer CRASH |
| `04-control-eip.png` | GDB con `eip = 0x42424242`, la que resume el trabajo |
| `05-ret2win-shell.png` | La shell que sale tras saltar a `win()` |
| `06-canary-detecta.png` | `*** stack smashing detected ***` en el binario protegido |

Las recorté a la zona relevante y revisé que no quedara ningún dato del sistema a
la vista.
