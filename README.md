# 🧘 Meditaciones Guiadas con Google Text-to-Speech

Genera y reproduce una sesión de meditación guiada en español usando la API de Google Cloud Text-to-Speech.

## Requisitos

- Python 3.8+
- Proyecto en Google Cloud con la **Cloud Text-to-Speech API** habilitada
- Una **Service Account** con rol de Text-to-Speech

## Instalación

### 1. Clona el repositorio
```bash
git clone https://github.com/german-rs/MeditacionesGuiadas.git
cd MeditacionesGuiadas
```

### 2. Crea el entorno virtual e instala dependencias
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 3. Configura las credenciales
```bash
cp .env.example .env
```
Edita `.env` y coloca la ruta a tu archivo JSON de Service Account:
```
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```
Descarga tu archivo JSON desde Google Cloud Console → IAM → Cuentas de servicio → Claves.

### 4. Ejecuta la meditación
```bash
python meditacion.py
```

## ⚠️ Seguridad

- El archivo `.env` y `credentials.json` están en `.gitignore` y **nunca se suben a GitHub**
- Usa `.env.example` como plantilla para otros colaboradores

## Estructura del proyecto

```
MeditacionesGuiadas/
├── meditacion.py        # Script principal
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno (NO en GitHub)
├── .env.example         # Plantilla de variables (SÍ en GitHub)
├── .gitignore           # Archivos ignorados por Git
├── credentials.json     # Service Account key (NO en GitHub)
└── README.md
```