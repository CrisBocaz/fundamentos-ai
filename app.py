# -*- coding: utf-8 -*-
"""
AI Multi-Operation App
Operaciones: Traducción y QA (Preguntas & Respuestas)
Stack: Gradio · Gemini (google-genai) · ChromaDB
"""

import os
import sys
import re

# Forzar UTF-8 en stdout/stderr para evitar errores de codificación
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONUTF8", "1")
import gradio as gr
import google.genai as genai
import chromadb
from chromadb.utils.embedding_functions import GoogleGenaiEmbeddingFunction

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
MAX_CHARS = 5000

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

LANGUAGES = [
    "Español", "English", "Português", "Français",
    "Deutsch", "Italiano", "中文", "日本語", "Русский", "Árabe",
]

def sanitize(text: str) -> str:
    """Remove control characters and strip excess whitespace."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()

def validate_key(api_key: str) -> tuple[bool, str]:
    if not api_key or not api_key.strip():
        return False, "⚠️ Ingresa tu API Key de Gemini para continuar."
    if len(api_key.strip()) < 20:
        return False, "⚠️ La API Key parece inválida (muy corta)."
    return True, ""

def get_client(api_key: str):
    return genai.Client(api_key=api_key.strip())

def generate_with_fallback(client, prompt: str) -> str:
    import time
    last_err = ""
    for i, model in enumerate(GEMINI_MODELS):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text.strip()
        except Exception as e:
            err_msg = str(e)
            print(f"[FALLBACK] {model} falló: {err_msg}", flush=True)
            if "API_KEY" in err_msg.upper() or "INVALID" in err_msg.upper() or "401" in err_msg:
                raise
            if "404" in err_msg or "NOT_FOUND" in err_msg:
                continue  # modelo no disponible, saltar sin delay
            last_err = err_msg
            if i < len(GEMINI_MODELS) - 1:
                time.sleep(1)
    # Si todos fueron 404, last_err queda vacío
    raise RuntimeError(last_err or "Todos los modelos fallaron sin error registrado")

# ─────────────────────────────────────────────
# Operación 1: Traducción
# ─────────────────────────────────────────────

def translate_text(api_key: str, source_text: str, target_lang: str) -> str:
    ok, err = validate_key(api_key)
    if not ok:
        return err

    source_text = sanitize(source_text)
    if not source_text:
        return "⚠️ Por favor ingresa un texto para traducir."

    if len(source_text) > MAX_CHARS:
        source_text = source_text[:MAX_CHARS]
        warning = f"⚠️ El texto fue truncado a {MAX_CHARS} caracteres.\n\n"
    else:
        warning = ""

    try:
        client = get_client(api_key)
        prompt = (
            f"Traduce el siguiente texto al idioma: {target_lang}.\n"
            f"Responde SOLO con la traducción, sin explicaciones ni comentarios adicionales.\n\n"
            f"Texto a traducir:\n{source_text}"
        )
        print(f"[TRANSLATE] idioma={target_lang} | chars_texto={len(source_text)} | chars_prompt={len(prompt)}", flush=True)
        result = generate_with_fallback(client, prompt)
        print(f"[TRANSLATE OK] chars_respuesta={len(result)}", flush=True)
        return warning + result

    except Exception as e:
        err_msg = str(e)
        print(f"[TRANSLATE ERROR] {err_msg}", flush=True)
        if "API_KEY" in err_msg.upper() or "INVALID" in err_msg.upper() or "401" in err_msg:
            return "❌ API Key inválida o sin permisos. Verifica tu clave de Gemini."
        if "quota" in err_msg.lower() or "429" in err_msg:
            return "❌ Cuota de API agotada en todos los modelos. Intenta más tarde."
        return f"❌ Error: {err_msg}"


# ─────────────────────────────────────────────
# Operación 2: QA con ChromaDB
# ─────────────────────────────────────────────

# Estado global del índice (por sesión de servidor)
_chroma_state = {"client": None, "collection": None, "api_key": None, "doc_hash": None}

def _build_index(api_key: str, document: str):
    """Crea o reutiliza el índice ChromaDB para el documento dado."""
    doc_hash = str(hash(document + api_key))
    if (
        _chroma_state["collection"] is not None
        and _chroma_state["doc_hash"] == doc_hash
    ):
        return _chroma_state["collection"]

    # Fragmentar el documento en chunks de ~500 caracteres con overlap
    chunk_size = 500
    overlap = 80
    chunks = []
    start = 0
    while start < len(document):
        end = min(start + chunk_size, len(document))
        chunks.append(document[start:end])
        start += chunk_size - overlap
        if start >= len(document):
            break

    os.environ["GEMINI_API_KEY"] = api_key.strip()
    ef = GoogleGenaiEmbeddingFunction(
        model_name="gemini-embedding-001",
        task_type="RETRIEVAL_DOCUMENT",
        api_key_env_var="GEMINI_API_KEY",
    )

    chroma_client = chromadb.Client()
    # Borrar colección anterior si existe
    try:
        chroma_client.delete_collection("qa_docs")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name="qa_docs",
        embedding_function=ef,
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

    _chroma_state["client"] = chroma_client
    _chroma_state["collection"] = collection
    _chroma_state["api_key"] = api_key
    _chroma_state["doc_hash"] = doc_hash
    return collection


def answer_question(api_key: str, document: str, question: str) -> str:
    ok, err = validate_key(api_key)
    if not ok:
        return err

    document = sanitize(document or "")
    question = sanitize(question or "")

    if not document:
        return "⚠️ Por favor pega el texto del documento antes de hacer una pregunta."
    if not question:
        return "⚠️ Por favor ingresa una pregunta."
    if len(document) > MAX_CHARS:
        document = document[:MAX_CHARS]

    try:
        collection = _build_index(api_key, document)

        os.environ["GEMINI_API_KEY"] = api_key.strip()
        ef_query = GoogleGenaiEmbeddingFunction(
            model_name="gemini-embedding-001",
            task_type="RETRIEVAL_QUERY",
            api_key_env_var="GEMINI_API_KEY",
        )
        query_emb = ef_query([question])

        results = collection.query(
            query_embeddings=query_emb,
            n_results=min(3, collection.count()),
        )
        context_chunks = results["documents"][0] if results["documents"] else [document[:1000]]
        context = "\n\n---\n\n".join(context_chunks)

        client = get_client(api_key)
        prompt = (
            "Eres un asistente experto en análisis de documentos. "
            "Responde la pregunta del usuario ÚNICAMENTE basándote en el contexto proporcionado. "
            "Si la respuesta no está en el contexto, dilo claramente. "
            "Sé detallado y preciso en tu respuesta.\n\n"
            f"CONTEXTO DEL DOCUMENTO:\n{context}\n\n"
            f"PREGUNTA: {question}\n\n"
            "RESPUESTA:"
        )
        return generate_with_fallback(client, prompt)

    except Exception as e:
        err_msg = str(e)
        print(f"[QA ERROR] {err_msg}", flush=True)
        if "API_KEY" in err_msg.upper() or "INVALID" in err_msg.upper() or "401" in err_msg:
            return "❌ API Key inválida o sin permisos. Verifica tu clave de Gemini."
        if "quota" in err_msg.lower() or "429" in err_msg:
            return "❌ Cuota de API agotada en todos los modelos. Intenta más tarde."
        return f"❌ Error: {err_msg}"


# ─────────────────────────────────────────────
# UI — Gradio
# ─────────────────────────────────────────────

CSS = """
/* ── MODERNO & COLORIDO DESIGN ── */
:root {
    --primary: #6366f1;
    --primary-light: #eef2ff;
    --primary-dark: #4f46e5;
    --text: #1a1a1a;
    --text-light: #666666;
    --bg: #ffffff;
    --bg-alt: #f8f9fa;
    --border: #e5e7eb;
    --accent: #000000;
    --success: #10b981;
}

