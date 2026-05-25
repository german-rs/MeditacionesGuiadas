import os
import subprocess

# ── Rutas ───────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))

VOZ_MEDITACION  = os.path.join(BASE_DIR, "meditacion_gemini_gen_Enceladus.mp3")
MUSICA_FONDO    = os.path.join(BASE_DIR, "528hz-meditation.mp3")
SALIDA          = os.path.join(BASE_DIR, "meditacion_fusionada.mp3")

# ── Configuración de mezcla ──────────────────────────────────────────────────
# Volumen relativo de cada pista (1.0 = original, 0.3 = 30%)
VOLUMEN_VOZ     = 1.0   # La voz guiada va al 100% — debe escucharse con claridad
VOLUMEN_MUSICA  = 0.25  # La música 528hz va suave, como fondo


def fusionar_audios(voz: str, musica: str, salida: str) -> str:
    """
    Fusiona la voz de meditación con la música de fondo.

    - La voz va al volumen completo.
    - La música va reducida para no tapar la voz.
    - La duración final sigue a la pista más larga (la voz, normalmente).
    - Si la música es más corta que la voz, se repite en loop automáticamente.
    """

    for archivo in [voz, musica]:
        if not os.path.exists(archivo):
            raise FileNotFoundError(f"❌ No se encontró el archivo: {archivo}")

    print("🎵 Fusionando audios:")
    print(f"   🎙  Voz    → {voz}")
    print(f"   🎶  Música → {musica}")
    print(f"   💾  Salida → {salida}")

    resultado = subprocess.run(
        [
            "ffmpeg", "-y",

            # Entrada 1: voz de meditación
            "-i", voz,

            # Entrada 2: música de fondo en loop
            # (si la música es más corta que la voz, se repite automáticamente)
            "-stream_loop", "-1", "-i", musica,

            "-filter_complex",
            (
                # Ajustar volumen de cada pista por separado
                f"[0:a]volume={VOLUMEN_VOZ}[voz];"
                f"[1:a]volume={VOLUMEN_MUSICA}[musica];"
                # Mezclar ambas pistas; duración = la más corta entre voz y loop
                # Se usa 'first' para que termine cuando termine la voz
                "[voz][musica]amix=inputs=2:duration=first:normalize=0[out]"
            ),

            "-map", "[out]",
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",          # Calidad alta (2 = ~190 kbps VBR)
            salida
        ],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"❌ Error en ffmpeg:\n{resultado.stderr}")

    # Calcular duración del archivo resultante
    duracion = obtener_duracion(salida)
    print(f"✅ Fusión completada: {salida}")
    if duracion:
        mins = int(duracion // 60)
        segs = int(duracion % 60)
        print(f"⏱  Duración total: {mins} min {segs} seg")

    return salida


def obtener_duracion(archivo: str) -> float | None:
    """Obtiene la duración en segundos de un archivo de audio via ffprobe."""
    try:
        resultado = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                archivo
            ],
            capture_output=True,
            text=True
        )
        return float(resultado.stdout.strip())
    except Exception:
        return None


if __name__ == "__main__":
    fusionar_audios(VOZ_MEDITACION, MUSICA_FONDO, SALIDA)