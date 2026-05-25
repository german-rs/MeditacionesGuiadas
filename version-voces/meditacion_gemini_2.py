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

# ── Sesión dividida por fases ─────────────────────────────────────────────────
# Cada fase es un bloque SSML independiente y válido (con su propio <speak>)
FASES = [
    {
        "nombre": "fase1_bienvenida",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st">
    Te doy la bienvenida a esta sesión de meditación.
    <break time="2000ms"/>
    Este es tu momento.
    <break time="1500ms"/>
    Un espacio solo para ti,
    <break time="1000ms"/>
    lejos de las exigencias del día.
    <break time="3000ms"/>
    En los próximos minutos,
    <break time="1000ms"/>
    vas a entrenar tu mente para volver al presente...
    <break time="1500ms"/>
    a soltar lo que no puedes controlar...
    <break time="1500ms"/>
    y a encontrar calma donde estás.
    <break time="4000ms"/>
  </prosody>
</speak>"""
    },
    {
        "nombre": "fase2_anclaje",
        "ssml": """<speak>
  <prosody rate="slow" pitch="-1st">
    Busca una posición cómoda,
    <break time="1000ms"/>
    ya sea sentado en una silla
    <break time="800ms"/>
    o sobre una superficie plana.
    <break time="2500ms"/>
    Deja que tu espalda encuentre su propio apoyo...
    <break time="2000ms"/>
    y cierra suavemente los ojos.
    <break time="4000ms"/>
    Lleva la atención a tu cuerpo.
    <break time="2000ms"/>
    Siente el peso de tu cuerpo sobre la superficie donde te encuentras...
    <break time="3000ms"/>
    Nota el contacto de tus pies con el suelo...
    <break time="2500ms"/>
    el contacto de tus manos sobre tus piernas...
    <break time="3000ms"/>
    Ahora siente cómo la tensión abandona tus hombros...
    <break time="2000ms"/>
    tu cuello...
    <break time="2000ms"/>
    tu mandíbula...
    <break time="2000ms"/>
    tu frente.
    <break time="4000ms"/>
    Sin forzar nada...
    <break time="1500ms"/>
    simplemente permite que cada parte de tu cuerpo
    <break time="1000ms"/>
    se vuelva un poco más ligera...
    <break time="1000ms"/>
    un poco más relajada...
    <break time="5000ms"/>
    Respira profundamente...
    <break time="1000ms"/>
    inhala...
    <break time="2000ms"/>
    y exhala lentamente...
    <break time="3000ms"/>
    Siente cómo tu cuerpo se relaja con cada respiración.
    <break time="5000ms"/>
  </prosody>
</speak>"""
    },
    {
        "nombre": "fase3_desarrollo",
        "ssml": """<speak>
  <prosody rate="x-slow" pitch="-2st">
    Ahora vamos a trabajar con la respiración.
    <break time="2000ms"/>
    Inhala por la nariz contando hasta cuatro.
    <break time="1500ms"/>
    Uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro.
    <break time="1500ms"/>
    Retén el aire suavemente...
    <break time="1000ms"/>
    uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro... <break time="1000ms"/>
    cinco.
    <break time="1500ms"/>
    Y exhala lentamente por la boca...
    <break time="1000ms"/>
    uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro... <break time="1000ms"/>
    cinco... <break time="1000ms"/>
    seis.
    <break time="5000ms"/>
    Muy bien.
    <break time="2000ms"/>
    Repitamos.
    <break time="1500ms"/>
    Inhala...
    <break time="1000ms"/>
    uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro.
    <break time="1500ms"/>
    Retén...
    <break time="1000ms"/>
    uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro... <break time="1000ms"/>
    cinco.
    <break time="1500ms"/>
    Exhala...
    <break time="1000ms"/>
    uno... <break time="1000ms"/>
    dos... <break time="1000ms"/>
    tres... <break time="1000ms"/>
    cuatro... <break time="1000ms"/>
    cinco... <break time="1000ms"/>
    seis.
    <break time="6000ms"/>
    Ahora deja que tu respiración vuelva a su ritmo natural.
    <break time="3000ms"/>
    Lleva tu atención al presente.
    <break time="3000ms"/>
    Si algún pensamiento aparece...
    <break time="2000ms"/>
    obsérvalo sin juzgarlo...
    <break time="2000ms"/>
    y suéltalo suavemente...
    <break time="2500ms"/>
    como si fuera una hoja flotando en el agua.
    <break time="3500ms"/>
    No hay nada que resolver ahora.
    <break time="3000ms"/>
    No hay ningún lugar donde estar.
    <break time="3000ms"/>
    Solo este momento.
    <break time="6000ms"/>
  </prosody>
</speak>"""
    },
    {
        "nombre": "fase4_profundizacion",
        "ssml": """<speak>
  <prosody rate="x-slow" pitch="-3st" volume="soft">
    Imagina que estás en un lugar tranquilo...
    <break time="3000ms"/>
    Un lugar donde te sientes completamente seguro...
    <break time="3000ms"/>
    y completamente en paz.
    <break time="8000ms"/>
    Cada vez que exhalas...
    <break time="2000ms"/>
    te hundes un poco más en esa calma.
    <break time="10000ms"/>
    No tienes que hacer nada.
    <break time="4000ms"/>
    No tienes que llegar a ningún lado.
    <break time="12000ms"/>
    Aquí puedes simplemente...
    <break time="3000ms"/>
    ser.
    <break time="15000ms"/>
  </prosody>
</speak>"""
    },
    {
        "nombre": "fase5_cierre",
        "ssml": """<speak>
  <prosody rate="slow" pitch="-1st" volume="medium">
    Poco a poco, comienza a traer de vuelta tu conciencia a este espacio.
    <break time="3000ms"/>
    Lleva contigo esta calma.
    <break time="2000ms"/>
    No tienes que dejarla aquí.
    <break time="2500ms"/>
    Es tuya.
    <break time="4000ms"/>
    Tómate un momento para agradecer este tiempo que te diste.
    <break time="3000ms"/>
    No siempre es fácil detenerse...
    <break time="2000ms"/>
    y hoy lo hiciste.
    <break time="5000ms"/>
    Cuando salgas de aquí,
    <break time="1500ms"/>
    puedes llevar esta respiración,
    <break time="1500ms"/>
    esta presencia,
    <break time="1500ms"/>
    a todo lo que venga.
    <break time="4000ms"/>
  </prosody>
</speak>"""
    },
    {
        "nombre": "fase6_retorno",
        "ssml": """<speak>
  <prosody rate="slow" pitch="0st" volume="medium">
    Cuando estés lista,
    <break time="1500ms"/>
    comienza a mover suavemente los dedos de las manos...
    <break time="3000ms"/>
    y los dedos de los pies.
    <break time="3000ms"/>
  </prosody>
  <prosody rate="medium" pitch="+1st" volume="medium">
    Toma una respiración profunda final...
    <break time="4000ms"/>
    Y abre los ojos con lentitud,
    <break time="1500ms"/>
    dejando que la luz entre suavemente.
    <break time="3000ms"/>
    La sesión ha concluido.
    <break time="2000ms"/>
    Que tengas un día pleno y consciente.
  </prosody>
</speak>"""
    },
]

STYLE_INSTRUCTIONS = (
    "Speak in a calm, warm tone — slow and deliberate, but never so slow it feels unnatural. "
    "Maintain a steady, unhurried rhythm, as if reading to someone who is resting with their eyes closed. "
    "Let each phrase land before moving to the next — leave gentle space between sentences, not dramatic silence. "
    "Keep the voice soft and grounded throughout. This is a guided meditation session."
)


# ── Autenticación (reutilizable) ──────────────────────────────────────────────
def obtener_token() -> str:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token


# ── Generar audio de una sola fase ───────────────────────────────────────────
def generar_fase(ssml: str, token: str, nombre_wav: str) -> str:
    url = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
        f"/locations/us-central1/publishers/google/models/gemini-2.5-flash-preview-tts:generateContent"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # ← SSML en contents, style_instructions en prompt (separados)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": ssml}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "prompt": STYLE_INSTRUCTIONS,
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Enceladus"
                    }
                }
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Error ({response.status_code}): {response.text}")

    audio_b64 = (
        response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    )
    pcm_data = base64.b64decode(audio_b64)

    with wave.open(nombre_wav, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(pcm_data)

    return nombre_wav


# ── Concatenar WAVs con ffmpeg ────────────────────────────────────────────────
def concatenar_wavs(archivos_wav: list[str], salida_mp3: str) -> str:
    # Crear archivo de lista para ffmpeg concat
    lista_path = "concat_list.txt"
    with open(lista_path, "w") as f:
        for archivo in archivos_wav:
            f.write(f"file '{os.path.abspath(archivo)}'\n")

    resultado = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", lista_path,
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",
            salida_mp3
        ],
        capture_output=True,
        text=True
    )

    os.remove(lista_path)

    if resultado.returncode != 0:
        raise RuntimeError(f"❌ Error en ffmpeg: {resultado.stderr}")

    return salida_mp3


# ── Flujo principal ───────────────────────────────────────────────────────────
def generar_sesion_completa(nombre_final: str = "meditacion_gemini_gen_Enceladus.mp3") -> str:
    token = obtener_token()
    archivos_wav = []

    for i, fase in enumerate(FASES, 1):
        nombre_wav = f"temp_{fase['nombre']}.wav"
        print(f"🎙️  Generando {fase['nombre']} ({i}/{len(FASES)})...")
        generar_fase(fase["ssml"], token, nombre_wav)
        archivos_wav.append(nombre_wav)
        print(f"   ✅ {nombre_wav} listo")

    print(f"\n🔗 Concatenando {len(archivos_wav)} fases...")
    concatenar_wavs(archivos_wav, nombre_final)

    # Limpiar WAVs temporales
    for archivo in archivos_wav:
        os.remove(archivo)

    print(f"✅ Sesión completa guardada como: {nombre_final}")
    return nombre_final


if __name__ == "__main__":
    generar_sesion_completa(nombre_final="meditacion_gemini_gen_Enceladus.mp3")
    print("\n🧘 Archivo listo para reproducir.")