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

  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 1 — Bienvenida e intención (1-2 min)       -->
  <!-- Voz: rate=medium, pitch normal. Punto de partida -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="medium" pitch="0st">
    Te doy la bienvenida a esta sesión de meditación.
    <break time="2500ms"/>
    Este es tu momento.
    <break time="1875ms"/>
    Un espacio solo para ti,
    <break time="1250ms"/>
    lejos de las exigencias del día.
    <break time="3750ms"/>
    En los próximos minutos,
    <break time="1250ms"/>
    vas a entrenar tu mente para volver al presente...
    <break time="1875ms"/>
    a soltar lo que no puedes controlar...
    <break time="1875ms"/>
    y a encontrar calma donde estás.
    <break time="5000ms"/>
  </prosody>


  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 2 — Anclaje corporal (2-4 min)             -->
  <!-- Voz: rate desciende a slow. Instrucciones claras -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="slow" pitch="-1st">
    Busca una posición cómoda,
    <break time="1250ms"/>
    ya sea sentada en una silla
    <break time="1000ms"/>
    o sobre una superficie plana.
    <break time="3125ms"/>
    Deja que tu espalda encuentre su propio apoyo...
    <break time="2500ms"/>
    y cierra suavemente los ojos.
    <break time="5000ms"/>

    Lleva la atención a tu cuerpo.
    <break time="2500ms"/>
    Siente el peso de tu cuerpo sobre la superficie donde te encuentras...
    <break time="3750ms"/>
    Nota el contacto de tus pies con el suelo...
    <break time="3125ms"/>
    el contacto de tus manos sobre tus piernas...
    <break time="3750ms"/>

    Ahora siente cómo la tensión abandona tus hombros...
    <break time="2500ms"/>
    tu cuello...
    <break time="2500ms"/>
    tu mandíbula...
    <break time="2500ms"/>
    tu frente.
    <break time="5000ms"/>

    Sin forzar nada...
    <break time="1875ms"/>
    simplemente permite que cada parte de tu cuerpo
    <break time="1250ms"/>
    se vuelva un poco más ligera...
    <break time="1250ms"/>
    un poco más relajada...
    <break time="6250ms"/>

    Respira profundamente...
    <break time="1250ms"/>
    inhala...
    <break time="2500ms"/>
    y exhala lentamente...
    <break time="3750ms"/>
    Siente cómo tu cuerpo se relaja con cada respiración.
    <break time="6250ms"/>
  </prosody>


  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 3 — Desarrollo principal (5-15 min)        -->
  <!-- Voz: rate=x-slow, pitch=-2st. Técnica 4-5-6     -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="x-slow" pitch="-2st">
    Ahora vamos a trabajar con la respiración.
    <break time="2500ms"/>
    Inhala por la nariz contando hasta cuatro.
    <break time="1875ms"/>
    Uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro.
    <break time="1875ms"/>
    Retén el aire suavemente...
    <break time="1250ms"/>
    uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro...
    <break time="1250ms"/>
    cinco.
    <break time="1875ms"/>
    Y exhala lentamente por la boca...
    <break time="1250ms"/>
    uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro...
    <break time="1250ms"/>
    cinco...
    <break time="1250ms"/>
    seis.
    <break time="6250ms"/>

    Muy bien.
    <break time="2500ms"/>
    Repitamos.
    <break time="1875ms"/>
    Inhala...
    <break time="1250ms"/>
    uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro.
    <break time="1875ms"/>
    Retén...
    <break time="1250ms"/>
    uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro...
    <break time="1250ms"/>
    cinco.
    <break time="1875ms"/>
    Exhala...
    <break time="1250ms"/>
    uno...
    <break time="1250ms"/>
    dos...
    <break time="1250ms"/>
    tres...
    <break time="1250ms"/>
    cuatro...
    <break time="1250ms"/>
    cinco...
    <break time="1250ms"/>
    seis.
    <break time="7500ms"/>

    Ahora deja que tu respiración vuelva a su ritmo natural.
    <break time="3750ms"/>
    Lleva tu atención al presente.
    <break time="3750ms"/>
    Si algún pensamiento aparece...
    <break time="2500ms"/>
    obsérvalo sin juzgarlo...
    <break time="2500ms"/>
    y suéltalo suavemente...
    <break time="3125ms"/>
    como si fuera una hoja flotando en el agua.
    <break time="4375ms"/>
    No hay nada que resolver ahora.
    <break time="3750ms"/>
    No hay ningún lugar donde estar.
    <break time="3750ms"/>
    Solo este momento.
    <break time="7500ms"/>
  </prosody>


  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 4 — Profundización / silencio (3-8 min)    -->
  <!-- Voz: volume=soft, rate=x-slow. Máximo silencio  -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="x-slow" pitch="-3st" volume="soft">
    Imagina que estás en un lugar tranquilo...
    <break time="3750ms"/>
    Un lugar donde te sientes completamente seguro...
    <break time="3750ms"/>
    y completamente en paz.
    <break time="10000ms"/>

    Cada vez que exhalas...
    <break time="2500ms"/>
    te hundes un poco más en esa calma.
    <break time="12500ms"/>

    No tienes que hacer nada.
    <break time="5000ms"/>
    No tienes que llegar a ningún lado.
    <break time="15000ms"/>

    Aquí puedes simplemente...
    <break time="3750ms"/>
    ser.
    <break time="18750ms"/>
  </prosody>


  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 5 — Cierre integrativo (2-3 min)           -->
  <!-- Voz: rate asciende a slow. Tono más cálido      -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="slow" pitch="-1st" volume="medium">
    Poco a poco, comienza a traer de vuelta tu conciencia a este espacio.
    <break time="3750ms"/>
    Lleva contigo esta calma.
    <break time="2500ms"/>
    No tienes que dejarla aquí.
    <break time="3125ms"/>
    Es tuya.
    <break time="5000ms"/>

    Tómate un momento para agradecer este tiempo que te diste.
    <break time="3750ms"/>
    No siempre es fácil detenerse...
    <break time="2500ms"/>
    y hoy lo hiciste.
    <break time="6250ms"/>

    Cuando salgas de aquí,
    <break time="1875ms"/>
    puedes llevar esta respiración,
    <break time="1875ms"/>
    esta presencia,
    <break time="1875ms"/>
    a todo lo que venga.
    <break time="5000ms"/>
  </prosody>


  <!-- ════════════════════════════════════════════════ -->
  <!-- FASE 6 — Retorno gradual (1-2 min)              -->
  <!-- Voz: rate sube a medium. Instrucciones activas  -->
  <!-- ════════════════════════════════════════════════ -->

  <prosody rate="slow" pitch="0st" volume="medium">
    Cuando estés lista,
    <break time="1875ms"/>
    comienza a mover suavemente los dedos de las manos...
    <break time="3750ms"/>
    y los dedos de los pies.
    <break time="3750ms"/>
  </prosody>

  <prosody rate="medium" pitch="+1st" volume="medium">
    Toma una respiración profunda final...
    <break time="5000ms"/>
    Y abre los ojos con lentitud,
    <break time="1875ms"/>
    dejando que la luz entre suavemente.
    <break time="3750ms"/>

    La sesión ha concluido.
    <break time="2500ms"/>
    Que tengas un día pleno y consciente.
  </prosody>

</speak>
"""


def generar_audio(ssml: str, nombre_final: str = "meditacion_gemini_gen_Enceladus.mp3") -> str:
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

    print("🎙️  Generando audio con Gemini 2.5 pro TTS (voz Enceladus)...")
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
    generar_audio(SESION_MEDITACION_SSML, nombre_final="meditacion_gemini_gen_Enceladus.mp3")
    print("\n🧘 Archivo listo para reproducir.")