# Stack Tecnológico Definitivo — Asistente de Bases Estándar

> Documento consolidado a partir de 8 investigaciones de IA (ChatGPT, Claude, Gemini, Perplexity) y decisiones del equipo técnico.

---

## 1. Filosofía del Stack

- **Python-first**: Todo el ecosistema backend, NLP, OCR y generación documental gira en torno a Python.
- **On-premise first**: Prioridad a tecnologías locales/auto-gestionables. Cloud solo como alternativa futura.
- **MVP rápido**: Streamlit como frontend inmediato; Angular 22 queda como meta técnica para producción.
- **Sin Docker** por restricciones corporativas (a futuro sí).
- **Sin CI/CD, sin observabilidad, sin gestión de secretos** en esta fase.

---

## 2. Mapa del Stack

| Capa | Tecnología | Versión | Rol | Estado |
|------|-----------|---------|-----|--------|
| **Frontend MVP** | Streamlit | >= 1.28 | UI rápida, wizard multipaso | ✅ Activo |
| **Frontend Producción** | Angular 21| 21.x | SPA corporativa completa | 🔮 Futuro |
| **Backend API** | FastAPI | >= 0.110 | API REST asíncrona, orquestación | ✅ Activo |
| **LLM Local** | Ollama + Gemma 3 1B | gemma3:1b | Extracción NLP local (testing) | ✅ Activo |
| **Base de Datos** | SQLite (PostgreSQL en prod) | 3.x / 16.x | Datos relacionales: expedientes, procesos, auditoría | ✅ Activo |
| **Vector DB** | Qdrant | >= 1.10 | Búsqueda semántica RAG, indexación de plantillas y normas | ✅ Activo |
| **Motor Plantillas** | docxtpl + python-docx | >= 1.0 (docxtpl) | Generación de documentos .docx desde plantillas Jinja2 | ✅ Activo |
| **OCR & Layout Local** | IBM Docling | >= 2.0 | Extracción de estructura, tablas y OCR de TDRs | ✅ Activo |
| **NLP / Reglas** | spaCy + Pydantic | >= 3.7 | Extracción determinista + validación estructurada | ✅ Activo |
| **Orquestación** | FastAPI + Celery + Redis | — | Colas de tareas asíncronas para procesos pesados (OCR, generación) | 🔮 Futuro |
| **IAM/SSO** | Keycloak | 25.x | Autenticación OAuth2/OIDC, RBAC | 📦 Implementación lista |
| **Protocolo IA** | FastMCP (MCP Server) | — | Exposición de herramientas a agentes de IA vía SSE | ✅ Activo |
| **SIGED** | Mock / Adapter | — | Simulación de endpoints REST; patrón Adapter + RPA documentado | ✅ Mock activo |
| **Almacenamiento** | Sistema de archivos local | — | Almacenamiento temporal de documentos (MinIO a futuro) | ✅ Activo |

---

## 3. Desglose Detallado por Componente

### 3.1 Frontend — Streamlit (MVP)

**Qué es**: Framework Python que convierte scripts en aplicaciones web interactivas sin necesidad de HTML/CSS/JS.

**Por qué**: Velocidad de prototipado. En una semana se tiene un wizard funcional de 12 pasos con estado, formularios y descarga de documentos.

**Limitaciones conocidas**:
- No es una SPA corporativa (sin routing real, sin lazy loading).
- Rendimiento degrada con muchos usuarios concurrentes.
- Personalización visual limitada frente a Angular/React.

**Migración futura**: Angular 22 cuando se requiera:
- Autenticación OAuth2 con Keycloak.
- Visor documental con trazabilidad campo-fuente.
- Roles y permisos granular por pantalla.
- Caching y SSR.

### 3.2 Backend — FastAPI (Python)

**Qué es**: Framework web asíncrono moderno con tipado, validación automática (Pydantic) y documentación OpenAPI.

**Por qué**:
- Ecosistema Python nativo para NLP (spaCy), LLM (Ollama), OCR (PaddleOCR).
- Rendimiento asíncrono (uvloop) sin necesidad de Docker.
- Documentación API autogenerada (/docs).
- Validación de datos con Pydantic integrada.

**Estructura esperada**:
```
backend/
  api/
    routes/
      expedientes.py
      procesos.py
      plantillas.py
    dependencies.py
  core/
    config.py
    database.py
    security.py
  services/
    siged_adapter.py    # Mock + Adapter REST
    ocr_service.py      # PaddleOCR (futuro)
    nlp_service.py      # spaCy + LLM
    template_engine.py  # docxtpl
  models/
    expediente.py
    proceso.py
    usuario.py
  schemas/
    expediente.py
    proceso.py
```

### 3.3 LLM Local — Ollama + Gemma 3 1B

