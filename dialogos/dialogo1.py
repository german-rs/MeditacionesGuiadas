import os
import base64
import requests
import wave
import subprocess
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv

load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not os.path.isabs(credentials_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(project_root, credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# ── Diálogo: cada turno es una voz distinta ───────────────────────────────────
DIALOGO = [
    {
        "voz": "Kore",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st" volume="medium">
    ¿Qué le pasa al cerebro cuando meditamos?
  </prosody>
</speak>"""
    },
    {
        "voz": "Enceladus",
        "ssml": """<speak>
  <prosody rate="medium" pitch="-1st" volume="medium">
    Algo fascinante.
    <break time="1000ms"/>
    La amígdala, que es la parte del cerebro que activa el estrés...
    <break time="1000ms"/>
    empieza a reducir su actividad.
    <break time="1500ms"/>
    Y al mismo tiempo, la corteza prefrontal, que es donde tomamos decisiones conscientes...
    <break time="1000ms"/>
    se fortalece.
  </prosody>
</speak>"""
    },
    {
        "voz": "Kore",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st" volume="medium">
    ¿Y eso ocurre después de mucho tiempo practicando...
    <break time="800ms"/>
    o desde las primeras sesiones?
  </prosody>
</speak>"""
    },
    {
        "voz": "Enceladus",
        "ssml": """<speak>
  <prosody rate="medium" pitch="-1st" volume="medium">
    Desde antes de lo que imaginas.
    <break time="1200ms"/>
    Estudios de Harvard muestran cambios medibles en el cerebro
    <break time="800ms"/>
    con solo ocho semanas de práctica regular.
    <break time="1500ms"/>
    El hipocampo, relacionado con la memoria y el aprendizaje,
    <break time="800ms"/>
    aumenta su densidad de materia gris.
  </prosody>
</speak>"""
    },
    {
        "voz": "Kore",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st" volume="medium">
    ¿Y qué pasa con el estrés crónico?
    <break time="800ms"/>
    ¿La meditación realmente lo reduce?
  </prosody>
</speak>"""
    },
    {
        "voz": "Enceladus",
        "ssml": """<speak>
  <prosody rate="medium" pitch="-1st" volume="medium">
    Sí, y hay evidencia clara.
    <break time="1200ms"/>
    La meditación baja los niveles de cortisol...
    <break time="800ms"/>
    que es la hormona del estrés.
    <break time="1500ms"/>
    Y activa el sistema nervioso parasimpático...
    <break time="800ms"/>
    el que le dice al cuerpo que está a salvo.
    <break time="1200ms"/>
    Es literalmente el opuesto del modo de alerta.
  </prosody>
</speak>"""
    },
    {
        "voz": "Kore",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st" volume="medium">
    Increíble.
    <break time="800ms"/>
    O sea que meditar no es solo relajarse...
    <break time="800ms"/>
    es entrenar el cerebro.
  </prosody>
</speak>"""
    },
    {
        "voz": "Enceladus",
        "ssml": """<speak>
  <prosody rate="medium" pitch="-1st" volume="medium">
    Exactamente.
    <break time="1000ms"/>
    Igual que el ejercicio físico transforma el cuerpo...
    <break time="800ms"/>
    la meditación transforma la estructura del cerebro.
    <break time="1200ms"/>
    A eso se le llama neuroplasticidad.
    <break time="1500ms"/>
    Y la ciencia lo está confirmando cada vez más.
  </prosody>
</speak>"""
    },
    {
        "voz": "Kore",
        "ssml": """<speak>
  <prosody rate="medium" pitch="0st" volume="medium">
    Si quieres empezar a entrenar tu cerebro hoy...
    <break time="1000ms"/>
    visítanos en aprendeameditar.cl
  </prosody>
</speak>"""
    },
]


STYLE_INSTRUCTIONS = (
    "Speak in a calm, warm, and natural conversational tone. "
    "This is a mindful dialogue between two people reflecting on breathing and presence. "
    "Keep a relaxed and unhurried pace, as if having a genuine conversation. "
    "Not a meditation session — a real, grounded exchange between two people."
)


# ── Autenticación ─────────────────────────────────────────────────────────────
def obtener_token() -> str:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token


# ── Generar un turno del diálogo ──────────────────────────────────────────────
def generar_turno(ssml: str, voz: str, token: str, nombre_wav: str) -> str:
    url = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
        f"/locations/us-central1/publishers/google/models/gemini-2.5-flash-preview-tts:generateContent"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{STYLE_INSTRUCTIONS}\n\n{ssml}"}]
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


# ── Concatenar todos los WAVs ─────────────────────────────────────────────────
def concatenar_wavs(archivos_wav: list[str], salida_mp3: str) -> str:
    lista_path = "concat_dialogo.txt"
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
def generar_dialogo(nombre_final: str = "dialogo_mindfulness_IG.mp3") -> str:
    token = obtener_token()
    archivos_wav = []

    print("\n🎙️  Generando diálogo Kore × Enceladus...\n")

    for i, turno in enumerate(DIALOGO, 1):
        voz    = turno["voz"]
        ssml   = turno["ssml"]
        wav    = f"temp_turno_{i}_{voz.lower()}.wav"

        print(f"  Turno {i}/{len(DIALOGO)} → {voz}")
        generar_turno(ssml, voz, token, wav)
        archivos_wav.append(wav)
        print(f"  ✅ {wav} listo")

    print(f"\n🔗 Concatenando {len(archivos_wav)} turnos...")
    concatenar_wavs(archivos_wav, nombre_final)

    for archivo in archivos_wav:
        os.remove(archivo)

    print(f"\n✅ Diálogo guardado como: {nombre_final}")
    return nombre_final


if __name__ == "__main__":
    generar_dialogo(nombre_final="dialogo_mindfulness_IG.mp3")
    print("\n🧘 Archivo listo para Instagram.")