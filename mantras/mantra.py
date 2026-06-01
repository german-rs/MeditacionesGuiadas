import os
import base64
import requests
import wave
import subprocess
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv

# ── Cargar variables de entorno ───────────────────────────────────────────────
load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not os.path.isabs(credentials_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(project_root, credentials_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# ── Voces disponibles ─────────────────────────────────────────────────────────
VOCES = {
    "Masculinas": [
        "Algenib",
        "Algieba",
        "Charon",
        "Enceladus",
        "Iapetus",
        "Sadaltager",
    ],
    "Femeninas": [
        "Gacrux",
        "Kore",
        "Sulafat",
        "Zephyr",
    ],
}

# ── SSML: ~5 minutos de Daimoku ───────────────────────────────────────────────
#
# Estructura:
#   - Introducción breve en silencio (1 respiración)
#   - Fase 1: Arranque lento y solemne (~40 rep, ~1:15 min)
#   - Fase 2: Ritmo constante y fluido (~90 rep, ~2:00 min)
#   - Fase 3: Ritmo más íntimo, bajando el volumen (~60 rep, ~1:15 min)
#   - Cierre: últimas repeticiones muy suaves hasta silencio (~15 rep, ~30 seg)
#
# Pronunciación objetivo: "Nam · myo · ho · ren · gue · kyo"
# Se usa guiones en el texto para forzar separación de sílabas en el motor TTS.
# La palabra "Nam-myoho-renge-kyo" se escribe con separaciones leves para
# que el modelo no la interprete como una sola palabra desconocida.
# ─────────────────────────────────────────────────────────────────────────────

def _rep(n: int, break_ms: int = 700) -> str:
    """Genera n repeticiones de la frase con una pausa entre cada una."""
    frase = "Nam myo ho ren gue kyo"
    pausa = f'<break time="{break_ms}ms"/>'
    return (frase + pausa + "\n") * n


DAIMOKU_SSML = f"""
<speak>

  <!-- Silencio inicial: aterriza al oyente -->
  <break time="3000ms"/>

  <!-- ───────────────────────────────────────────────
       FASE 1 — Arranque: lento y solemne (~1:15 min)
       ritmo: ~1 rep cada 1.8 s  →  40 rep ≈ 72 s
  ─────────────────────────────────────────────────── -->
  <prosody rate="78%" pitch="-2st" volume="soft">
    {_rep(5, break_ms=1100)}
  </prosody>

  <prosody rate="82%" pitch="-2st" volume="soft">
    {_rep(10, break_ms=950)}
  </prosody>

  <prosody rate="86%" pitch="-1st" volume="medium">
    {_rep(12, break_ms=850)}
  </prosody>

  <prosody rate="90%" pitch="-1st" volume="medium">
    {_rep(13, break_ms=750)}
  </prosody>

  <!-- ───────────────────────────────────────────────
       FASE 2 — Cuerpo: ritmo constante y fluido (~2:00 min)
       ritmo: ~1 rep cada 1.3 s  →  90 rep ≈ 117 s
  ─────────────────────────────────────────────────── -->
  <prosody rate="92%" pitch="0st" volume="medium">
    {_rep(30, break_ms=680)}
  </prosody>

  <prosody rate="94%" pitch="0st" volume="medium">
    {_rep(30, break_ms=650)}
  </prosody>

  <prosody rate="92%" pitch="-1st" volume="medium">
    {_rep(30, break_ms=680)}
  </prosody>

  <!-- ───────────────────────────────────────────────
       FASE 3 — Recogimiento: más íntimo, baja el volumen (~1:15 min)
       ritmo: ~1 rep cada 1.5 s  →  60 rep ≈ 90 s
  ─────────────────────────────────────────────────── -->
  <prosody rate="88%" pitch="-1st" volume="soft">
    {_rep(20, break_ms=800)}
  </prosody>

  <prosody rate="84%" pitch="-2st" volume="soft">
    {_rep(20, break_ms=900)}
  </prosody>

  <prosody rate="80%" pitch="-2st" volume="x-soft">
    {_rep(20, break_ms=1000)}
  </prosody>

  <!-- ───────────────────────────────────────────────
       CIERRE — Últimas repeticiones, fundido a silencio (~30 seg)
  ─────────────────────────────────────────────────── -->
  <prosody rate="76%" pitch="-3st" volume="x-soft">
    {_rep(8, break_ms=1200)}
  </prosody>

  <prosody rate="72%" pitch="-3st" volume="x-soft">
    {_rep(4, break_ms=1500)}
  </prosody>

  <prosody rate="68%" pitch="-4st" volume="x-soft">
    {_rep(2, break_ms=2000)}
  </prosody>

  <!-- Silencio final -->
  <break time="4000ms"/>

</speak>
"""


# ── Selección de voz en consola ───────────────────────────────────────────────
def seleccionar_voz() -> str:
    todas_las_voces = []

    print("\n" + "─" * 45)
    print("  🎙️  Selección de voz")
    print("─" * 45)

    indice = 1
    for genero, voces in VOCES.items():
        print(f"\n  {genero}:")
        for voz in voces:
            print(f"    [{indice}] {voz}")
            todas_las_voces.append(voz)
            indice += 1

    print("\n  [0] Generar TODAS las voces")
    print("─" * 45)

    while True:
        try:
            seleccion = input(f"  Elige una voz [0-{len(todas_las_voces)}]: ").strip()
            numero = int(seleccion)
            if numero == 0:
                print("\n  ✅ Se generarán TODAS las voces.")
                print("─" * 45 + "\n")
                return "TODAS"
            elif 1 <= numero <= len(todas_las_voces):
                voz_elegida = todas_las_voces[numero - 1]
                print(f"\n  ✅ Voz seleccionada: {voz_elegida}")
                print("─" * 45 + "\n")
                return voz_elegida
            else:
                print(f"  ⚠️  Ingresa un número entre 0 y {len(todas_las_voces)}.")
        except ValueError:
            print("  ⚠️  Entrada inválida. Ingresa solo el número.")


# ── Generación de audio ───────────────────────────────────────────────────────
def generar_audio(ssml: str, voz: str, nombre_final: str) -> str:
    # 1. Autenticación
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    url = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
        f"/locations/us-central1/publishers/google/models/gemini-2.5-flash-preview-tts:generateContent"
    )

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    # Instrucciones de estilo adaptadas al canto meditativo
    style_instructions = (
        "You are chanting the Buddhist mantra 'Nam-myoho-renge-kyo' in a meditative, devotional style. "
        "Pronounce each syllable clearly and evenly: Nam · myo · ho · ren · ge · kyo. "
        "Maintain a steady, calm rhythm throughout — like a practitioner sitting in front of a Gohonzon. "
        "Do NOT sing melodically. Chant in a spoken, intoned manner: low, grounded, and resonant. "
        "Honor the SSML timing cues for pauses and prosody changes naturally."
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{style_instructions}\n\n{ssml}"}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voz
                    }
                }
            }
        }
    }

    print(f"🎙️  Generando audio con Gemini 2.5 Flash TTS (voz: {voz})...")
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Error ({response.status_code}): {response.text}")

    # 2. Extraer audio base64
    audio_b64 = (
        response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    )
    pcm_data = base64.b64decode(audio_b64)

    # 3. Guardar PCM raw como WAV temporal
    wav_temp = f"_temp_{voz}.wav"
    with wave.open(wav_temp, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(24000)
        wav_file.writeframes(pcm_data)

    print(f"  ✅ WAV temporal: {wav_temp}")

    # 4. Convertir WAV → MP3 con ffmpeg
    print(f"  🔄 Convirtiendo a MP3...")
    resultado = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", wav_temp,
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",
            nombre_final
        ],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"❌ Error en ffmpeg: {resultado.stderr}")

    os.remove(wav_temp)
    print(f"  ✅ MP3 guardado: {nombre_final}")
    return nombre_final


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seleccion = seleccionar_voz()

    if seleccion == "TODAS":
        todas = [v for voces in VOCES.values() for v in voces]
        print(f"\n🔁 Generando {len(todas)} archivos...\n")
        for voz in todas:
            nombre = f"daimoku_5min_{voz.lower()}.mp3"
            try:
                generar_audio(DAIMOKU_SSML, voz=voz, nombre_final=nombre)
            except Exception as e:
                print(f"  ⚠️  Error con {voz}: {e}")
        print("\n🙏 Todos los archivos generados.")
    else:
        nombre = f"daimoku_5min_{seleccion.lower()}.mp3"
        generar_audio(DAIMOKU_SSML, voz=seleccion, nombre_final=nombre)
        print("\n🙏 Archivo listo para reproducir.")