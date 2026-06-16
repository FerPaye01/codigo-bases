# Stack Tecnológico, Arquitectura y Configuración del Proyecto (agent.md)

Este documento describe la arquitectura de software, el stack tecnológico, la configuración del entorno y los comandos esenciales para el proyecto **Asistente de Bases Estándar - Osinergmin**.

> 📖 Para el detalle completo de cada componente, decisiones y justificaciones, ver [`stack.md`](stack.md).

---

## 🛠️ Stack Tecnológico

El proyecto está construido sobre **Python** con un conjunto de librerías modernas de IA, procesamiento documental y desarrollo web rápido. Las elecciones concretas se consolidaron tras analizar 8 investigaciones de IA (ChatGPT, Claude, Gemini, Perplexity).

| Capa | Tecnología | Estado |
|------|-----------|--------|
| **Frontend MVP** | Streamlit | ✅ Activo |
| **Frontend Producción** | Angular 21 | 🔮 Futuro |
| **LLM Local** | Ollama + Gemma 3 1B | ✅ Activo (testing) |
| **Backend API** | FastAPI | ✅ Activo |
| **Base de Datos** | SQLite (PostgreSQL en prod) | ✅ Activo (persistencia relacional) |
| **Vector DB** | Qdrant | ✅ Activo (embebido local con fastembed) |
| **Motor Plantillas** | docxtpl + python-docx | ✅ Activo |
| **OCR / Layout** | IBM Docling | ✅ Activo |
| **NLP** | spaCy + reglas + Pydantic + LLM | ✅ Activo |
| **IAM** | Keycloak (config lista) | 📦 Preparado |
| **SIGED** | Mock + patrón Adapter | ✅ Mock activo |
| **Protocolo IA** | FastMCP (MCP Server SSE) | ✅ Activo |
| **Orquestación** | FastAPI directo (Celery+Redis a futuro) | 🔮 Futuro |
| **Almacenamiento** | Sistema de archivos local (MinIO a futuro) | ✅ Activo |

**Decisiones clave del stack** (ver `stack.md` sección 5 para el detalle completo):
- Streamlit para prototipado rápido; Angular 22 cuando haya Keycloak + visor documental.
- Gemma 3 1B porque es el único modelo que corre en la máquina actual. Suficiente para testing.
- Qdrant como vector DB (self-hosted, API REST nativa, búsqueda híbrida).
- docxtpl para plantillas .docx (gratuito, Jinja2, mantiene formato).
- SIGED con Mock ahora; patrón Adapter preparado para migrar a API REST o RPA sin reescribir.

---

## 🏗️ Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────┐
│           STREAMLIT WEB APP (app.py)                    │
│  Wizard de 12 pasos para generación de Bases           │
│  Visualización, confirmación y descarga de documentos   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              FASTAPI BACKEND (en desarrollo)             │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SIGED Adapter (Mock)                            │   │
│  │  → consultar_expediente(numero) → JSON           │   │
│  │  → descargar_tdr(expediente_id) → bytes          │   │
│  │  → Patrón: REST (httpx) → SOAP (zeep) → RPA      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  NLP Service (híbrido)                           │   │
│  │  → spaCy + reglas → campos estructurados         │   │
│  │  → Ollama + Gemma 3 1B → campos semánticos      │   │
│  │  → Pydantic → validación tipada                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Template Engine                                 │   │
│  │  → docxtpl(contexto) → .docx final               │   │
│  │  → Jinja2: {{ variable }}, {% if %}, {% for %}   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              CAPA DE DATOS                               │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  SQLite (Local)  │  │  Qdrant (Local)  │              │
│  │  - expedientes   │  │  - vectores      │              │
│  │  - procesos      │  │  - búsqueda      │              │
│  │  - auditoría     │  │    semántica     │              │
│  └──────────────────┘  └──────────────────┘              │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Ollama          │  │  FastMCP Server  │              │
│  │  (gemma3:1b)     │  │  (herramientas   │              │
│  │                  │  │   vía SSE)       │              │
│  └──────────────────┘  └──────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### Flujo del Asistente (12 pasos)

