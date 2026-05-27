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
    # Subir un nivel desde version-voces/ hasta la raíz del proyecto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(project_root, credentials_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# ── Sesión de meditación en SSML ──────────────────────────────────────────────
SESION_MEDITACION_SSML = """
<speak>
  <!-- FASE 1 — Bienvenida e intención (~25 seg) -->
  <prosody rate="slow" pitch="-1st" volume="soft">
    Bienvenido a este espacio de descanso.
    <break time="2000ms"/>
    Esta meditación es para ti.
    <break time="1500ms"/>
    Para soltar el día...
    <break time="1500ms"/>
    y permitirte descansar.
    <break time="2500ms"/>
  </prosody>

  <!-- FASE 2 — Anclaje corporal (~30 seg) -->
  <prosody rate="65%" pitch="-2st" volume="soft">
    Cierra los ojos...
    <break time="2000ms"/>
    Siente el peso de tu cuerpo sobre la cama.
    <break time="2500ms"/>
    Deja que la superficie te sostenga...
    <break time="2000ms"/>
    completamente.
    <break time="3000ms"/>
    No necesitas hacer nada más.
    <break time="3000ms"/>
  </prosody>

  <!-- FASE 3 — Desarrollo / núcleo (~1:30 min) -->
  <prosody rate="60%" pitch="-3st" volume="x-soft">
    Lleva tu atención a la respiración.
    <break time="3000ms"/>
    Sin cambiarla...
    <break time="2000ms"/>
    solo obsérvala.
    <break time="4000ms"/>
    Con cada exhalación...
    <break time="2000ms"/>
    siente cómo tu cuerpo se hunde un poco más...
    <break time="3000ms"/>
    en el descanso.
    <break time="5000ms"/>
    Si tu mente trae pensamientos del día...
    <break time="2000ms"/>
    está bien.
    <break time="2000ms"/>
    Solo obsérvalos pasar...
    <break time="2000ms"/>
    como nubes en el cielo...
    <break time="3000ms"/>
    y vuelve suavemente...
    <break time="2000ms"/>
    a la respiración.
    <break time="6000ms"/>
    Inhala...
    <break time="4000ms"/>
    exhala...
    <break time="6000ms"/>
    Tu único lugar ahora...
    <break time="2000ms"/>
    es este momento.
    <break time="8000ms"/>
  </prosody>

  <!-- FASE 4 — Profundización / silencio (~45 seg) -->
  <prosody rate="55%" pitch="-4st" volume="x-soft">
    Deja que cada respiración...
    <break time="3000ms"/>
    te lleve más profundo...
    <break time="4000ms"/>
    hacia el descanso.
    <break time="15000ms"/>
  </prosody>

  <!-- FASE 5 — Cierre integrativo (~30 seg) -->
  <prosody rate="60%" pitch="-3st" volume="x-soft">
    Tu cuerpo sabe cómo descansar.
    <break time="3000ms"/>
    Confía en él.
    <break time="3000ms"/>
    Permite que esta noche...
    <break time="2000ms"/>
    sea de verdadero descanso.
    <break time="4000ms"/>
  </prosody>

  <!-- FASE 6 — Retorno gradual adaptado al sueño (~20 seg) -->
  <prosody rate="55%" pitch="-4st" volume="x-soft">
    No hay nada más que hacer.
    <break time="3000ms"/>
    Solo dejarte ir...
    <break time="3000ms"/>
    suavemente...
    <break time="2000ms"/>
    hacia el sueño.
    <break time="2000ms"/>
  </prosody>

  <prosody rate="slow" pitch="-2st" volume="x-soft">
    Buenas noches.
    <break time="1500ms"/>
    Visítanos en aprendeameditar.cl
  </prosody>

</speak>
"""


def generar_audio(ssml: str, nombre_final: str = "mdt_dormir_IG.mp3") -> str:
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
                        "voiceName": "Enceladus"
                    }
                }
            }
        }
    }

    print("🎙️  Generando audio con Gemini 2.5 flash TTS (voz Enceladus)...")
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


if __name__ == "__main__":
    generar_audio(SESION_MEDITACION_SSML, nombre_final="mdt_dormir_IG.mp3")
    print("\n😴 Archivo listo para reproducir.")