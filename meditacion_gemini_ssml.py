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
    credentials_path = os.path.join(os.path.dirname(__file__), credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# ── Sesión de meditación en SSML ──────────────────────────────────────────────
SESION_MEDITACION_SSML = """
<speak>
  Bienvenido a tu sesión de meditación.
  <break time="1500ms"/>
  Encuentra una posición cómoda, ya sea sentado o acostado.
  <break time="1000ms"/>
  Cierra suavemente los ojos.
  <break time="2500ms"/>

  Respira profundo...
  <break time="800ms"/>
  inhala...
  <break time="1200ms"/>
  y exhala lentamente.
  <break time="2000ms"/>

  Siente cómo tu cuerpo se relaja con cada respiración.
  <break time="2500ms"/>

  Inhala por la nariz contando hasta cuatro.
  <break time="600ms"/>
  Uno...
  <break time="600ms"/>
  dos...
  <break time="600ms"/>
  tres...
  <break time="600ms"/>
  cuatro.
  <break time="1000ms"/>
  Retén el aire un momento.
  <break time="1500ms"/>
  Exhala lentamente por la boca.
  <break time="600ms"/>
  Uno...
  <break time="600ms"/>
  dos...
  <break time="600ms"/>
  tres...
  <break time="600ms"/>
  cuatro.
  <break time="3000ms"/>

  Lleva tu atención al presente.
  <break time="1200ms"/>
  Suelta cualquier pensamiento que aparezca...
  <break time="800ms"/>
  simplemente déjalo ir.
  <break time="1500ms"/>
  No hay nada que resolver ahora.
  <break time="1000ms"/>
  Solo este momento.
  <break time="3000ms"/>

  Respira naturalmente.
  <break time="1500ms"/>
  Siente el peso de tu cuerpo sobre la superficie donde descansas.
  <break time="2000ms"/>
  Siente cómo la tensión abandona tus hombros...
  <break time="800ms"/>
  tu cuello...
  <break time="800ms"/>
  tu mandíbula.
  <break time="4000ms"/>

  Permanece aquí, en calma, durante unos momentos más.
  <break time="6000ms"/>

  Cuando estés listo, comienza a mover suavemente los dedos de las manos.
  <break time="2000ms"/>
  Toma una respiración profunda final.
  <break time="2500ms"/>
  Y abre los ojos con calma.
  <break time="2000ms"/>

  Has completado tu sesión de meditación.
  <break time="1000ms"/>
  Que tengas un día pleno y sereno.
</speak>
"""


def generar_audio(ssml: str, nombre_final: str = "meditacion_gemini.mp3") -> str:
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
        "Read in a calm, warm, and natural conversational tone. "
        "Keep a relaxed and unhurried pace, maintaining a fluid and steady rhythm. "
        "Use soft, gentle pauses. This is a guided meditation session."
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
                        "voiceName": "Algenib"
                    }
                }
            }
        }
    }

    print("🎙️  Generando audio con Gemini 2.5 Flash TTS (voz Algenib)...")
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
            "-qscale:a", "2",   # Calidad VBR alta (0=mejor, 9=peor)
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
    generar_audio(SESION_MEDITACION_SSML, nombre_final="meditacion_gemini.mp3")
    print("\n🧘 Archivo listo para reproducir.")