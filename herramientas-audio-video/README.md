# Herramientas de Audio y Video

Scripts en Python para extraer y convertir audio de archivos `.mp4` usando [ffmpeg](https://ffmpeg.org/).

## Requisitos

- Python 3
- [ffmpeg](https://ffmpeg.org/download.html) instalado y accesible desde la terminal
  - **Windows:** descargar de ffmpeg.org y agregarlo al PATH
  - **Mac:** `brew install ffmpeg`
  - **Linux:** `sudo apt install ffmpeg`

## Scripts

### `extraer_audio.py`

Extrae el audio de archivos `.mp4` **sin pérdida de calidad**: copia el stream de audio original tal cual venía (sin recodificar).

```bash
python extraer_audio.py "ruta/a/carpeta" --recursivo
python extraer_audio.py --gui
```

El resultado se guarda en una subcarpeta `audio_extraido`, manteniendo el codec original (normalmente `.m4a`).

### `convertir_a_mp3.py`

Convierte archivos `.mp4` a `.mp3` en alta calidad (VBR máxima), para mejor compatibilidad con reproductores. Al abrirlo sin argumentos, muestra una ventana con selector de carpeta.

```bash
python convertir_a_mp3.py
python convertir_a_mp3.py "ruta/a/carpeta" --recursivo --calidad 0
```

El resultado se guarda en una subcarpeta `mp3_convertido`.

> Nota: al convertir a mp3 se recodifica el audio (mp3 no admite copia directa de AAC), por lo que hay una pérdida mínima de calidad, casi imperceptible con calidad VBR 0.

### `audio_a_mp3.py`

Convierte archivos de audio sueltos `.aac` / `.m4a` (sin video) a `.mp3` en alta calidad. Al abrirlo sin argumentos, muestra una ventana con selector de carpeta.

```bash
python audio_a_mp3.py
python audio_a_mp3.py "ruta/a/carpeta" --recursivo --calidad 0
```

El resultado se guarda en una subcarpeta `mp3_convertido`.

## Notas

- Ambos scripts procesan carpetas completas, no archivos individuales sueltos.
- Usar `--recursivo` para incluir subcarpetas en la búsqueda de `.mp4`.
