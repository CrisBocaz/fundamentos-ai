# Fundamentos AI 🚀

**Aplicación de traducción inteligente y Q&A sobre documentos con Google Gemini API**

Una aplicación web moderna construida con **Gradio 6.0** que aprovecha los modelos de IA más recientes de Google para proporcionar dos funcionalidades principales:

- 🌐 **Traducción Inteligente** - Traduce textos entre múltiples idiomas con procesamiento en tiempo real
- 📄 **Q&A sobre Documentos** - Responde preguntas específicas basadas en el contenido de tus documentos

## ¿Por qué Fundamentos AI?

Este proyecto demuestra cómo construir aplicaciones de IA modernas que:
- **Utilizan múltiples modelos con fallback automático** - Si un modelo no está disponible, automáticamente intenta con otro
- **Mantienen seguridad de primera clase** - La API Key se maneja con encriptación y validación
- **Ofrecen UI/UX profesional** - Interfaz minimalista pero moderna construida con Gradio 6.0
- **Implementan búsqueda semántica** - Utiliza ChromaDB para encontrar el contexto más relevante en documentos

## 🎯 Características Clave

### Traducción Inteligente
- ✅ Soporte para **60+ idiomas**
- ✅ Interfaz intuitiva con selección de idioma origen/destino
- ✅ Contador de caracteres en tiempo real (máx. 5,000)
- ✅ Procesamiento instantáneo con múltiples modelos

### Q&A (Preguntas y Respuestas)
- ✅ Carga documentos de cualquier tamaño
- ✅ Búsqueda semántica con **ChromaDB** para contexto relevante
- ✅ Respuestas contextuales basadas en el contenido
- ✅ Fallback automático entre 4 modelos de Gemini

### Seguridad & Confiabilidad
- 🔒 **Autenticación con API Key** - Control de acceso garantizado
- 🔄 **Fallback automático** - Si gemini-2.5-flash no funciona, intenta con otros
- ✨ **Validación robusta** - Encriptación de API Key, validación de entrada
- 📊 **Logging detallado** - Rastrea cada operación para debugging

## 📱 Vista Previa

### Traducción Tab
```
┌─────────────────────────────────────────────────┐
│ 🌐 Traducción                                   │
├─────────────────────────────────────────────────┤
│ Idioma origen: [Español ▼]                      │
│ Texto original: [Escribe aquí...]               │
│ Caracteres: 0 / 5,000                           │
│                                  [Traducir →]   │
│ Idioma destino: [English ▼]                     │
│ Traducción: [Resultado aquí...]                 │
└─────────────────────────────────────────────────┘
```

### Q&A Tab
```
┌─────────────────────────────────────────────────┐
│ 📄 QA — Preguntas & Respuestas                  │
├─────────────────────────────────────────────────┤
│ Paso 1: Pega el documento                       │
│ [Documento...]                                  │
│                                                 │
│ Paso 2: Escribe tu pregunta                     │
│ [¿Cuál es el tema principal?]                   │
│                                                 │
│ Paso 3: Obtén la respuesta       [Responder →]  │
│ [Respuesta del asistente...]                    │
└─────────────────────────────────────────────────┘
```

**📸 Nota:** Para ver capturas de pantalla actuales de la app funcionando, ejecuta localmente y accede a `http://localhost:7860`

## Modelos Soportados

La aplicación utiliza un sistema de fallback con estos modelos:
1. `gemini-2.5-flash` (primario)
2. `gemini-2.5-flash-lite`
3. `gemini-2.0-flash`
4. `gemini-2.0-flash-lite` (fallback final)

## 🌐 Acceso a la Aplicación

