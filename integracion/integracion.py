import os
import subprocess

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ARCHIVO_1 = os.path.join(BASE_DIR, "frecuencias", "528hz-meditation.mp3")
ARCHIVO_2 = os.path.join(BASE_DIR, "sonidos", "deep-relaxing-music.mp3")
SALIDA    = os.path.join(BASE_DIR, "integracion", "meditacion_integrada.mp3")


def unir_audios(archivo_1: str, archivo_2: str, salida: str) -> str:
    """Une dos archivos MP3 mezclándolos en paralelo con ffmpeg."""

    # Verificar que los archivos existen
    for archivo in [archivo_1, archivo_2]:
        if not os.path.exists(archivo):
            raise FileNotFoundError(f"❌ No se encontró el archivo: {archivo}")

    print(f"🎵 Mezclando audios:")
    print(f"   → {archivo_1}")
    print(f"   → {archivo_2}")

    resultado = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", archivo_1,
            "-i", archivo_2,
            "-filter_complex", "amix=inputs=2:duration=longest:normalize=0",
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",
            salida
        ],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"❌ Error en ffmpeg:\n{resultado.stderr}")

    print(f"✅ Audio integrado guardado en: {salida}")
    return salida


if __name__ == "__main__":
    unir_audios(ARCHIVO_1, ARCHIVO_2, SALIDA)