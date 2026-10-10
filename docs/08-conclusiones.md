# 8. Conclusiones

Este proyecto nació de una consigna exigente: *no* limitarme a ejecutar exploits públicos, sino
**construir una metodología propia** de análisis de vulnerabilidades y desarrollo de exploits,
y documentarla para que otro analista pueda aprender de ella. Estas son mis conclusiones tras
recorrer ese camino.

---

## 8.1. Lo que he construido

- Una **metodología de 7 fases** (cap. 1), enmarcada en el ciclo de gestión de vulnerabilidades
  y guiada por una mentalidad concreta: entender el *porqué*, pensar en patrones y bajar al
  nivel de la máquina.
- Un mapa de **protecciones modernas** (cap. 2) entendidas no como una lista, sino como barreras
  encadenadas que definen qué técnica de explotación es viable.
- Un **arsenal ordenado por fase** (cap. 3): la herramienta correcta en el momento correcto.
- Un **caso práctico completo y reproducible** (cap. 4 + [`labs/`](../labs/)): del `strcpy`
  vulnerable al control de EIP y la redirección de flujo, con su contraste frente al binario
  protegido.
- El análisis de **cuatro CVEs reales** (cap. 5) que demuestran que, bajo familias muy distintas,
  late el mismo patrón: entrada controlada + validación ausente.
- Un **flujo de investigación de 0days** (cap. 6): el embudo que va de una superficie amplia a
  un fallo entendido en su causa raíz.
- Una vuelta **defensiva** (cap. 7) que conecta todo lo anterior con mi objetivo profesional en
  Blue Team / SOC.

---

## 8.2. Las ideas que me llevo

1. **Un fallo no es una vulnerabilidad, y una vulnerabilidad no es un exploit.** Entre cada
   escalón hay trabajo real: reproducir, entender, sortear protecciones, dar fiabilidad.
2. **La explotación moderna es encadenar soluciones a barreras**, no un truco único. Leak contra
   ASLR, ROP contra DEP, respetar el canary... Cada protección sube el coste del atacante.
3. **El patrón importa más que el caso.** Cuatro CVEs distintas comparten raíz; reconocer esa
   raíz es lo que me preparará para el fallo que aún no existe.
4. **Entender la ofensiva es la mejor defensa.** Saber cómo se construye un exploit es lo que me
   dice qué telemetría buscar y dónde bastionar para que duela.
5. **Documentar es parte del trabajo técnico.** Un hallazgo sin un informe claro y reproducible
   pierde la mitad de su valor.

---

## 8.3. Honestidad sobre mi punto de partida

Empiezo. No tengo todavía un historial de CVEs propias ni decenas de binarios resueltos, y
prefiero decirlo con claridad antes que inflar el trabajo. Lo que sí tengo es un **método
sólido**, un **laboratorio reproducible** construido por mí, y la capacidad de **analizar casos
reales con criterio**. Este repositorio es el punto de partida de un portfolio que pienso hacer
crecer, no un punto final.

---

## 8.4. Próximos pasos (cómo evoluciona esta metodología)

- **Resolver y documentar** retos de pwn/binary exploitation (HTB, TryHackMe, pwnable.kr,
  PortSwigger) con este mismo patrón, ampliando el capítulo 5 con casos propios.
- **Subir de nivel técnico:** ROP real contra DEP, bypass de ASLR con infoleaks, heap
  exploitation, explotación en 64 bits.
- **Profundizar en fuzzing con cobertura** (AFL++/libFuzzer) sobre software open source y
  practicar el *root cause analysis* de los crashes.
- **Cerrar el círculo defensivo:** para cada técnica ofensiva que aprenda, construir su
  detección (Sysmon/EDR/SIEM), mapearla a MITRE ATT&CK y validarla con Atomic Red Team.
- Mantener este repositorio **vivo**: cada caso nuevo es una iteración de la metodología, tal y
  como el propio ciclo predica.

---

> El módulo planteaba que esto *"no es solo un módulo, es una forma de ponerte a prueba"*. Me lo
> he tomado así: más que acumular técnicas, he intentado demostrar que puedo **investigar por mi
> cuenta, sacar conclusiones y documentarlas de forma profesional**. Ese es el analista que
> quiero ser, y este proyecto es la primera evidencia de ello.

➡️ Referencias en [9. Bibliografía y recursos](09-bibliografia.md)