**Qué es**: Gemma 3 1B es un modelo de lenguaje pequeño (1 billón de parámetros) de Google, ejecutado localmente vía Ollama.

**Propósito**: Extracción de campos estructurados del TDR usando JSON con Pydantic. Para testing y prototipado rápido.

**Limitaciones**:
- 1B params → precisión limitada en documentos complejos.
- No recomendado para producción.
- Para producción se migraría a Gemma 3 12B, Mistral 7B o Qwen 3.

**Uso**:
```python
import ollama
response = ollama.chat(model='gemma3:1b', messages=[
    {"role": "system", "content": "Extrae los campos del TDR en JSON"},
    {"role": "user", "content": texto_tdr}
])
```

### 3.4 Base de Datos — PostgreSQL 16

**Qué es**: Base de datos relacional ACID, madura, extensible.

**Por qué**: Soporte JSONB para datos semi-estructurados, extensibilidad para vectores (aunque usamos Qdrant), madurez en entornos públicos.

**Tablas mínimas**:
```sql
CREATE TABLE expedientes (
  id UUID PRIMARY KEY,
  numero_expediente VARCHAR(50) UNIQUE NOT NULL,
  datos_siged JSONB,
  fecha_consulta TIMESTAMPTZ,
  usuario_id UUID
);

CREATE TABLE procesos (
  id UUID PRIMARY KEY,
  expediente_id UUID REFERENCES expedientes(id),
  tipo_proceso VARCHAR(30),
  estado VARCHAR(20),
  datos_extraidos JSONB,
  datos_administrativos JSONB,
  plantilla_usada VARCHAR(100),
  documento_generado_url TEXT,
  creado_en TIMESTAMPTZ DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.5 Vector DB — Qdrant

**Qué es**: Base de datos vectorial especializada en búsqueda semántica (similarity search).

**Por qué**:
- Búsqueda híbrida (dense + sparse) para RAG.
- Self-hosted, sin dependencia cloud.
- API REST nativa, fácil de integrar con FastAPI.
- Buen rendimiento hasta millones de vectores.

**Uso en el proyecto**:
- Indexar plantillas de Bases (Bienes, Servicios, Consultoría).
- Indexar directivas OSCE y normas legales.
- RAG contextual: al extraer datos del TDR, buscar cláusulas relacionadas en las plantillas.

### 3.6 Motor de Plantillas — docxtpl + python-docx

**Qué es**: Librería Python que usa Jinja2 para reemplazar variables dentro de archivos .docx.

**Por qué**:
- Las plantillas son .docx reales editables por el área legal.
- Sintaxis Jinja2 familiar ({{ variable }}, {% if %}, {% for %}).
- Mantiene el formato original del documento Word.
- Gratuito (MIT).

**Ejemplo**:
```python
from docxtpl import DocxTemplate
doc = DocxTemplate("plantilla_bienes.docx")
context = { "objeto": "Servicio de limpieza", "monto": "150,000" }
doc.render(context)
doc.save("base_generada.docx")
```

### 3.7 OCR & Layout Analysis — IBM Docling

**Qué es**: Motor de Document Intelligence open source que convierte archivos PDF, DOCX e imágenes a Markdown estructurado conservando tablas y lectura ordenada, apoyándose en RapidOCR/EasyOCR de forma local.

**Ventajas**:
- Reconstruye tablas y formatos complejos.
- Soporta múltiples idiomas, incluido el español.
- Genera Markdown que es el formato óptimo de entrada para LLMs locales como Gemma 3.

**Estado**: ✅ Activo. Integrado en el backend y frontend para subida y procesamiento de archivos TDR locales en el MVP.

### 3.8 NLP — spaCy + Pydantic + LLM

**Enfoque híbrido** (consenso de todas las IA investigadas):

| Tipo de campo | Método | Ejemplo |
|--------------|--------|---------|
| **Campos estructurados** | spaCy + reglas (regex) | RUC, fechas, montos, plazos |
| **Campos semánticos** | Gemma 3 1B + structured output | Objeto de contratación, descripción |
| **Validación** | Pydantic schemas | Tipado, rangos, campos obligatorios |
| **Trazabilidad** | JSON con confianza por campo | { "campo": "...", "fuente": "página 3", "confianza": 0.95 } |

### 3.9 IAM — Keycloak

**Qué es**: Servidor de identidad open source (OAuth2/OIDC, SAML).

**Estado**: Implementación lista (docker-compose y config) pero no integrada con la app aún.

**Roles definidos**:
- `admin_sistema` — Gestión de usuarios, configuración.
- `operador_bases` — Crear/editar procesos de Bases.
- `revisor` — Solo lectura + aprobación.
- `auditor` — Solo lectura de logs.

### 3.10 SIGED — Mock + Patrón Adapter

**Escenario actual**: No tenemos acceso a la API real de SIGED. Se implementa un **Mock** que simula los endpoints necesarios.

**Patrón documentado** (`SIGEDAdapter`):
```python
class SIGEDAdapter:
    """Adaptador para integración con SIGED.
    
    Estrategias por escenario:
    1. API REST disponible → Cliente HTTP (httpx) con retry
    2. API SOAP → zeep + parser XML
    3. Sin API → Mock (actual) → Playwright RPA (futuro)
    """
    def consultar_expediente(self, numero: str) -> dict: ...
    def descargar_tdr(self, expediente_id: str) -> bytes: ...
