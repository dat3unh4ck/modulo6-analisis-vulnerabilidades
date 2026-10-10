# 📸 Capturas de pantalla

Coloca aquí las capturas que vayas generando al reproducir el laboratorio.
El documento y el README del laboratorio las referencian con estos nombres:

| Archivo | Qué debe mostrar |
|---------|------------------|
| `01-checksec.png` | Salida de `checksec` sobre `vuln_linux` (sin canary, sin PIE, NX off) |
| `02-ejecucion-normal-vs-crash.png` | Ejecución normal y luego el `Segmentation fault` |
| `03-fuzzing.png` | Salida de `fuzzer.py` con el primer CRASH |
| `04-control-eip.png` | **La clave:** GDB mostrando `eip = 0x42424242` |
| `05-ret2win-shell.png` | La shell obtenida tras saltar a `win()` |
| `06-canary-detecta.png` | `*** stack smashing detected ***` en el binario protegido |

> Consejo: recorta las capturas a la zona relevante y, si aparece algún dato del
> sistema, verifica que no expones nada sensible. Un buen set de capturas es lo
> que convierte el write-up en una evidencia convincente en una entrevista técnica.