/* Hide Gradio footer */
footer { display: none !important; }

/* Page background - clean white */
gradio-app, .gradio-container {
    background: white !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Header - modern with gradient */
.app-header {
    text-align: center;
    padding: 3rem 1rem 2.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.app-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0 0 0.5rem;
    letter-spacing: 0;
}
.app-header p {
    color: var(--text-light);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 400;
}

/* API Key Row - flexible layout */
#api-key-row {
    width: 100% !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 0.5rem !important;
}

/* Botón toggle key - pequeño y alineado */
.btn-toggle-key {
    align-self: center !important;
    margin: 0 !important;
}
.btn-toggle-key button {
    padding: 0 !important;
    font-size: 1rem !important;
    min-width: 36px !important;
    max-width: 36px !important;
    width: 36px !important;
    height: 36px !important;
    box-shadow: none !important;
    background: var(--bg-alt) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    line-height: 1 !important;
}
.btn-toggle-key button:hover {
    background: var(--primary-light) !important;
    box-shadow: none !important;
}

/* API key box - modern */
.key-box {
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px !important;
    padding: 0.65rem 1rem;
    margin: 0.75rem 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07) !important;
}

/* Tabs - modern and prominent */
.tab-nav {
    border-bottom: 3px solid var(--primary) !important;
    gap: 0 !important;
    padding: 0 2rem !important;
    background: white !important;
}
.tab-nav button {
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: var(--text-light) !important;
    border-radius: 0 !important;
    transition: all 0.3s ease !important;
    padding: 1.5rem 2.5rem !important;
    border: none !important;
    background: white !important;
    margin-bottom: -3px !important;
    box-shadow: none !important;
}
/* Tab hover — ambos selectores para local y HF Spaces */
.tab-nav button:hover:not(.selected),
.tab-nav button[aria-selected="false"]:hover {
    background: var(--primary-light) !important;
    color: var(--text) !important;
}
/* Tab activo — .selected (local) y aria-selected (HF Spaces / Gradio 6) */
.tab-nav button.selected,
.tab-nav button[aria-selected="true"] {
    color: var(--primary) !important;
    background: white !important;
    border-bottom: 4px solid var(--primary) !important;
    box-shadow: none !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}

