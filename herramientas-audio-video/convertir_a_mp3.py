#!/usr/bin/env python3
"""
convertir_a_mp3.py

Convierte el audio de archivos .mp4 a .mp3 en alta calidad, usando ffmpeg.
Pensado para máxima compatibilidad con reproductores (mp3 es el formato
más universal).

Requisitos:
    - Tener ffmpeg instalado y accesible desde la terminal (comando "ffmpeg").
      * Windows: https://ffmpeg.org/download.html (agregarlo al PATH)
      * Mac:     brew install ffmpeg
      * Linux:   sudo apt install ffmpeg

USO CON VENTANA (recomendado, abre selector de carpeta):
    python convertir_a_mp3.py

    (el modo con ventana es el que se abre por defecto, sin argumentos)

USO POR LÍNEA DE COMANDOS (sin ventana):
    python convertir_a_mp3.py "C:\\ruta\\a\\mi\\carpeta" --recursivo

OPCIONES (modo línea de comandos):
    --recursivo       Busca .mp4 también en subcarpetas.
    --salida RUTA     Carpeta de salida (por defecto: "mp3_convertido" dentro
                      de la carpeta de origen).
    --calidad N       Calidad VBR del mp3, de 0 (mejor) a 9 (peor).
                      Por defecto: 0 (la mejor calidad posible en mp3).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def verificar_ffmpeg():
    if shutil.which("ffmpeg") is None:
        mensaje = (
            "No se encontró 'ffmpeg' en el sistema.\n\n"
            "Instalalo primero:\n"
            "  Windows -> https://ffmpeg.org/download.html (agregar al PATH)\n"
            "  Mac     -> brew install ffmpeg\n"
            "  Linux   -> sudo apt install ffmpeg"
        )
        print(mensaje)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Falta ffmpeg", mensaje)
        except Exception:
            pass
        sys.exit(1)


def convertir_a_mp3(archivo: Path, carpeta_salida: Path, calidad: int, log=print):
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    salida = carpeta_salida / f"{archivo.stem}.mp3"

    cmd = [
        "ffmpeg", "-y", "-i", str(archivo),
        "-vn",                       # sin video
        "-codec:a", "libmp3lame",
        "-q:a", str(calidad),        # 0 = mejor calidad VBR, 9 = peor
        str(salida),
    ]

    log(f"  -> {archivo.name} ...")
    resultado = subprocess.run(cmd, capture_output=True, text=True)

    if resultado.returncode != 0:
        log(f"     FALLÓ: {resultado.stderr[-300:]}")
        return False
    else:
        log(f"     OK ({salida.name})")
        return True


def procesar_carpeta(carpeta: Path, salida: Path, recursivo: bool, calidad: int, log=print):
    patron = "**/*.mp4" if recursivo else "*.mp4"
    archivos = sorted(carpeta.glob(patron))

    if not archivos:
        log(f"No se encontraron archivos .mp4 en: {carpeta}")
        return 0, 0

    log(f"Encontrados {len(archivos)} archivo(s) .mp4. Convirtiendo a mp3...\n")
    exitos = 0
    for archivo in archivos:
        if convertir_a_mp3(archivo, salida, calidad, log):
            exitos += 1

    log(f"\nListo. {exitos}/{len(archivos)} convertidos. Guardado en: {salida.resolve()}")
    return exitos, len(archivos)


def modo_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    root = tk.Tk()
    root.title("Convertir MP4 a MP3")
    root.geometry("520x400")

    carpeta_var = tk.StringVar(value="Ninguna carpeta seleccionada")
    carpeta_elegida = {"ruta": None}

    log_box = scrolledtext.ScrolledText(root, height=15, state="disabled")

    def log(texto):
        log_box.configure(state="normal")
        log_box.insert(tk.END, texto + "\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")
        root.update_idletasks()

    def elegir_carpeta():
        carpeta = filedialog.askdirectory(title="Elegí la carpeta con los videos .mp4")
        if carpeta:
            carpeta_elegida["ruta"] = Path(carpeta)
            carpeta_var.set(carpeta)

    def iniciar_conversion():
        if not carpeta_elegida["ruta"]:
            messagebox.showwarning("Falta carpeta", "Primero elegí una carpeta con videos.")
            return
        carpeta = carpeta_elegida["ruta"]
        salida = carpeta / "mp3_convertido"
        boton_convertir.config(state="disabled")
        log_box.configure(state="normal")
        log_box.delete("1.0", tk.END)
        log_box.configure(state="disabled")

        exitos, total = procesar_carpeta(carpeta, salida, recursivo=True, calidad=0, log=log)
        boton_convertir.config(state="normal")

        if total == 0:
            messagebox.showinfo("Sin archivos", "No se encontraron .mp4 en esa carpeta.")
        else:
            messagebox.showinfo("Listo", f"{exitos}/{total} archivos convertidos.\nGuardado en:\n{salida}")

    tk.Label(root, text="Convertir MP4 a MP3", font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))
    tk.Button(root, text="Elegir carpeta con videos...", command=elegir_carpeta).pack(pady=5)
    tk.Label(root, textvariable=carpeta_var, wraplength=480, fg="gray").pack(pady=(0, 10))
    boton_convertir = tk.Button(root, text="Convertir a MP3", command=iniciar_conversion,
                                 bg="#2e7d32", fg="white", font=("Segoe UI", 10, "bold"))
    boton_convertir.pack(pady=5)
    log_box.pack(fill="both", expand=True, padx=15, pady=15)

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Convierte archivos .mp4 a .mp3.")
    parser.add_argument("carpeta", nargs="?", help="Carpeta con los archivos .mp4 (si se omite, abre ventana)")
    parser.add_argument("--salida", help="Carpeta de salida para los mp3")
    parser.add_argument("--recursivo", action="store_true", help="Buscar también en subcarpetas")
    parser.add_argument("--calidad", type=int, default=0, choices=range(0, 10),
                         help="Calidad VBR del mp3: 0 = mejor, 9 = peor (default: 0)")
    args = parser.parse_args()

    verificar_ffmpeg()

    if not args.carpeta:
        modo_gui()
        return

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"ERROR: la carpeta no existe: {carpeta}")
        sys.exit(1)

    salida = Path(args.salida) if args.salida else carpeta / "mp3_convertido"
    procesar_carpeta(carpeta, salida, args.recursivo, args.calidad)


if __name__ == "__main__":
    main()
