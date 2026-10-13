# 8. Conclusiones

El encargo era exigente: no quedarme en ejecutar exploits públicos, sino construir
mi propia metodología de análisis de vulnerabilidades y desarrollo de exploits, y
documentarla para que otro pueda aprender de ella. Esto es lo que saco después de
recorrerla.

## 8.1. Lo que he montado

- Una metodología de 7 fases (cap. 1), dentro del ciclo de gestión de
  vulnerabilidades, con una forma de pensar concreta: entender el porqué, pensar
  en patrones y bajar al nivel de la máquina.
- Un mapa de las protecciones modernas (cap. 2), no como lista sino como barreras
  encadenadas que deciden qué técnica de explotación es viable.
- Las herramientas ordenadas por fase (cap. 3): la correcta en el momento
  correcto.
- Un caso práctico completo y reproducible (cap. 4 y [`labs/`](../labs/)): del
  `strcpy` vulnerable al control de EIP y la redirección, con su contraste frente
  al binario protegido.
- El análisis de cuatro CVE reales (cap. 5) que, bajo familias muy distintas,
  comparten la misma raíz: entrada controlada más validación ausente.
- Un flujo de investigación de 0days (cap. 6): el embudo que va de una superficie
  amplia a un fallo entendido en su causa.
- La vuelta defensiva (cap. 7) que conecta todo lo anterior con lo que quiero
  hacer: Blue Team y SOC.

## 8.2. Lo que me llevo

- Un fallo no es una vulnerabilidad, y una vulnerabilidad no es un exploit. Entre
  cada escalón hay trabajo: reproducir, entender, sortear protecciones, dar
  fiabilidad.
- La explotación moderna es ir resolviendo barreras encadenadas, no un truco
  único. Leak contra ASLR, ROP contra DEP, sin romper el canary. Cada protección
  sube el coste.
- El patrón importa más que el caso. Cuatro CVE distintas con la misma raíz;
  reconocer esa raíz es lo que me prepara para el fallo que aún no existe.
- Entender la ofensiva es la mejor defensa. Saber cómo se arma un exploit es lo
  que me dice qué telemetría buscar y dónde bastionar para que duela.
- Documentar es parte del trabajo técnico, no un apéndice. Un hallazgo sin informe
  claro y reproducible pierde la mitad de su valor.

## 8.3. De dónde parto, sin inflarlo

Estoy empezando. No tengo todavía CVE propias ni decenas de binarios resueltos, y
prefiero decirlo claro antes que adornar el trabajo. Lo que sí tengo es un método
sólido, un laboratorio reproducible hecho por mí y la capacidad de analizar casos
reales con criterio. Este repositorio es el punto de partida de un portfolio que
pienso hacer crecer, no el final.

## 8.4. Por dónde sigo

- Resolver y documentar retos de pwn (HTB, TryHackMe, pwnable.kr, PortSwigger) con
  este mismo patrón, ampliando el capítulo 5 con casos míos.
- Subir el nivel técnico: ROP real contra DEP, bypass de ASLR con infoleaks, heap
  exploitation, explotación en 64 bits.
- Profundizar en fuzzing con cobertura (AFL++/libFuzzer) sobre software open source
  y practicar el root cause analysis de los crashes.
- Cerrar el lado defensivo: para cada técnica ofensiva que aprenda, montar su
  detección (Sysmon/EDR/SIEM), mapearla a MITRE ATT&CK y validarla con Atomic Red
  Team.
- Mantener el repositorio vivo: cada caso nuevo es una iteración más de la
  metodología.

En el enunciado había una frase sobre que esto era menos un módulo y más una
forma de ponerte a prueba, y me lo tomé al pie de la letra. Más que acumular
técnicas, lo que he intentado demostrar es que
puedo investigar por mi cuenta, sacar conclusiones y documentarlas bien. Es el
analista que quiero ser, y este proyecto es el primer paso.
