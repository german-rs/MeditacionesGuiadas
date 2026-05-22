import os
import time
from dotenv import load_dotenv
from google.cloud import texttospeech
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
    """Genera el audio de meditación usando Google Text-to-Speech."""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=texto)

    # Voz en español, tono calmado
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",
        name="es-US-Neural2-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.78,  # Más lento para meditación
        pitch=-3.0,  # Tono más grave y sereno
        volume_gain_db=0.0,
    )

    print("🎙️  Generando audio con Google TTS...")
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    with open(nombre_archivo, "wb") as f:
        f.write(response.audio_content)

    print(f"✅ Audio guardado como: {nombre_archivo}")
    return nombre_archivo


def reproducir_audio(nombre_archivo: str):
    """Reproduce el archivo de audio generado."""
    pygame.mixer.init()
    pygame.mixer.music.load(nombre_archivo)
    print("\n🧘 Iniciando sesión de meditación...\n")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    pygame.mixer.quit()
    print("\n✨ Sesión finalizada. Que tengas un día pleno.")


if __name__ == "__main__":
    archivo = generar_audio(SESION_MEDITACION)
    reproducir_audio(archivo)