/* Buttons — primarios (Traducir, Responder) */
/* Gradio 6: variant="primary" → button.primary  |  legacy: .gr-button-primary */
button.primary,
.gr-button-primary,
button[data-testid="button"].primary {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2) !important;
}
button.primary:hover,
.gr-button-primary:hover,
button[data-testid="button"].primary:hover {
    background: var(--primary-dark) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}
button.primary:focus,
.gr-button-primary:focus {
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
}

/* Botones secundarios (toggle, sm) */
button.secondary,
.gr-button-secondary {
    background: white !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}
button.secondary:hover,
.gr-button-secondary:hover {
    background: var(--primary-light) !important;
    border-color: var(--primary) !important;
}

/* Char counter */
.char-counter {
    font-size: 0.75rem;
    color: var(--text-light);
    text-align: right;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
.char-counter.warn { color: #d32f2f; font-weight: 600; }

/* Output boxes - modern styling */
.output-box textarea {
    background: white !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 0.9rem !important;
    color: var(--text) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07) !important;
}
.gr-box {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07) !important;
}

/* All Gradio containers - color uniforme */
.gr-panel, .gradio-container, [data-testid="column"] {
    background: white !important;
}
.gr-group {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07) !important;
}

/* NUCLEAR CSS - Override Gradio's entire styling */
.gr-form-group, .gr-block, .gr-form {
    background: white !important;
    border: none !important;
}

.gr-form-group > *, .gr-block > * {
    background: white !important;
    border: 1px solid var(--border) !important;
}

