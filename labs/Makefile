# Makefile del laboratorio — Módulo 6
# -----------------------------------------------------------------------------
# Compila los binarios vulnerables en x86 de 32 bits (registro EIP).
#
# Hay dos escenarios según tu host:
#
#  A) Host x86/x86-64 (PC Intel/AMD, Kali x86_64):  usa gcc nativo con -m32.
#       Requiere multilib:   sudo apt install gcc-multilib
#       Targets:  make linux   |   make protegido
#
#  B) Host ARM64 (Mac con Apple Silicon, Kali ARM64):  NO existe gcc-multilib.
#       Se compila con el cross-compiler i686 en ESTÁTICO y se ejecuta bajo QEMU.
#       Requiere:  sudo apt install gcc-i686-linux-gnu qemu-user qemu-user-static binfmt-support
#       Targets:  make cross   |   make cross-protegido
#       Ejecución:  qemu-i386 ./build/vuln_linux <input>   (o directo, vía binfmt)
#
# Limpieza:  make clean
# -----------------------------------------------------------------------------

BUILD = build
SRC   = src

# --- Toolchains ---
CC_NATIVE = gcc
CC_CROSS  = i686-linux-gnu-gcc

# --- Flags ---
# Vulnerable (sin protecciones). En cross añadimos -static para correr bajo qemu
# sin necesidad del loader/libc de 32 bits (que no existe en un host ARM).
VULN_NATIVE = -m32 -fno-stack-protector -no-pie -z execstack -g
VULN_CROSS  =      -fno-stack-protector -no-pie -z execstack -static -g

# Protegido (con canary, para la comparativa defensiva)
HARD_NATIVE = -m32 -fstack-protector-all -no-pie -g
HARD_CROSS  =      -fstack-protector-all -no-pie -static -g

.PHONY: all linux protegido cross cross-protegido clean dirs help

all: help

dirs:
	@mkdir -p $(BUILD)

# ---------- Escenario A: host x86 nativo ----------
linux: dirs
	$(CC_NATIVE) $(VULN_NATIVE) -o $(BUILD)/vuln_linux $(SRC)/vuln_linux.c
	@echo "[+] $(BUILD)/vuln_linux (x86-32 nativo, sin protecciones)"
	@echo "[i] Desactiva ASLR:  echo 0 | sudo tee /proc/sys/kernel/randomize_va_space"

protegido: dirs
	$(CC_NATIVE) $(HARD_NATIVE) -o $(BUILD)/vuln_protegido $(SRC)/vuln_linux.c
	@echo "[+] $(BUILD)/vuln_protegido (con canary) — para la captura de 'stack smashing detected'"

# ---------- Escenario B: host ARM64 / Apple Silicon (cross + QEMU) ----------
cross: dirs
	$(CC_CROSS) $(VULN_CROSS) -o $(BUILD)/vuln_linux $(SRC)/vuln_linux.c
	@echo "[+] $(BUILD)/vuln_linux (x86-32 estático, para QEMU)"
	@echo "[i] Ejecuta:  qemu-i386 ./build/vuln_linux hola"

cross-protegido: dirs
	$(CC_CROSS) $(HARD_CROSS) -o $(BUILD)/vuln_protegido $(SRC)/vuln_linux.c
	@echo "[+] $(BUILD)/vuln_protegido (con canary, estático) — comparativa defensiva"

clean:
	rm -rf $(BUILD)
	@echo "[+] Binarios eliminados."

help:
	@echo "Host x86 nativo :  make linux   |  make protegido"
	@echo "Host ARM64/Mac  :  make cross   |  make cross-protegido   (ejecutar con qemu-i386)"
	@echo "Limpieza        :  make clean"