### Opción 1: Ejecutar Localmente (Recomendado para desarrollo)
Sigue la sección de [Instalación Local](#instalación-local) abajo

### Opción 2: Despliegue en la Nube
> 🚀 **Próximamente** - Deploy automático en Hugging Face Spaces o Heroku
> 
> Para desplegar tu propia instancia:
> - **Hugging Face Spaces**: Clona este repo como un nuevo Space privado
> - **Heroku**: Usa `heroku create` + agrega buildpack de Python
> - **Railway/Render**: Conecta el repo directamente

---

## 💻 Instalación Local

### Requisitos Previos
- **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
- **pip** - Incluido con Python
- **Git** - [Descargar](https://git-scm.com/downloads)
- **API Key de Google Gemini** - [Obtener gratis](https://aistudio.google.com/apikey)

### Pasos de Instalación

**Paso 1: Clonar el repositorio**
```bash
git clone https://github.com/CrisBocaz/fundamentos-ai.git
cd fundamentos-ai
```

**Paso 2: Crear ambiente virtual** (recomendado)
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**Paso 3: Instalar dependencias**
```bash
pip install -r requirements.txt
```

**Paso 4: Ejecutar la aplicación**
```bash
# macOS / Linux
PYTHONUTF8=1 python3 app.py

# Windows
set PYTHONUTF8=1 && python app.py
```

### 🎯 Acceso a la App
La aplicación se abrirá automáticamente en:
- **URL:** `http://localhost:7860`
- **Interfaz:** Interfaz web moderna en tu navegador

---

## 📖 Guía de Uso

### 1️⃣ Configuración Inicial

1. **Obtén tu API Key**
   - Ve a [Google AI Studio](https://aistudio.google.com/apikey)
   - Crea una nueva API Key (gratis con 60 consultas/minuto)
   - Copia la clave

2. **Ingresa la API Key**
   - En la sección superior "API Key de Google Gemini"
   - Pega tu clave (puedes mostrar/ocultar con el botón 👁)
   - Verás: ✅ "API Key ingresada. Puedes usar las operaciones."

### 2️⃣ Traducción de Textos

1. Selecciona **Idioma Origen** (ej: Español)
2. Pega o escribe tu texto (máx. 5,000 caracteres)
3. Selecciona **Idioma Destino** (ej: English)
4. Presiona **"Traducir →"**
5. Ver resultado en el campo de Traducción

**Idiomas soportados:** Español, English, Français, Deutsch, 中文, 日本語, Português, Italiano, Русский, y muchos más

### 3️⃣ Q&A sobre Documentos

1. **Paso 1:** Pega tu documento (artículo, libro, reporte, etc.)
2. **Paso 2:** Escribe tu pregunta específica
3. **Paso 3:** Presiona **"Responder →"**
4. Ver respuesta contextual basada en tu documento

**Ejemplo:**
```
Documento: "La mitocondria es el orgánulo responsable de la producción de energía..."
Pregunta: "¿Cuál es la función principal de la mitocondria?"
Respuesta: "La mitocondria es el orgánulo responsable de la producción de energía..."
```

## 🔍 Validar Modelos Disponibles

Para verificar qué modelos de Gemini están disponibles con tu API Key:

```bash
python3 check_models.py
```

O con tu API Key como argumento:
```bash
python3 check_models.py "AIza_tu_clave_aqui"
```

**Salida esperada:**
```
=== Modelos con soporte generateContent ===

  ✅ models/gemini-2.5-flash
  ✅ models/gemini-2.5-flash-lite
  ✅ models/gemini-2.0-flash
  ✅ models/gemini-2.0-flash-lite
  ...
```

## 🔐 Obtener API Key de Google Gemini

### Pasos:
1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Inicia sesión con tu cuenta Google
3. Haz clic en "**Create API Key**"
4. Selecciona "**Create new secret key in new project**"
5. Copia la clave generada
6. **⚠️ IMPORTANTE:** Nunca compartas tu API Key públicamente

### Límites de Cuota (Tier Gratuito):
- 📊 **60 solicitudes por minuto**
- 📈 **1 millón de tokens de entrada por día**
- 📝 **Documentos ilimitados** para Q&A

### Plan Pagado:
- Acceso prioritario a nuevos modelos
- Límites de cuota aumentados
- Soporte técnico mejorado
- [Ver precios](https://ai.google.dev/pricing)

## 📂 Estructura del Proyecto

```
fundamentos-ai/
│
├── 📄 app.py                    # Aplicación principal (Gradio 6.0)
│   ├── UI Components (Tabs, Inputs, Buttons)
│   ├── API Key validation
│   ├── Translation engine
│   └── Q&A with ChromaDB
│
├── 🔍 check_models.py           # Script para validar modelos disponibles
│   └── Lista modelos con soporte generateContent
│
├── 📋 requirements.txt          # Dependencias Python
│   ├── gradio==6.0
│   ├── google-generativeai>=0.3.0
│   ├── chromadb>=0.4.0
│   └── python-dotenv>=1.0.0
│
├── .gitignore                   # Protege datos sensibles
│   ├── .env (API keys)
│   ├── __pycache__
│   ├── *.log
│   └── venv/
│
├── README.md                    # Este archivo
└── LICENSE                      # MIT License
```

### Líneas de Código:
- **~1000+ líneas** en app.py
- **~500 líneas** de CSS personalizado
- **~200 líneas** de lógica de negocio (traducción, Q&A)
- **~300 líneas** de validación y manejo de errores

## 🛠️ Tecnologías

| Componente | Descripción | Versión |
|-----------|-------------|---------|
| **Gradio** | Framework web moderno para aplicaciones de ML | 6.0 |
| **Google Gemini API** | Modelos de IA generativa state-of-the-art | 2.5-flash, 2.0-flash |
| **ChromaDB** | Base de datos vectorial para búsqueda semántica | 0.4.0+ |
| **Python** | Lenguaje principal | 3.8+ |
| **Google-GenAI** | SDK oficial de Google Gemini | 0.3.0+ |

### Arquitectura
```
┌─────────────────────┐
│   Gradio UI 6.0     │ ← Interfaz moderna y responsiva
└──────────┬──────────┘
           │
     ┌─────▼──────┐
     │  app.py    │ ← Lógica principal de la app
     └─────┬──────┘
           │
    ┌──────┴──────┬──────────┐
    │             │          │
    ▼             ▼          ▼
┌────────┐  ┌─────────┐  ┌────────┐
│Gemini  │  │ChromaDB │  │Validate│
│API     │  │Semantic │  │API Key │
│        │  │Search   │  │        │
└────────┘  └─────────┘  └────────┘
```

## 🔒 Seguridad & Best Practices

### Protección de Datos Sensibles
El proyecto incluye `.gitignore` que protege automáticamente:
```
.env                    # Variables de entorno (API keys)
*.log                   # Archivos de log con información sensible
__pycache__/           # Archivos compilados de Python
venv/                  # Ambiente virtual
.DS_Store              # Archivos del sistema macOS
*.pyc                  # Bytecode compilado
```

### ⚠️ IMPORTANTE - Seguridad de API Key
**NUNCA** hagas esto:
```bash
# ❌ MAL - Expone la API Key
git add .env
git commit -m "Add API key"
python app.py AIza_tu_clave_123

# ✅ BIEN - Usa variables de entorno
export GEMINI_API_KEY="AIza_tu_clave"
python app.py  # Lee desde variable de entorno
```

## 🐛 Manejo Automático de Errores

La aplicación detecta y maneja:

| Error | Acción |
|-------|--------|
| ❌ **API Key inválida** | Muestra: "API Key inválida o sin permisos" |
| ❌ **Cuota agotada** | Intenta automáticamente con el siguiente modelo |
| ❌ **Modelo no disponible** | Fallback a: gemini-2.0-flash → gemini-2.0-flash-lite |
| ❌ **Documento vacío** | Valida entrada antes de procesar |
| ❌ **Timeout de API** | Reintentos con exponential backoff |

## 📊 Logging & Debug

Durante desarrollo, la aplicación imprime logs útiles:
```
[TRANSLATE] idioma=English | chars_texto=150 | chars_respuesta=200
[QA] documento=1500 chars | pregunta=50 chars | resultado=350 chars
[FALLBACK] gemini-2.5-flash falló: 429 RESOURCE_EXHAUSTED. Probando gemini-2.0-flash...
[API_ERROR] API Key inválida o sin permisos. Verifica tu clave de Gemini.
```

Para desactivar logs en producción:
```python
# En app.py, comentar todas las líneas con print([DEBUG])
```

## 🚀 Próximas Características (Roadmap)

- [ ] 🌍 Soporte para más idiomas (árabe, hindi, coreano, tailandés)
- [ ] 📁 Upload de archivos PDF/DOCX directo
- [ ] 🔊 Síntesis de voz para traducciones
- [ ] 📊 Dashboard de estadísticas de uso
- [ ] 🌙 Modo oscuro/claro
- [ ] 🔌 API REST para integración con otros servicios
- [ ] 📱 Aplicación móvil (React Native)
- [ ] 🧠 Fine-tuning con modelos personalizados

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. **Fork** el proyecto
   ```bash
   # En GitHub, haz clic en "Fork"
   ```

2. **Clona tu fork**
   ```bash
   git clone https://github.com/TU_USUARIO/fundamentos-ai.git
   cd fundamentos-ai
   ```

3. **Crea una rama para tu feature**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Commit tus cambios**
   ```bash
   git commit -m "feat: Add amazing feature"
   ```

5. **Push a tu rama**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Abre un Pull Request**
   - [Abrir PR](https://github.com/CrisBocaz/fundamentos-ai/pulls)

## 📜 Licencia

Este proyecto está bajo la **Licencia MIT**.  
Eres libre de usar, modificar y distribuir este código con libertad.

Ver archivo [LICENSE](LICENSE) para más detalles.

## 💬 Soporte & Comunidad

¿Preguntas, bugs o sugerencias?

- 🐛 **Reportar un bug:** [Abrir issue](https://github.com/CrisBocaz/fundamentos-ai/issues/new)
- 💡 **Sugerir feature:** [Discusión](https://github.com/CrisBocaz/fundamentos-ai/discussions)
- 📧 **Email:** Contacto directo en GitHub

## 🙏 Agradecimientos

Construido con:
- 💙 **Google Gemini Team** - Modelos increíbles
- 🎨 **Gradio Team** - Framework web fantástico
- 📦 **ChromaDB Team** - Búsqueda vectorial eficiente

---

**⭐ Si te es útil, no olvides dejar una estrella!**

**Última actualización:** Mayo 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Estable y funcional

