#!/usr/bin/env python3
"""
extraer_audio.py

Extrae el audio de archivos .mp4 SIN pérdida de calidad (copia el stream
de audio original tal cual, sin recodificar) usando ffmpeg.

Requisitos:
    - Tener ffmpeg instalado y accesible desde la terminal (comando "ffmpeg").
      * Windows: https://ffmpeg.org/download.html (agregarlo al PATH)
      * Mac:     brew install ffmpeg
      * Linux:   sudo apt install ffmpeg

USO BÁSICO (línea de comandos):
    python extraer_audio.py "C:\\ruta\\a\\mi\\carpeta"

    Esto busca todos los .mp4 dentro de esa carpeta (y subcarpetas, si usás
    --recursivo) y guarda el audio extraído en una subcarpeta "audio_extraido".

USO CON VENTANA (selector de carpeta, sin escribir rutas a mano):
    python extraer_audio.py --gui

OPCIONES:
    --recursivo         Busca .mp4 también en subcarpetas.
    --salida RUTA        Carpeta de salida (por defecto: "audio_extraido" dentro
                          de la carpeta de origen).
    --formato EXT        Formato del contenedor de salida: m4a, mp3, wav, original
                          (por defecto: original -> mantiene el codec de audio tal
                          cual venía en el mp4, sin recodificar = sin pérdida).

                          Si elegís mp3 o wav, ffmpeg SÍ tiene que recodificar
                          (esos formatos no son compatibles con audio AAC crudo),
                          así que ahí ya no es 100% "sin pérdida" salvo que uses wav
                          (wav es sin compresión, pero el archivo pesa mucho más).

Ejemplos:
    python extraer_audio.py "./videos"
    python extraer_audio.py "./videos" --recursivo
    python extraer_audio.py "./videos" --formato mp3
    python extraer_audio.py --gui
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def verificar_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: no se encontró 'ffmpeg' en el sistema.")
        print("Instalalo primero:")
        print("  Windows -> https://ffmpeg.org/download.html (agregar al PATH)")
        print("  Mac     -> brew install ffmpeg")
        print("  Linux   -> sudo apt install ffmpeg")
        sys.exit(1)


def obtener_codec_audio(archivo: Path) -> str:
    """Devuelve el nombre del codec de audio del archivo (ej: aac, mp3, ac3)."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name",
        "-of", "csv=p=0",
        str(archivo),
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    return resultado.stdout.strip()


EXTENSION_POR_CODEC = {
    "aac": "m4a",
    "mp3": "mp3",
    "ac3": "ac3",
    "eac3": "eac3",
    "vorbis": "ogg",
    "opus": "opus",
    "flac": "flac",
    "pcm_s16le": "wav",
}


def extraer_audio(archivo: Path, carpeta_salida: Path, formato: str):
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    if formato == "original":
        codec = obtener_codec_audio(archivo)
        extension = EXTENSION_POR_CODEC.get(codec, "m4a")
        salida = carpeta_salida / f"{archivo.stem}.{extension}"
        cmd = [
            "ffmpeg", "-y", "-i", str(archivo),
            "-vn",              # sin video
            "-acodec", "copy",  # copia el audio tal cual, SIN recodificar
            str(salida),
        ]
    else:
        salida = carpeta_salida / f"{archivo.stem}.{formato}"
        cmd = ["ffmpeg", "-y", "-i", str(archivo), "-vn"]
        if formato == "mp3":
            cmd += ["-codec:a", "libmp3lame", "-q:a", "0"]  # mp3 máxima calidad VBR
        elif formato == "wav":
            cmd += ["-codec:a", "pcm_s16le"]  # sin compresión
        else:
            cmd += ["-codec:a", formato]
        cmd.append(str(salida))

    print(f"  -> {archivo.name}  ...", end=" ", flush=True)
    resultado = subprocess.run(cmd, capture_output=True, text=True)

    if resultado.returncode != 0:
        print("FALLÓ")
        print(resultado.stderr[-500:])
    else:
        print(f"OK  ({salida.name})")


def procesar_carpeta(carpeta: Path, salida: Path, recursivo: bool, formato: str):
    patron = "**/*.mp4" if recursivo else "*.mp4"
    archivos = sorted(carpeta.glob(patron))

    if not archivos:
        print(f"No se encontraron archivos .mp4 en: {carpeta}")
        return

    print(f"Encontrados {len(archivos)} archivo(s) .mp4. Extrayendo audio...\n")
    for archivo in archivos:
        extraer_audio(archivo, salida, formato)

    print(f"\nListo. Audio guardado en: {salida.resolve()}")


def modo_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()

    carpeta = filedialog.askdirectory(title="Elegí la carpeta con los videos .mp4")
    if not carpeta:
        return

    carpeta = Path(carpeta)
    salida = carpeta / "audio_extraido"

    try:
        procesar_carpeta(carpeta, salida, recursivo=True, formato="original")
        messagebox.showinfo("Listo", f"Audio extraído en:\n{salida}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    parser = argparse.ArgumentParser(description="Extrae audio de archivos .mp4 sin pérdida de calidad.")
    parser.add_argument("carpeta", nargs="?", help="Carpeta con los archivos .mp4")
    parser.add_argument("--salida", help="Carpeta de salida para el audio extraído")
    parser.add_argument("--recursivo", action="store_true", help="Buscar también en subcarpetas")
    parser.add_argument("--formato", default="original",
                         choices=["original", "mp3", "wav", "m4a"],
                         help="Formato de salida (default: original, sin recodificar)")
    parser.add_argument("--gui", action="store_true", help="Abrir selector de carpeta con ventana")
    args = parser.parse_args()

    verificar_ffmpeg()

    if args.gui:
        modo_gui()
        return

    if not args.carpeta:
        parser.print_help()
        sys.exit(1)

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"ERROR: la carpeta no existe: {carpeta}")
        sys.exit(1)

    salida = Path(args.salida) if args.salida else carpeta / "audio_extraido"
    procesar_carpeta(carpeta, salida, args.recursivo, args.formato)


if __name__ == "__main__":
    main()