/* Force white background on ALL divs and wrappers */
div[class*="gr-"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

fieldset {
    background: white !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* Specific Gradio component wrappers */
.gr-textbox-wrapper, .gr-number-wrapper, .gr-dropdown-wrapper,
.gradio-textbox, .gradio-number, .gradio-dropdown,
.gr-textbox, .gr-number, .gr-dropdown {
    background: white !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* Remove ALL dark backgrounds and borders */
[style*="background: rgb"], [style*="background-color"],
[style*="border: rgb"], [style*="border-color"] {
    background: white !important;
    border-color: var(--border) !important;
}

/* Labels - clean */
label span {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* EXTREME COLOR OVERRIDE - All inputs white */
* {
    --input-background-fill: white !important;
    --input-background-fill-focus: white !important;
    --input-border-color: var(--border) !important;
    --input-text-color: var(--text) !important;
}

textarea, input, select {
    background: white !important;
    border-radius: 4px !important;
    border: 1.5px solid var(--border) !important;
    font-size: 0.9rem !important;
    color: var(--text) !important;
    transition: all 0.2s ease !important;
}

textarea:focus, input:focus, select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
    background: white !important;
}

input[type="text"], input[type="password"], input[type="number"], input[type="email"] {
    background: white !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 4px !important;
}

textarea {
    background: white !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 4px !important;
}

select, select option {
    background: white !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 4px !important;
}

/* Gradio-specific selectors */
.gr-textbox input, .gr-number input, .gr-dropdown select {
    background: white !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

.gr-textbox, .gr-number, .gr-dropdown {
    background: white !important;
}

/* Override autofill */
input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px white inset !important;
    -webkit-text-fill-color: var(--text) !important;
}

/* Info callout - modern */
.info-tip {
    background: var(--primary-light);
    border-left: 3px solid var(--primary);
    border-radius: 4px;
    padding: 1rem 1rem 1rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 1rem;
}

/* Lock banner */
.lock-banner {
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: 0;
    padding: 1rem;
    color: var(--text-light);
    font-size: 0.85rem;
    font-weight: 400;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Placeholder translation */
.translate-waiting {
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: 0;
    padding: 2rem;
    text-align: center;
    color: var(--text-light);
    font-size: 0.85rem;
    margin-top: 1.5rem;
}
.translate-waiting .tw-icon { font-size: 2.5rem; display: block; margin-bottom: 0.75rem; }
.translate-waiting strong { display: block; color: var(--text); margin-bottom: 0.5rem; font-size: 0.9rem; }

/* Step indicators */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 0.75rem;
}
.step-badge {
    background: var(--primary);
    color: white;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 600;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}
.step-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.step-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0 1.5rem;
}

/* ── Modal API Key ── */
.api-key-modal {
    display: flex;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.api-key-modal.hidden {
    display: none;
}

.api-key-modal-content {
    background: white;
    border-radius: 8px;
    padding: 2.5rem;
    max-width: 450px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.api-key-modal h2 {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
}

.api-key-modal p {
    margin: 0 0 1.5rem;
    font-size: 0.95rem;
    color: var(--text-light);
}

.api-key-modal-input-group {
    margin-bottom: 1.5rem;
}

.api-key-modal-input-group label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--text);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.api-key-modal-input-wrapper {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

.api-key-modal-input-wrapper input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 1.5px solid var(--border);
    border-radius: 4px;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.api-key-modal-input-wrapper input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.api-key-modal-buttons {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

.api-key-modal-btn-accept {
    padding: 0.75rem 2rem;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}

.api-key-modal-btn-accept:hover {
    background: var(--primary-dark);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.api-key-modal-btn-accept:disabled {
    background: var(--border);
    cursor: not-allowed;
    box-shadow: none;
}

.api-key-modal-error {
    color: #ef4444;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    display: none;
}

.api-key-modal-error.show {
    display: block;
}
"""

def toggle_tabs(api_key: str):
    """Enable or disable tabs based on API key presence."""
    ok, _ = validate_key(api_key)
    return (
        gr.update(interactive=ok),   # btn_translate
        gr.update(interactive=ok),   # btn_qa
        gr.update(visible=not ok),   # key_error
        gr.update(visible=ok),       # key_ok_msg
        gr.update(interactive=ok),   # source_lang
        gr.update(interactive=ok),   # src_text
        gr.update(interactive=ok),   # target_lang
        gr.update(interactive=ok),   # doc_text
        gr.update(interactive=ok),   # question_input
    )

def char_count(text: str) -> str:
    n = len(text) if text else 0
    cls = "char-counter warn" if n > MAX_CHARS else "char-counter"
    return f'<span class="{cls}">{n:,} / {MAX_CHARS:,} caracteres</span>'



JS = """
(function() {
    function attachToggle() {
        const btn = document.querySelector('button.btn-toggle-key');
        if (!btn || btn.dataset.toggleReady) return;
        btn.dataset.toggleReady = '1';
        btn.addEventListener('click', function(e) {
            e.stopImmediatePropagation();
            const input = document.querySelector('input[data-testid="password"]');
            if (!input) return;
            input.type = input.type === 'password' ? 'text' : 'password';
            btn.textContent = input.type === 'password' ? '👁' : '🙈';
        }, true);
    }
    // Ejecutar inmediatamente y con MutationObserver para cuando Gradio renderice
    attachToggle();
    new MutationObserver(attachToggle).observe(document.body, {childList:true, subtree:true});
})();
"""

with gr.Blocks(title="AI Multi-Op · Gemini") as demo:

    # ── CSS extra para forzar tema claro ──
    gr.HTML('<style>' +
            '*:not(svg){background:white!important;border-color:#e0e0e0!important;color:#1a1a1a!important;}' +
            '</style>')

    # ── Modal API Key (REMOVIDO - se usa campo en la página) ──
    gr.HTML("""
    <div id="apiKeyModal" class="api-key-modal" style="display: none !important; visibility: hidden;">
        <div class="api-key-modal-content">
            <h2>🔐 API Key</h2>
            <p>Ingresa tu API Key de Google Gemini para comenzar.</p>

            <div class="api-key-modal-input-group">
                <label>API Key</label>
                <div class="api-key-modal-input-wrapper">
                    <input
                        type="text"
                        id="modalApiKeyInput"
                        placeholder="AIza..."
                        autocomplete="off"
                        style="flex: 1; padding: 0.75rem 1rem; border: 1.5px solid #e5e7eb; border-radius: 4px; font-size: 0.9rem;"
                    />
                </div>
                <div id="apiKeyError" class="api-key-modal-error">
                    ⚠️ Por favor ingresa una API Key válida.
                </div>
            </div>

            <div class="api-key-modal-buttons">
                <button
                    class="api-key-modal-btn-accept"
                    id="acceptKeyBtn"
                    type="button"
                >
                    Aceptar
                </button>
            </div>
        </div>
    </div>

    <script>
    // Mantener modal oculto
    window.addEventListener('load', function() {
        const modal = document.getElementById('apiKeyModal');
        if (modal) {
            modal.style.display = 'none !important';
            modal.style.visibility = 'hidden';
        }
    });
    document.getElementById('apiKeyModal').style.display = 'none !important';

    // Toggle visibilidad API Key — MutationObserver para detectar el botón
    (function() {
        function attachToggle(btn) {
            if (btn.dataset.toggleReady) return;
            btn.dataset.toggleReady = '1';
            btn.addEventListener('click', function(e) {
                e.stopImmediatePropagation();
                const input = document.querySelector('input[data-testid="password"]');
                if (!input) return;
                input.type = input.type === 'password' ? 'text' : 'password';
                btn.textContent = input.type === 'password' ? '👁' : '🙈';
            }, true);
        }
        // Intentar inmediatamente
        const existing = document.querySelector('button.btn-toggle-key');
        if (existing) { attachToggle(existing); }
        // Observar el DOM para cuando Gradio renderice el botón
        const observer = new MutationObserver(function() {
            const btn = document.querySelector('button.btn-toggle-key');
            if (btn) { attachToggle(btn); }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """)

    # ── Header ──
    gr.HTML("""
    <div class="app-header">
        <h1>✦ AI Multi-Operation</h1>
        <p>Traducción inteligente y QA sobre documentos · Powered by Gemini</p>
    </div>
    """)

    # ── API Key ──
    with gr.Group(elem_classes="key-box"):
        gr.HTML('<label style="font-size:0.8rem;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:0.1em;">API Key de Google Gemini</label>')
        with gr.Row(equal_height=False, elem_id="api-key-row"):
            api_key_input = gr.Textbox(
                placeholder="AIza...",
                type="password",
                max_lines=1,
                show_label=False,
                container=False,
                visible=True,
            )
            btn_key_toggle = gr.Button("👁", scale=0, min_width=44, size="sm", elem_classes="btn-toggle-key")
        key_error = gr.HTML(
            '<div style="color:#ef4444;font-size:1rem;margin-top:4px;font-weight:500;">'
            '⚠️ Primero, ingresa tu API Key para habilitar las operaciones.'
            '</div>',
            visible=True,
        )
        key_ok_msg = gr.HTML(
            '<div style="color:#16a34a;font-size:1rem;margin-top:4px;font-weight:500;">'
            '✅ API Key ingresada. Puedes usar las operaciones.'
            '</div>',
            visible=False,
        )

    # ── Tabs ──
    with gr.Tabs() as tabs:

        # ════════════════════════════════════════
        # Tab 1: Traducción
        # ════════════════════════════════════════
        with gr.Tab("🌐  Traducción", id="tab_translate") as tab_translate:

            gr.HTML('<div class="info-tip">Ingresa texto en cualquier idioma y selecciona el idioma de destino. <span style="color:#888;font-style:italic;">Ej: "La inteligencia artificial está transformando la manera en que trabajamos..." → En Idioma Destino a English → Presionar Traducir.</span></div>')

            with gr.Row():
                with gr.Column(scale=1):
                    source_lang = gr.Dropdown(
                        choices=LANGUAGES,
                        value="Español",
                        label="Idioma origen",
                        interactive=False,
                    )
                    src_text = gr.Textbox(
                        label="Texto original",
                        placeholder="Pega o escribe el texto que deseas traducir...",
                        lines=8,
                        max_lines=20,
                        interactive=False,
                    )
                    char_html_t = gr.HTML('<span class="char-counter">0 / 5,000 caracteres</span>')

                with gr.Column(scale=0, min_width=120):
                    gr.HTML('<div style="height: 2rem;"></div>')
                    btn_translate = gr.Button("Traducir →", variant="primary", interactive=False)

                with gr.Column(scale=1):
                    target_lang = gr.Dropdown(
                        choices=LANGUAGES,
                        value="English",
                        label="Idioma destino",
                        interactive=False,
                    )
                    translation_output = gr.Textbox(
                        label="Traducción",
                        lines=10,
                        interactive=False,
                        elem_classes="output-box",
                        placeholder="La traducción aparecerá aquí...",
                    )

            src_text.change(fn=char_count, inputs=src_text, outputs=char_html_t, queue=False, show_progress=False)
            btn_translate.click(
                fn=translate_text,
                inputs=[api_key_input, src_text, target_lang],
                outputs=translation_output,
            )

        # ════════════════════════════════════════
        # Tab 2: QA — Preguntas & Respuestas
        # ════════════════════════════════════════
        with gr.Tab("📄  QA — Preguntas & Respuestas", id="tab_qa") as tab_qa:

            gr.HTML(
                '<div class="info-tip">'
                'Sigue los 3 pasos: pega el documento, escribe tu pregunta y obtén la respuesta. '
                'ChromaDB indexa el texto para búsqueda semántica eficiente. '
                '<span style="color:#888;font-style:italic;">Ej: Paso 1: pega un artículo / Paso 2: Haz la pregunta → Paso 3: Presionar Responder.</span>'
                '</div>'
            )

            # Paso 1 - Documento
            gr.HTML(
                '<div class="step-header">'
                '<span class="step-badge">1</span>'
                '<span class="step-title">Pega el documento</span>'
                '</div>'
            )
            doc_text = gr.Textbox(
                label="Documento",
                placeholder="Pega aquí el contenido del documento sobre el que quieres hacer preguntas...",
                lines=7,
                max_lines=15,
                visible=True,
                interactive=False,
            )
            char_html_q = gr.HTML('<span class="char-counter">0 / 5,000 caracteres</span>', visible=True)

            # Paso 2 - Pregunta
            gr.HTML(
                '<hr class="step-divider">'
                '<div class="step-header">'
                '<span class="step-badge">2</span>'
                '<span class="step-title">Escribe tu pregunta</span>'
                '</div>'
            )
            question_input = gr.Textbox(
                label="Pregunta",
                placeholder="¿Cuál es el tema principal del documento?",
                lines=2,
                max_lines=4,
                interactive=False,
            )

            btn_qa = gr.Button("Responder →", variant="primary", interactive=False)

            # Paso 3 - Respuesta
            gr.HTML(
                '<hr class="step-divider">'
                '<div class="step-header">'
                '<span class="step-badge">3</span>'
                '<span class="step-title">Obtén la respuesta</span>'
                '</div>'
            )
            answer_output = gr.Textbox(
                label="Respuesta del asistente",
                lines=10,
                interactive=True,
                elem_classes="output-box",
                placeholder="La respuesta aparecerá aquí...",
            )

            doc_text.change(fn=char_count, inputs=doc_text, outputs=char_html_q, queue=False, show_progress=False)
            btn_qa.click(
                fn=answer_question,
                inputs=[api_key_input, doc_text, question_input],
                outputs=answer_output,
            )

    # ── Key validation on change ──
    api_key_input.change(
        fn=toggle_tabs,
        inputs=api_key_input,
        outputs=[btn_translate, btn_qa, key_error, key_ok_msg, source_lang, src_text, target_lang, doc_text, question_input],
        queue=False,
        show_progress="hidden",
    )


    gr.HTML("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;color:#94a3b8;font-size:0.75rem;">
        Desarrollado con Gradio · Gemini · ChromaDB &nbsp;|&nbsp; Los datos no se almacenan
    </div>
    """)



if __name__ == "__main__":
    demo.launch(
        css=CSS,
        js=JS,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