| Paso | Acción | Estado |
|:----:|--------|--------|
| 1 | Ingreso de expediente SIGED + selección de plantilla (Bienes/Servicios/Consultoría) | ✅ |
| 2 | Validación del expediente (Mock) | ✅ |
| 3 | Identificación y descarga del TDR digital | ✅ |
| 4 | Extracción con OCR/NLP de datos del TDR | ✅ |
| 5 | Visualización y corrección de datos técnicos extraídos | ✅ |
| 6 | Ingreso/Modificación de datos administrativos | ✅ |
| 7 | Configuración del cronograma de licitación | ✅ |
| 8 | Generación dinámica del borrador .docx | ✅ |
| 9 | Ajuste del documento según matrices de mapeo | ✅ |
| 10 | Revisión humana (checklist de validaciones) | ✅ |
| 11 | Descarga del borrador final en .docx | ✅ |
| 12 | Guardado en historial de expedientes | ✅ |

---

## 🧠 FastMCP — Servidor MCP

El servidor MCP (Model Context Protocol) se mantiene activo. Está implementado con **FastMCP** y expone herramientas a los agentes de IA a través del protocolo SSE.

**Ubicación**: `MCP/server.py`

**Herramientas actuales**:
- Consulta de expedientes (mock).
- Generación de documentos (a implementar con docxtpl).
- Validación de datos.

**Inicio**:
```bash
python MCP/server.py
```

---

## ⚙️ Configuración del Entorno

### 1. Prerrequisitos

- Python >= 3.10
- Git
- Ollama (con modelo `gemma3:1b` descargado)

### 2. Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
.\venv\Scripts\activate   # Windows
```

### 3. Dependencias

Instalación de las dependencias principales del MVP (incluyendo FastAPI, motor de OCR local, base de datos vectorial y motor de plantillas):
```bash
pip install streamlit pandas ollama mcp fastmcp rich pydantic fastapi uvicorn docling qdrant-client fastembed python-docx docxtpl requests
```

Dependencias de Producción (a futuro):
```bash
# PostgreSQL
pip install psycopg2-binary sqlalchemy

# IAM
# Keycloak OIDC client (a integrar)
```

### 4. Modelo Local (Ollama)

```bash
ollama pull gemma3:1b
```

---

## 🚀 Comandos de Ejecución

| Comando | Descripción |
|---------|------------|
| `streamlit run app.py` | Levantar portal web (Streamlit) |
| `uvicorn api:app --reload` | Levantar API backend (FastAPI) en puerto 8000 |
| `python MCP/server.py` | Iniciar servidor MCP en modo SSE |
| `python create_template.py` | Generar los 6 archivos de plantilla Word (.docx) |
| `python tests/test_api_new.py` | Ejecutar pruebas de la API y auditoría de base de datos |
| `python LLM/ollama_gemma3_demo.py` | Demo de extracción estructurada con Gemma 3 |
| `python LLM/ollama_mcp_client.py` | Cliente de demostración MCP |

---

## 📚 Referencias del Proyecto

- [`stack.md`](stack.md) — Documentación detallada de cada componente del stack, decisiones y justificaciones.
- [`mvp.md`](mvp.md) — Análisis estratégico del MVP, integración SIGED y riesgos.
- [`diccionario.md`](diccionario.md) — Glosario de términos (TDR, SIGED, GAF, GSTI).
- [`rules.md`](rules.md) — Reglas de codificación y comportamiento del agente.
- [`llm.md`](llm.md) — Estructura del proyecto y ubicación de información relevante.
- [`INVESTIGACION/`](INVESTIGACION/) — Las 8 investigaciones de IA que fundamentan las decisiones del stack.

---

*Última actualización: Junio 2026*
  ### 1. Servidores en Funcionamiento (Segundo Plano)                                                                                                                             
                                                                                                                                                                                  
  • Ollama Server: Levantado en la dirección local  http://127.0.0.1:11434  con el modelo  gemma3:1b  listo y cargado por  llama-server .                                         
      • Comando utilizado:                                                                                                                                                        
        OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=/data/proyectos/proyecto-bases/.ollama/models /data/proyectos/proyecto-bases/ollama_bin/bin/ollama serve                        
                                                                                                                                                                                  
  • FastAPI API Server: Levantado en  http://127.0.0.1:8000 . Conectado al backend de Ollama de forma automática.                                                                 
      • Comando utilizado:                                                                                                                                                        
        ./venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000                                                                                                                   
                                                                                                                                                                                  
      • Bitácora del servicio: task-227.log    

      uvicorn api:app --host 127.0.0.1 --port 8000 --reload