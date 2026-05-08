# Fundamentos AI 🚀

Aplicación de traducción y QA con Gemini API

Una aplicación web moderna construida con **Gradio 6.0** que proporciona dos funcionalidades principales:
- 🌐 **Traducción Inteligente** - Traduce textos entre múltiples idiomas
- 📄 **Q&A sobre Documentos** - Responde preguntas basadas en documentos subidos

## Características

### Traducción
- Soporte para múltiples idiomas
- Interfaz intuitiva con selección de idioma origen/destino
- Procesamiento en tiempo real

### Q&A (Preguntas y Respuestas)
- Carga de documentos en texto
- Búsqueda semántica con ChromaDB
- Respuestas contextuales basadas en el contenido del documento
- Soporte para múltiples modelos de Gemini con fallback automático

### Seguridad & Confiabilidad
- **Fallback automático de modelos** - Si un modelo no está disponible, intenta con otros
- **Autenticación con API Key** - Control de acceso mediante API Key de Google Gemini
- **Validación de entrada** - Encriptación de API Key durante la sesión
- **Manejo robusto de errores** - Mensajes claros para el usuario

## Modelos Soportados

La aplicación utiliza un sistema de fallback con estos modelos:
1. `gemini-2.5-flash` (primario)
2. `gemini-2.5-flash-lite`
3. `gemini-2.0-flash`
4. `gemini-2.0-flash-lite` (fallback final)

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/CrisBocaz/fundamentos-ai.git
cd fundamentos-ai

# Crear ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar la aplicación
PYTHONUTF8=1 python3 app.py
```

La aplicación se abrirá en `http://localhost:7860`

### Flujo de uso:

1. **Ingresar API Key** - En la sección superior, ingresa tu API Key de Google Gemini
2. **Elegir operación:**
   - **Traducción**: Pega texto, selecciona idioma destino, presiona traducir
   - **Q&A**: Carga un documento, escribe tu pregunta, obtén respuesta

## Validar Modelos

Para verificar qué modelos están disponibles con tu API Key:

```bash
python3 check_models.py
# O con tu API Key como argumento
python3 check_models.py "tu-api-key-aqui"
```

## API Key de Gemini

1. Ir a [Google AI Studio](https://aistudio.google.com/apikey)
2. Crear una nueva API Key
3. Copiar y pegar en la sección "API Key de Google Gemini"

## Estructura del Proyecto

```
fundamentos-ai/
├── app.py              # Aplicación principal (Gradio)
├── check_models.py     # Script para validar modelos disponibles
├── requirements.txt    # Dependencias de Python
├── .gitignore         # Archivos ignorados en Git
└── README.md          # Este archivo
```

## Tecnologías

- **Gradio 6.0** - Framework web para ML
- **Google Gemini API** - Modelos de IA generativa
- **ChromaDB** - Base de datos vectorial para búsqueda semántica
- **Python 3** - Lenguaje principal

## Configuración de Seguridad

### .gitignore
El proyecto incluye un `.gitignore` que protege:
- **`.env`** - Variables de entorno (API keys)
- **`*.log`** - Archivos de log
- **`__pycache__/`** - Archivos compilados de Python
- **`venv/`** - Ambiente virtual

**IMPORTANTE:** Nunca commitees tu API Key. Úsala como variable de entorno.

## Manejo de Errores

La aplicación maneja automáticamente:
- ✅ **Cuota agotada** - Intenta con siguiente modelo
- ✅ **Modelo no disponible** - Fallback a modelo alternativo
- ✅ **API Key inválida** - Mensaje claro al usuario
- ✅ **Documento vacío** - Validación de entrada

## Logs

Durante el desarrollo, la aplicación imprime logs en la consola para debug:
```
[TRANSLATE] idioma=Spanish | chars_texto=150
[QA] documento=1500 chars | pregunta=50 chars
[FALLBACK] gemini-2.0-flash falló: 429 RESOURCE_EXHAUSTED
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## Soporte

¿Preguntas o problemas? Abre un [issue](https://github.com/CrisBocaz/fundamentos-ai/issues) en GitHub.

---

**Desarrollado con ❤️ usando Google Gemini API**
