import os
import time
from dotenv import load_dotenv
from google.cloud import texttospeech
from pydub import AudioSegment
import pygame

# ── Configuración de Entorno ──────────────────────────────────────────────────
load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path or not os.path.exists(credentials_path):
    raise FileNotFoundError("❌ Verifica la ruta de tu cuenta de servicio de Google Cloud en el archivo .env")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# ── Guion SSML diseñado para el Sueño Profundo ────────────────────────────────
SESION_SUEÑO_SSML = """
<speak>
    Es momento de descansar. <break time="4s"/>
    Suelta cualquier expectativa de lo que debes hacer... ya no hay nada que resolver hoy. <break time="6s"/>
    Deja que tu cuerpo se hunda profundamente en la cama. Siente el soporte firme debajo de ti. <break time="8s"/>

    Inhala aire fresco... suave... profundo... <break time="4s"/>
    Y al exhalar, entrega todo el peso del día a la gravedad. <break time="8s"/>

    Permite que tus pensamientos pasen como nubes lejanas en la noche. <break time="5s"/>
    No te enganches a ninguno... solo míralos pasar... y déjalos ir. <break time="10s"/> <break time="10s"/>

    Siente cómo tus párpados se vuelven pesados... muy pesados. <break time="6s"/>
    La tensión de tu rostro se disuelve. <break time="4s"/>
    Tu mandíbula se relaja... tus hombros caen libres... <break time="8s"/>

    Cada respiración es un ancla hacia un descanso profundo. <break time="5s"/>
    Inhalando calma... <break time="4s"/>
    Exhalando cualquier rastro de prisa. <break time="10s"/> <break time="10s"/>

    Tu mente se aquieta. <break time="5s"/>
    Tu cuerpo sabe exactamente cómo descansar. <break time="6s"/>
    Confía en este momento. <break time="5s"/>
    Déjate llevar por el silencio... <break time="10s"/> <break time="10s"/> <break time="10s"/>

    Descansa... <break time="5s"/>
    Duerme en paz. <break time="10s"/> <break time="10s"/>
</speak>
"""


def generar_voz_ssml(ssml_text: str, archivo_salida: str = "solo_voz.mp3") -> str:
    """Genera la pista de voz usando Google Cloud TTS."""
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",
        name="es-US-Neural2-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.74,  # Ritmo lento para inducir el sueño
        pitch=-4.0,  # Tono grave y relajante
    )

    print("🎙️  1. Solicitando voz pausada a Google TTS...")
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    with open(archivo_salida, "wb") as f:
        f.write(response.audio_content)

    return archivo_salida


def mezclar_con_fondo(archivo_voz: str, archivo_fondo: str, archivo_final: str = "meditacion_dormir.mp3") -> str:
    """Mezcla la voz con el fondo musical asegurando un bucle correcto."""
    print(f"🎵 2. Mezclando voz con el archivo de fondo: {archivo_fondo}...")

    if not os.path.exists(archivo_fondo):
        raise FileNotFoundError(
            f"❌ No se encontró el archivo '{archivo_fondo}'. Asegúrate de guardarlo en esta misma carpeta.")

    # Cargar las pistas
    voz = AudioSegment.from_mp3(archivo_voz)
    fondo = AudioSegment.from_mp3(archivo_fondo)

    # Atenuar la música de fondo (-24 dB) para que se mantenga sutil
    fondo_suave = fondo - 24

    # Superponer la voz. 'loop=True' maneja automáticamente la duración de 5m 52s del fondo
    mezcla = voz.overlay(fondo_suave, loop=True)

    # Cierre suave: desvanecimiento de 8 segundos al final
    sesion_terminada = mezcla.fade_out(8000)

    print(f"💾 3. Exportando mezcla final...")
    sesion_terminada.export(archivo_final, format="mp3")
    print(f"✅ ¡Sesión lista para escuchar!: {archivo_final}")

    # Limpieza del archivo temporal de voz
    if os.path.exists(archivo_voz):
        os.remove(archivo_voz)

    return archivo_final


def reproducir_audio(nombre_archivo: str):
    """Reproduce el resultado final usando pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(nombre_archivo)
    print("\n🌙 Iniciando reproducción: Preparando el espacio para dormir...\n")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    pygame.mixer.quit()
    print("\n✨ Audio finalizado.")


if __name__ == "__main__":
    # Ajustado al archivo real que encontraste
    ARCHIVO_AMBIENTAL = "deep-relaxing-music.mp3"

    try:
        archivo_temporal_voz = generar_voz_ssml(SESION_SUEÑO_SSML)
        archivo_final_meditacion = mezclar_con_fondo(archivo_temporal_voz, ARCHIVO_AMBIENTAL)
        reproducir_audio(archivo_final_meditacion)

    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")