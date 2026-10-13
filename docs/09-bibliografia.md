# 9. Bibliografía y recursos

Fuentes en las que me he apoyado. Las que vienen del manual del Módulo 6 van
marcadas con (M6).

## 9.1. Libros

- (M6) Benjamin Strout — *The Vulnerability Researcher's Handbook*. Packt.
- (M6) Jon Erickson — *Hacking: The Art of Exploitation*. No Starch Press.
- (M6) Bruce Dang, Alexandre Gazet, Elias Bachaalany & Sébastien Josse —
  *Practical Reverse Engineering*. Wiley.
- (M6) Andreas Zeller, Rahul Gopinath, Marcel Böhme, Gordon Fraser & Christian
  Holler — *The Fuzzing Book*. https://www.fuzzingbook.org/
- Tobias Klein — *A Bug Hunter's Diary*. No Starch Press.
- Dennis Andriesse — *Practical Binary Analysis*. No Starch Press.

## 9.2. Estándares, taxonomías y bases de datos

- NVD — National Vulnerability Database: https://nvd.nist.gov/
- MITRE CVE: https://www.cve.org/
- MITRE CWE: https://cwe.mitre.org/
- MITRE ATT&CK: https://attack.mitre.org/
- CVSS: https://www.first.org/cvss/
- Exploit-DB: https://www.exploit-db.com/
- OWASP Top 10: https://owasp.org/www-project-top-ten/

## 9.3. CVE del capítulo 5

- CVE-2014-0160 (Heartbleed): https://nvd.nist.gov/vuln/detail/CVE-2014-0160 · https://heartbleed.com/
- CVE-2017-0144 (EternalBlue): https://nvd.nist.gov/vuln/detail/CVE-2017-0144 · https://learn.microsoft.com/security-updates/securitybulletins/2017/ms17-010
- CVE-2021-3156 (Baron Samedit): https://nvd.nist.gov/vuln/detail/CVE-2021-3156 · https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
- CVE-2021-44228 (Log4Shell): https://nvd.nist.gov/vuln/detail/CVE-2021-44228

## 9.4. Herramientas (documentación oficial)

Reconocimiento y escaneo: [Nmap](https://nmap.org/) · [Masscan](https://github.com/robertdavidgraham/masscan) ·
[RustScan](https://github.com/RustScan/RustScan) · [Amass](https://github.com/owasp-amass/amass) ·
[Nessus](https://www.tenable.com/products/nessus) · [OpenVAS/Greenbone](https://www.greenbone.net/) ·
[Nuclei](https://github.com/projectdiscovery/nuclei)

Fuzzing: [AFL++](https://github.com/AFLplusplus/AFLplusplus) · [libFuzzer](https://llvm.org/docs/LibFuzzer.html) ·
[boofuzz](https://github.com/jtpereyda/boofuzz) · [Radamsa](https://gitlab.com/akihe/radamsa)

Reversing y depuración: [Ghidra](https://ghidra-sre.org/) · [Cutter](https://cutter.re/) ·
[x64dbg](https://x64dbg.com/) · [GDB](https://www.sourceware.org/gdb/) ·
[GEF](https://github.com/hugsy/gef) · [pwndbg](https://github.com/pwndbg/pwndbg)

Diffing: [BinDiff](https://github.com/google/bindiff) · [Diaphora](https://github.com/joxeankoret/diaphora)

Explotación y payloads: [Metasploit](https://www.metasploit.com/) ·
[pwntools](https://github.com/Gallopsled/pwntools) · [ROPgadget](https://github.com/JonathanSalwan/ROPgadget)

BAS y simulación: [MITRE Caldera](https://caldera.mitre.org/) ·
[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)

Reporting: [PwnDoc](https://github.com/pwndoc/pwndoc) · [Faction](https://github.com/factionsecurity/faction)

## 9.5. Práctica

- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — gratis.
- [TryHackMe](https://tryhackme.com/) · [Hack The Box](https://www.hackthebox.com/)
- [pwnable.kr](http://pwnable.kr/) · [pwnable.tw](https://pwnable.tw/) — binary exploitation.
- [pwn.college](https://pwn.college/) — currículo abierto de explotación.
- [Nightmare (guyinatuxedo)](https://guyinatuxedo.github.io/) — introducción a pwn/CTF.
- [Exploit Education](https://exploit.education/) — máquinas vulnerables graduadas.

## 9.6. Clásicos

- Aleph One — *Smashing the Stack for Fun and Profit*. Phrack 49 (1996).
  http://phrack.org/issues/49/14.html
- Nergal — *The advanced return-into-lib(c) exploits*. Phrack 58 (2001).
- c0ntex — *Bypassing non-executable-stack during exploitation (ret2libc)*.
- Matt Miller (Microsoft) — publicaciones sobre mitigaciones de exploits en Windows.

Cada afirmación técnica de este documento se puede contrastar con estas
referencias. He tirado sobre todo de fuentes primarias —NVD, avisos de
fabricantes, documentación oficial— y he intentado separar lo que es conocimiento
establecido de lo que es mi interpretación o mi práctica.
