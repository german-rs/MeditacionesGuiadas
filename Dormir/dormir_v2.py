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

# ── Sesión de meditación en SSML ──────────────────────────────────────────────
SESION_MEDITACION_SSML = """
<speak>

  <!-- FASE 1 — Bienvenida e intención (~25 seg) -->
  <prosody rate="medium" pitch="-1st" volume="soft">
    Te doy la bienvenida a este espacio de descanso.
    <break time="2200ms"/>
    Esta meditación es para.
    <break time="1650ms"/>
    soltar el día...
    <break time="1650ms"/>
    y permitirte descansar.
    <break time="3000ms"/>
  </prosody>

<!-- FASE 2 — Anclaje corporal (~30 seg) -->
<prosody rate="85%" pitch="-2st" volume="soft">
  Ahora. Cierra los ojos...
  <break time="2860ms"/>
  Siente el peso de tu cuerpo sobre la cama.
  <break time="3575ms"/>
  y deja que la superficie te sostenga...completamente.
  <break time="7000ms"/>
  No necesitas hacer nada más.
  <break time="4290ms"/>
</prosody>

  <!-- FASE 3 — Desarrollo / núcleo (~1:30 min) -->
  <prosody rate="80%" pitch="-3st" volume="x-soft">
    Ahora. Lleva tu atención a la respiración.
    <break time="3300ms"/>
    Sin cambiarla...
    <break time="2200ms"/>
    solo obsérvala.
    <break time="4400ms"/>
    Con cada exhalación...
    <break time="2200ms"/>
    siente cómo tu cuerpo se hunde un poco más...
    <break time="3300ms"/>
    en el descanso.
    <break time="5500ms"/>
    Si tu mente trae pensamientos del día...
    <break time="2200ms"/>
    está bien.
    <break time="2200ms"/>
    Solo obsérvalos pasar...
    <break time="2200ms"/>
    como nubes en el cielo...
    <break time="3300ms"/>
    y vuelve suavemente...
    <break time="2200ms"/>
    a la respiración.
    <break time="6600ms"/>
    Inhala...
    <break time="4400ms"/>
    exhala...
    <break time="6600ms"/>
    Tu único lugar ahora...
    <break time="2200ms"/>
    es este momento.
    <break time="8800ms"/>
  </prosody>

  <!-- FASE 4 — Profundización / silencio (~45 seg) -->
  <prosody rate="75%" pitch="-4st" volume="x-soft">
    Deja que cada respiración...
    <break time="3300ms"/>
    te lleve más profundo...
    <break time="4400ms"/>
    hacia el descanso.
    <break time="10500ms"/>
  </prosody>

  <!-- FASE 5 — Cierre integrativo (~30 seg) -->
  <prosody rate="80%" pitch="-3st" volume="x-soft">
    Tu cuerpo sabe cómo descansar.
    <break time="3300ms"/>
    Confía en él.
    <break time="3300ms"/>
    Permite que esta noche...
    <break time="2200ms"/>
    sea de verdadero descanso.
    <break time="4400ms"/>
  </prosody>

  <!-- FASE 6 — Retorno gradual adaptado al sueño (~20 seg) -->
  <prosody rate="75%" pitch="-4st" volume="x-soft">
    No hay nada más que hacer.
    <break time="3300ms"/>
    Solo dejarte ir...
    <break time="3300ms"/>
    suavemente...
    <break time="2200ms"/>
    hacia el sueño.
    <break time="2200ms"/>
  </prosody>

<prosody rate="85%" pitch="-2st" volume="x-soft">
  Buenas noches.
</prosody>
<break time="2650ms"/>

<prosody rate="medium" pitch="0st" volume="soft">
  Visítanos en aprendeameditar.cl
</prosody>
</speak>
"""


# ── Selección de voz en consola ───────────────────────────────────────────────
def seleccionar_voz() -> str:
    todas_las_voces = []

    print("\n" + "─" * 45)
    print("  🎙️  Selección de voz")
    print("─" * 45)

    indice = 1
    indices_por_genero = {}

    for genero, voces in VOCES.items():
        print(f"\n  {genero}:")
        indices_por_genero[genero] = []
        for voz in voces:
            print(f"    [{indice}] {voz}")
            todas_las_voces.append(voz)
            indices_por_genero[genero].append(indice)
            indice += 1

    print("\n" + "─" * 45)

    while True:
        try:
            seleccion = input(f"  Elige una voz [1-{len(todas_las_voces)}]: ").strip()
            numero = int(seleccion)
            if 1 <= numero <= len(todas_las_voces):
                voz_elegida = todas_las_voces[numero - 1]
                print(f"\n  ✅ Voz seleccionada: {voz_elegida}")
                print("─" * 45 + "\n")
                return voz_elegida
            else:
                print(f"  ⚠️  Ingresa un número entre 1 y {len(todas_las_voces)}.")
        except ValueError:
            print("  ⚠️  Entrada inválida. Ingresa solo el número.")


# ── Generación de audio ───────────────────────────────────────────────────────
def generar_audio(ssml: str, voz: str, nombre_final: str = "mdt_dormir_IG.mp3") -> str:
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

    style_instructions = (
        "Speak in a calm, warm tone — slow and deliberate, but never so slow it feels unnatural. "
        "Maintain a steady, unhurried rhythm, as if reading to someone who is resting with their eyes closed. "
        "Let each phrase land before moving to the next — leave gentle space between sentences, not dramatic silence. "
        "Keep the voice soft and grounded throughout. This is a guided meditation session."
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
    wav_temp = "mdt_temp.wav"
    with wave.open(wav_temp, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)   # 16-bit
        wav.setframerate(24000)
        wav.writeframes(pcm_data)

    print(f"✅ WAV temporal generado: {wav_temp}")

    # 4. Convertir WAV → MP3 con ffmpeg
    print("🔄 Convirtiendo a MP3 con ffmpeg...")
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

    # 5. Limpiar WAV temporal
    os.remove(wav_temp)

    print(f"✅ MP3 guardado como: {nombre_final}")
    return nombre_final


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    voz_seleccionada = seleccionar_voz()
    nombre_archivo = f"medt_dormir_IG_{voz_seleccionada.lower()}.mp3"
    generar_audio(SESION_MEDITACION_SSML, voz=voz_seleccionada, nombre_final=nombre_archivo)
    print("\n😴 Archivo listo para reproducir.")