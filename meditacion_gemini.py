import os
import time
import base64
import wave
import struct
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
import pygame

# ── Cargar variables de entorno ───────────────────────────────────────────────
load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path:
    raise ValueError("❌ No se encontró GOOGLE_APPLICATION_CREDENTIALS en el archivo .env")
if not os.path.exists(credentials_path):
    raise FileNotFoundError(f"❌ No se encontró el archivo: {credentials_path}\n"
                            "   Asegúrate de haber descargado el JSON de tu Service Account.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# ── Texto de la sesión de meditación ─────────────────────────────────────────
SESION_MEDITACION = """
Bienvenido a tu sesión de meditación.
Encuentra una posición cómoda, ya sea sentado o acostado.
Cierra suavemente los ojos.

Respira profundo... inhala... y exhala lentamente.
Siente cómo tu cuerpo se relaja con cada respiración.

Inhala por la nariz contando hasta cuatro.
Uno... dos... tres... cuatro.
Retén el aire un momento.
Exhala lentamente por la boca. Uno... dos... tres... cuatro.

Lleva tu atención al presente.
Suelta cualquier pensamiento que aparezca... simplemente déjalo ir.
No hay nada que resolver ahora. Solo este momento.

Respira naturalmente.
Siente el peso de tu cuerpo sobre la superficie donde descansas.
Siente cómo la tensión abandona tus hombros... tu cuello... tu mandíbula.

Permanece aquí, en calma, durante unos momentos más.

Cuando estés listo, comienza a mover suavemente los dedos de las manos.
Toma una respiración profunda final.
Y abre los ojos con calma.

Has completado tu sesión de meditación. Que tengas un día pleno y sereno.
"""


def generar_audio(texto: str, nombre_archivo: str = "meditacion.mp3") -> str:
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    # ✅ Endpoint correcto para Gemini TTS
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")  # Agrega esto a tu .env
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
        "Keep a relaxed and unhurried pace, but maintain a fluid and steady rhythm. "
        "Use standard, soft pauses between sentences."
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{style_instructions}\n\n{texto}"}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Algenib"  # ✅ Nombre exacto como en la UI
                    }
                }
            }
        }
    }

    print("🎙️ Generando audio con Gemini 2.5 Flash TTS (voz Algenib)...")
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Error ({response.status_code}): {response.text}")

    response_data = response.json()

    # Extraer el audio de la respuesta de Gemini
    try:
        audio_b64 = (
            response_data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        )
    except (KeyError, IndexError) as e:
        raise ValueError(f"❌ No se encontró audio en la respuesta: {response_data}") from e

    audio_bytes = base64.b64decode(audio_b64)

    with open(nombre_archivo, "wb") as f:
        f.write(audio_bytes)

    print(f"✅ Audio guardado como: {nombre_archivo}")
    return nombre_archivo


def convertir_a_wav(pcm_file: str, wav_file: str, sample_rate: int = 24000, channels: int = 1):
    """Convierte PCM raw a WAV estándar que pygame puede reproducir."""
    with open(pcm_file, "rb") as f:
        pcm_data = f.read()

    with wave.open(wav_file, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(pcm_data)

    print(f"✅ Convertido a WAV estándar: {wav_file}")


def reproducir_audio(nombre_archivo: str):
    """Reproduce el archivo de audio generado."""
    # Convertir PCM a WAV estándar
    wav_final = nombre_archivo.replace(".wav", "_final.wav")
    convertir_a_wav(nombre_archivo, wav_final)

    pygame.mixer.init(frequency=24000)
    pygame.mixer.music.load(wav_final)
    print("\n🧘 Iniciando sesión de meditación...\n")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    pygame.mixer.quit()
    print("\n✨ Sesión finalizada. Que tengas un día pleno.")

if __name__ == "__main__":
    archivo = generar_audio(SESION_MEDITACION, nombre_archivo="meditacion.wav")
    reproducir_audio(archivo)