```

**Mock actual**: Lee expedientes desde archivos JSON locales. Permite desarrollar y probar el flujo completo sin depender de SIGED.

### 3.11 MCP — FastMCP Server

**Se mantiene del prototipo original**. El servidor MCP expone herramientas a los agentes de IA a través del protocolo SSE (Server-Sent Events).

**Herramientas actuales**:
- Consulta de expedientes (mock).
- Generación de documentos (docxtpl a futuro).
- Validación de datos.

---

## 4. Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO                               │
│  Streamlit Web App (app.py) — Wizard 12 pasos           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              FASTAPI BACKEND (a implementar)            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SIGEDAdapter (Mock)                             │  │
│  │  → consultar_expediente()                        │  │
│  │  → descargar_tdr()                               │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  NLP Service                                     │  │
│  │  → spaCy + reglas (campos estructurados)         │  │
│  │  → Ollama + Gemma 3 1B (campos semánticos)       │  │
│  │  → Pydantic (validación)                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Template Engine                                 │  │
│  │  → docxtpl.render(contexto) → .docx              │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   DATOS                                  │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │  PostgreSQL    │  │  Qdrant        │                  │
│  │  (relacional)  │  │  (vectores)    │                  │
│  └────────────────┘  └────────────────┘                  │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │  FastMCP       │  │  Ollama        │                  │
│  │  (MCP Server)  │  │  (gemma3:1b)   │                  │
│  └────────────────┘  └────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Decisiones Clave y su Justificación

| Decisión | Opción elegida | Descartado | Por qué |
|----------|---------------|------------|---------|
| Frontend MVP | Streamlit | Angular 22 (futuro) | Velocidad de prototipado; Angular cuando haya Keycloak y visor documental |
| LLM | Gemma 3 1B | Mistral, Llama, Qwen | Único que corre en la máquina actual; suficiente para testing |
| Vector DB | Qdrant | pgvector, Weaviate, Milvus | Mejor balance rendimiento/simplicidad; self-hosted |
| Motor plantillas | docxtpl | Aspose.Words (pago) | Gratuito, mantiene formato, sintaxis Jinja2 |
| OCR | PaddleOCR (futuro) | Tesseract, Azure Doc Intelligence | Más preciso que Tesseract; on-premise; gratis |
| Orquestación | FastAPI directo | Temporal, Celery | Simplicidad para MVP; Temporal si hay flujos >24h |
| Base de datos | PostgreSQL | SQLite, MongoDB | ACID, JSONB, madurez institucional |
| IAM | Keycloak (listo) | Azure AD, AWS Cognito | Open source, OIDC, self-hosted |
| SIGED | Mock → Adapter | Integración directa | No hay API disponible; el patrón Adapter permite migrar sin reescribir |

---

## 6. Pendientes y Deuda Técnica Reconocida

| Ítem | Impacto | Plan |
|------|---------|------|
| Sin autenticación (Keycloak no integrado) | Bajo (MVP) | Tener config lista; integrar en fase Angular |
| Sin Docker | Medio (entorno manual) | Adoptar cuando TI corporativo lo autorice |
| Sin CI/CD | Medio (despliegues manuales) | No relevante para MVP |
| Sin observabilidad | Bajo (MVP) | Agregar logging básico; OpenTelemetry en producción |
| Sin gestión de secretos | Bajo (MVP) | Variables de entorno por ahora; Vault en producción |
| Gemma 3 1B es pequeño para producción | Alto | Probar Gemma 3 12B o Mistral 7B cuando haya GPU |
| Sin OCR (PaddleOCR) | Medio | Por ahora TDRs digitales; OCR cuando haya documentos escaneados reales |
| Sin Qdrant implementado | Medio | Arrancar con búsqueda simple; Qdrant cuando haya volumen |

---

## 7. Cómo Contribuir a Este Documento

- `stack.md` es la fuente de verdad del stack tecnológico. Cualquier cambio en herramientas, versiones o decisiones debe reflejarse aquí primero.
- Las decisiones técnicas deben incluir: qué se eligió, qué se descartó, y por qué.
- Mantener la tabla de "Decisiones Clave" actualizada.
- Este documento se alimenta de las investigaciones en `INVESTIGACION/`.

---

*Última actualización: Junio 2026*
*Versión: 1.0*
