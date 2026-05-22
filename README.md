# 🧘 Meditaciones Guiadas con Google Text-to-Speech

Genera y reproduce una sesión de meditación guiada en español usando la API de Google Cloud Text-to-Speech.

## Requisitos
- Python 3.8+
- Cuenta de Google Cloud con TTS habilitado

## Instalación

1. Clona el repositorio:
   git clone https://github.com/german-rs/meditacion-tts.git
   cd meditacion-tts

2. Crea el entorno virtual e instala dependencias:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Configura tu API key:
   cp .env.example .env
   # Edita .env y reemplaza con tu API key real

4. Ejecuta la meditación:
   python meditacion.py

## ⚠️ Seguridad
Nunca subas el archivo `.env` a GitHub. Ya está incluido en `.gitignore`.