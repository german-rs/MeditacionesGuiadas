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

# ── Texto de la sesión de Escaneo Corporal en SSML ───────────────────────────
# Nota: Encadenamos pausas de 10s para generar silencios prolongados de meditación.
SESION_ESCANEO_CORPORAL = """
<speak>
    Bienvenido a esta sesión de escaneo corporal. <break time="3s"/>
    Tómate un momento para encontrar una postura cómoda, preferiblemente acostado boca arriba... o sentado con la espalda recta pero relajada. <break time="6s"/>
    Permite que tus ojos se cierren suavemente... y lleva la atención hacia el interior. <break time="8s"/>

    Conecta con tu respiración. <break time="4s"/>
    Siente cómo el aire entra... y cómo el aire sale. <break time="5s"/>
    No intentes cambiar nada... solo observa el ritmo natural de tu respiración. <break time="10s"/>

    Lleva ahora tu atención hacia los dedos de tus pies. <break time="5s"/>
    Siente cualquier sensación que esté presente ahí... calor, frío, un leve hormigueo... o quizás, nada en absoluto. <break time="6s"/>
    Acepta las sensaciones tal como son. <break time="10s"/> <break time="10s"/>

    Sube suavemente tu atención por las plantas de los pies, los tobillos... y las pantorrillas. <break time="6s"/>
    Siente el peso de tus piernas apoyadas sobre la superficie. <break time="5s"/>
    Si notas tensión, inhala profundamente... y al exhalar, permite que tus piernas se ablanden y se hundan un poco más. <break time="10s"/> <break time="10s"/>

    Dirige tu consciencia ahora hacia la zona de la pelvis y las caderas. <break time="5s"/>
    Nota el contacto, el peso. <break time="4s"/>
    Sube lentamente por tu columna vertebral... recorriendo la parte baja de la espalda... la parte media... y los omóplatos. <break time="6s"/>
    Suelta cualquier carga que sientas en esta zona. <break time="10s"/> <break time="10s"/>

    Lleva la atención a tu abdomen y a tu pecho. <break time="5s"/>
    Observa el sutil movimiento de subida y bajada con cada ciclo de aire. <break time="5s"/>
    Tu cuerpo se expande... tu cuerpo se relaja. <break time="10s"/> <break time="10s"/> <break time="10s"/>

    Pasa ahora a tus manos. Siente las palmas, los dedos... <break time="4s"/>
    Sube por tus brazos hacia los hombros. <break time="5s"/>
    A menudo acumulamos tensión aquí... permite que tus hombros caigan, pesados, lejos de las orejas. <break time="8s"/>

    Finalmente, mueve tu atención al cuello, a la mandíbula... liberando cualquier tensión en los dientes. <break time="5s"/>
    Relaja los músculos de la cara... los ojos... la frente. <break time="6s"/>
    Todo tu cuerpo está ahora presente, relajado y en calma. <break time="10s"/> <break time="10s"/> <break time="10s"/>

    Descansa en esta sensación de plenitud durante unos instantes de silencio. <break time="10s"/> <break time="10s"/> <break time="10s"/> <break time="10s"/>

    Poco a poco, comienza a regresar al espacio que te rodea. <break time="5s"/>
    Mueve suavemente los dedos de tus pies... y de tus manos. <break time="5s"/>
    Toma una respiración profunda... <break time="4s"/>
    Y cuando te sientas listo... abre los ojos lentamente. <break time="6s"/>

    El escaneo corporal ha terminado. Conserva esta paz contigo el resto del día.
</speak>
"""


def generar_audio(ssml_text: str, nombre_archivo: str = "escaneo_corporal.mp3") -> str:
    """Genera el audio usando Google TTS interpretando etiquetas SSML."""
    client = texttospeech.TextToSpeechClient()

    # CAMBIO CLAVE: Se usa el parámetro 'ssml' en lugar de 'text'
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Voz en español con el modelo Neural2
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",
        name="es-US-Neural2-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.78,  # Ritmo pausado ideal para meditación
        pitch=-3.0,  # Tono más grave y cálido
        volume_gain_db=0.0,
    )

    print("🎙️  Generando audio con Google TTS (Procesando SSML)...")
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
    print("\n🧘 Iniciando sesión de escaneo corporal...\n")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    pygame.mixer.quit()
    print("\n✨ Sesión finalizada. Regreso consciente al presente.")


if __name__ == "__main__":
    archivo = generar_audio(SESION_ESCANEO_CORPORAL)
    reproducir_audio(archivo)