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

  <!-- FASE 1 — Bienvenida e identificación (7 seg) -->
  <prosody rate="medium" pitch="0st">
    Te doy la bienvenida a esta meditación de atención plena.
    <break time="2000ms"/>
    Tómate un minuto.
    <break time="1250ms"/>
    Solo para ti.
    <break time="2000ms"/>
  </prosody>

  <!-- FASE 2 — Anclaje (8 seg) -->
  <prosody rate="75%" pitch="-1st">
    Cierra los ojos...
    <break time="1875ms"/>
    y siente tu cuerpo donde estás.
    <break time="2500ms"/>
  </prosody>

  <!-- FASE 3 — Atención en la respiración (30 seg) -->
  <prosody rate="75%" pitch="-2st">
    Ahora, lleva tu atención a la respiración.
    <break time="2500ms"/>
    No la cambies...
    <break time="1875ms"/>
    solo obsérvala.
    <break time="3750ms"/>
    Siente como el aire entra...
    <break time="3750ms"/>
    y sale...
    <break time="5000ms"/>
    Si tu mente se distrae...
    <break time="1875ms"/>
    sin juzgarte...
    <break time="1875ms"/>
    vuelve tu atención a la respiración.
    <break time="15000ms"/>
  </prosody>

  <!-- FASE 4 — Profundización / silencio (8 seg) -->
  <prosody rate="60%" pitch="-3st" volume="x-soft">
    Solo siente este momento...
    <break time="5000ms"/>
  </prosody>

  <!-- FASE 5 — Cierre integrativo (5 seg) -->
  <prosody rate="75%" pitch="-1st" volume="medium">
    Ahora. Lleva esta calma contigo.
    <break time="2500ms"/>
  </prosody>

  <!-- FASE 6 — Retorno + marca (7 seg) -->
  <prosody rate="medium" pitch="+1st" volume="medium">
    y abre los ojos... lentamente...
    <break time="2500ms"/>
    Gracias por meditar con nosotros.
    <break time="1250ms"/>
    Visítanos en aprendeameditar.cl
  </prosody>

</speak>
"""


def generar_audio(ssml: str, nombre_final: str = "meditacion_gemini_Enceladus.mp3") -> str:
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
    wav_temp = "meditacion_temp.wav"
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
    generar_audio(SESION_MEDITACION_SSML, nombre_final="meditacion_IG_Enceladus.mp3")
    print("\n🧘 Archivo listo para reproducir.")