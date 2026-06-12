# Investigación de Arquitectura Tecnológica para Asistentes de IA
## Asistente de Bases Estándar y Asistente de Contratos — Entidad Pública
**Fecha:** Junio 2026 | **Clasificación:** Reservado — Uso Interno

---

# A. RESUMEN EJECUTIVO

## Contexto
Se propone el diseño desde cero de dos asistentes de IA para automatizar la generación documental en procesos de contratación pública:

1. **Asistente IA de Bases Estándar**: Extrae información de TDR vía OCR/NLP, permite ingreso administrativo por el usuario y genera automáticamente el documento de bases en formato `.docx` usando plantillas predefinidas (bienes, servicios, consultoría, normal/abreviado).

2. **Asistente IA de Contratos**: Procesa múltiples documentos fuente (Bases Integradas, Oferta Económica, Oferta Técnica, Vigencia de Poder, Garantía), valida consistencia cruzada entre ellos y genera el contrato en `.docx` con revisión humana obligatoria.

## Hallazgos Principales

| Dimensión | Recomendación Principal |
|---|---|
| OCR | Azure AI Document Intelligence (custom model) como principal; PaddleOCR como fallback on-premise |
| LLM | Azure OpenAI (GPT-4o) para cloud; Mistral Large 3 / Qwen 3.5-72B para on-premise |
| Vector DB | PostgreSQL + pgvector para MVP; Qdrant para producción |
| Orquestación | LangChain + FastAPI (MVP); Temporal + microservicios (producción) |
| Plantillas | docxtpl (Python) como motor principal |
| Infraestructura MVP | Docker Compose on-premise o Azure Container Apps |
| Infraestructura Producción | Kubernetes (AKS/EKS) o Azure Container Apps + App Gateway |

## Decisión Estratégica Clave

> **Iniciar con Bases antes que Contratos** es la decisión correcta. El caso de Bases tiene un flujo determinista (1 TDR → 1 plantilla → 1 salida), permite validar la pila tecnológica con bajo riesgo y genera valor rápido. Contratos requiere validación cruzada multidocumento, lógica legal compleja y revisión normativa, lo que justifica su implementación en una fase posterior con la experiencia acumulada.

## Riesgo Crítico

> La entidad puede tener restricciones para enviar documentos sensibles a servicios en nube pública. **Este factor debe resolverse antes de seleccionar cualquier proveedor cloud**. La arquitectura propuesta contempla escenarios híbridos y totalmente on-premise.

---

# B. TABLA COMPARATIVA POR COMPONENTE

---

## Componente 1: Frontend / Interfaz de Usuario

| Atributo | AWS | Azure | Open Source / On-Premise |
|---|---|---|---|
| **Alternativa** | React + Amplify Hosting | React + Azure Static Web Apps | React + Nginx / Vue.js self-hosted |
| **Chatbot** | Amazon Lex (básico, en inglés principalmente) | Azure Bot Service + Copilot Studio | Rasa, Botpress, custom chat con React |
| **Formularios dinámicos** | AWS AppSync + Amplify | Power Apps (low-code) | React Hook Form + Formik + shadcn/ui |
| **Visor documental** | Amazon S3 + pre-signed URLs + PDF.js | Azure Blob + PDF.js / MS Office Online | PDF.js, react-pdf, DocxPreviewer |
| **Ventajas** | Integración nativa con S3/Lambda; hosting gestionado | Integración con Azure AD; Power Platform low-code | Control total; sin costo de licencia; portable |
| **Desventajas** | Amplify puede ser overkill; Lex limitado en español | Power Apps agrega complejidad; Copilot Studio requiere licencia | Mayor esfuerzo de desarrollo y mantenimiento |
| **MVP** | React + FastAPI backend + pre-signed URL para descarga | React + Azure Static Web Apps + Azure AD | **React + Nginx + Docker** (recomendado MVP) |
| **Producción** | React + CloudFront + WAF + Cognito | React + Azure Front Door + Azure AD B2C | React + Kubernetes Ingress + OAuth2 Proxy |
| **Complejidad** | Media | Media | Baja (MVP) / Media (producción) |
| **Riesgos** | Dependencia de Amplify CLI; Lex pobre en español | Power Apps puede encasillar el diseño; vendor lock-in | Requiere equipo frontend competente |

**Recomendación**: Para el MVP usar **React + TypeScript** con componentes de `shadcn/ui` o `Ant Design`, servido desde Nginx en Docker. Para el visor de documentos usar `react-pdf` (PDF.js) y para previsualización de .docx usar `mammoth.js` o conversión a HTML en backend. Evitar soluciones low-code como Power Apps que dificultan la integración con lógica compleja.

---

## Componente 2: Backend / Orquestador

| Atributo | AWS | Azure | Open Source / On-Premise |
|---|---|---|---|
| **Serverless** | Lambda + API Gateway + Step Functions | Azure Functions + Logic Apps + Durable Functions | — (no aplica on-premise puro) |
| **Microservicios** | ECS/EKS + API Gateway | AKS + API Management | FastAPI / NestJS en Kubernetes |
| **Orquestación flujos** | Step Functions (ASL JSON) | Durable Functions (código) / Logic Apps | **Temporal** (workflows duraderos), Prefect |
| **Framework API** | FastAPI en Lambda (Mangum) | FastAPI en Azure Functions | **FastAPI** (Python), NestJS (Node.js) |
| **Ventajas AWS** | Escalado automático; integración nativa S3/Textract | Integración Azure AD; Durable Functions para workflows complejos | Control total; no hay egress fees |
| **Desventajas** | Step Functions tiene límite de payload (256KB); cold start en Lambda | Durable Functions requiere aprender modelo de programación reactivo | Requiere infraestructura propia; más ops |
| **MVP** | FastAPI en ECS Fargate (single container) | FastAPI en Azure Container Apps | **FastAPI + Docker Compose** (recomendado) |
| **Producción** | FastAPI + Celery en EKS + SQS | FastAPI + Temporal en AKS | FastAPI + Temporal + Kubernetes |
| **Complejidad** | Media | Media | Baja (MVP) / Alta (producción con Temporal) |
| **Riesgos** | Límite de tamaño en Step Functions para documentos grandes; vendor lock-in ASL | Durable Functions en Python aún menos maduro que .NET | Temporal requiere equipo con curva de aprendizaje |

**Recomendación**: Para MVP usar **FastAPI (Python)** con Celery + Redis para tareas asíncronas (OCR, generación documental). Para producción escalar a **Temporal** como orquestador de workflows duraderos con retry automático, que es crítico cuando hay llamadas a SIGED que pueden fallar. FastAPI es la opción más productiva para el equipo dado que toda la pila de NLP/OCR es Python.

---

## Componente 3: Integración con SIGED

| Atributo | Opción API REST disponible | Opción API SOAP/legacy | Sin API disponible |
|---|---|---|---|
| **Patrón** | Cliente HTTP (httpx/requests) con retry exponencial | Cliente SOAP (zeep, suds) con parser XML | Web scraping controlado o carga manual |
| **Autenticación** | OAuth2 / API Key / JWT institucional | WS-Security / Basic Auth | Credenciales de sesión web (riesgo alto) |
| **Descarga archivos** | Stream directo a S3/MinIO o disco temporal | MTOM/SOAP con adjuntos binarios | Selenium/Playwright headless + download |
| **Manejo de errores** | Circuit breaker (Tenacity), timeout, dead-letter queue | Timeout estricto, parser tolerante | Fragil: requiere monitoreo activo |
| **Auditoría** | Log de cada request/response con timestamp y usuario | Log de envelope SOAP | Screenshot + log de acción |
| **Rate limiting** | Respetar límites del proveedor; backoff exponencial | Evitar polling agresivo | Mínimo de peticiones; horario off-peak |
| **Metadatos** | Extraer: número de expediente, tipo, fecha, estado, documentos asociados | Mismo objetivo con parsing XML | Extracción manual o semi-automática |
| **Complejidad** | Baja | Media | Alta (frágil en producción) |
| **Riesgos** | Cambios en API SIGED rompen integración; SLA bajo | SOAP puede retornar errores crípticos; ausencia de sandbox | Cambios en UI rompen scraping; legal/normativo |

**Nota sobre AWS/Azure**: Si SIGED es interno a la entidad, la integración corre en la misma red (VPN/VPC). Si es externo, se requiere firewall egress y certificados institucionales. AWS API Gateway o Azure APIM pueden actuar como proxy/façade con transformación de mensajes.

**Recomendación**: Diseñar una capa de abstracción `SIGEDAdapter` que encapsule el método de integración. Para MVP asumir API REST disponible. Para el caso sin API, proponer protocolo de integración al equipo SIGED antes de iniciar el desarrollo (ver sección I).

---

## Componente 4: Almacenamiento Documental

| Atributo | AWS S3 | Azure Blob Storage | MinIO (on-premise) | File Server NFS |
|---|---|---|---|---|
| **Tipo** | Object storage cloud | Object storage cloud | Object storage compatible S3 | Sistema de archivos |
| **Cifrado reposo** | SSE-S3, SSE-KMS, SSE-C | SSE con Microsoft-managed keys o CMK | AES-256 con KMS propio | BitLocker / dm-crypt |
| **Versionado** | Sí, nativo | Sí (soft delete + versiones) | Sí (compatible S3) | Manual con naming |
| **Lifecycle/Retención** | Lifecycle policies + S3 Glacier | Lifecycle + Archive tier | Lifecycle rules | Scripts manuales |
| **Acceso temporal** | Pre-signed URLs (TTL configurable) | SAS tokens | Pre-signed URLs | Token propio |
| **Costo aprox.** | $0.023/GB/mes (Standard) | $0.018/GB/mes (LRS) | Infraestructura propia; software libre | Infraestructura propia |
| **CDN / aceleración** | CloudFront | Azure CDN / Front Door | Nginx como proxy | — |
| **Ventajas** | Maduro, integraciones nativas AWS | Integración Azure AD, tiering automático | Sin datos en nube; control total; API S3 compatible | Sin complejidad de object storage |
| **Desventajas** | Costo egress; datos en nube | Datos en nube; vendor lock-in | Requiere operación y HA propia | Sin versionado nativo; difícil escalar |
| **MVP** | S3 con bucket privado + VPC Endpoint | Azure Blob con acceso privado | **MinIO single-node** en Docker | Disco local del servidor |
| **Producción** | S3 con replicación cross-region + Macie | Azure Blob con GRS + Defender for Storage | **MinIO distribuido** (4+ nodos) | NFS con backup HA |
| **Complejidad** | Baja | Baja | Media | Baja |
| **Riesgos** | Egress cost; datos sensibles fuera de entidad | Residencia de datos en Azure DCs | Requiere equipo DevOps para HA y backup | Sin object-level metadata; difícil buscar |

**Recomendación**: Para MVP on-premise usar **MinIO** (Docker, API S3-compatible). Para cloud privado usar **Azure Blob** si ya tienen convenio con Microsoft, o **S3** si están en AWS. Organizar el almacenamiento con prefijos: `expedientes/{id}/fuente/`, `expedientes/{id}/generados/`, `plantillas/bases/`, `plantillas/contratos/`.

---

## Componente 5: Base de Datos / Persistencia

| Atributo | AWS | Azure | Open Source / On-Premise |
|---|---|---|---|
| **Relacional** | RDS PostgreSQL / Aurora | Azure Database for PostgreSQL | **PostgreSQL** (recomendado) |
| **NoSQL documento** | DynamoDB | Cosmos DB | MongoDB, CouchDB |
| **Caché/cola** | ElastiCache (Redis) | Azure Cache for Redis | **Redis** (recomendado) |
| **Estado de procesos** | DynamoDB (Temporal backend) | Cosmos DB (Temporal backend) | PostgreSQL (Temporal backend) |
| **Prototipo** | RDS PostgreSQL t3.micro | PostgreSQL en Azure DB Flexible | **SQLite** (solo prototipo local) |
| **Auditoría y trazabilidad** | PostgreSQL con tabla audit_log + particionado | idem | idem |
| **Esquema recomendado** | Ver abajo | Ver abajo | Ver abajo |
| **Ventajas PostgreSQL** | ACID, pgvector, JSONB, extensible, maduro | | |
| **Ventajas DynamoDB/Cosmos** | Escalado serverless, sin mantenimiento | | |
| **Desventajas NoSQL** | Consultas analíticas complejas difíciles; sin JOINs | | |
| **MVP** | RDS t3.micro (dev) o PostgreSQL en Docker | PostgreSQL Flexible Server B1ms | **PostgreSQL 16 en Docker** |
| **Producción** | RDS Multi-AZ PostgreSQL | Azure DB PostgreSQL Flexible (HA) | PostgreSQL con Patroni (HA) |
| **Complejidad** | Baja | Baja | Baja (MVP) / Media (HA producción) |
| **Riesgos** | Costo RDS multi-AZ; backup manual si self-hosted | Mismo | Patroni requiere conocimiento DBA |

**Esquema de tablas mínimo**:

```sql
-- Expedientes consultados
CREATE TABLE expedientes (
  id UUID PRIMARY KEY,
  numero_expediente VARCHAR(50) UNIQUE NOT NULL,
  tipo VARCHAR(30), -- bases, contrato
  datos_siged JSONB,
  fecha_consulta TIMESTAMPTZ,
  usuario_id UUID REFERENCES usuarios(id)
);

-- Procesos de generación
CREATE TABLE procesos (
  id UUID PRIMARY KEY,
  expediente_id UUID REFERENCES expedientes(id),
  tipo_proceso VARCHAR(30), -- bases, contrato
  estado VARCHAR(20), -- iniciado, ocr_completado, extraccion_completada, revision_humana, finalizado, error
  datos_extraidos JSONB,
  datos_administrativos JSONB,
  plantilla_usada VARCHAR(100),
  documento_generado_url TEXT,
  creado_en TIMESTAMPTZ DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ DEFAULT NOW(),
  usuario_id UUID REFERENCES usuarios(id)
);

-- Trazabilidad campo-fuente
CREATE TABLE trazabilidad_campos (
  id UUID PRIMARY KEY,
  proceso_id UUID REFERENCES procesos(id),
  campo_destino VARCHAR(100),
  valor_extraido TEXT,
  documento_fuente VARCHAR(200),
  pagina_fuente INTEGER,
  confianza DECIMAL(5,4),
  validado_humano BOOLEAN DEFAULT FALSE,
  creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Auditoría de acciones
CREATE TABLE auditoria (
  id UUID PRIMARY KEY,
  usuario_id UUID,
  accion VARCHAR(100),
  recurso VARCHAR(100),
  detalle JSONB,
  ip_origen INET,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Componente 6: OCR

| Atributo | AWS Textract | Azure AI Document Intelligence | Google Document AI | Tesseract OCR | PaddleOCR |
|---|---|---|---|---|---|
| **Tipo** | Cloud managed | Cloud managed + contenedor | Cloud managed | Open source local | Open source local |
| **Precisión general** | ~94% texto limpio | ~95% (mejor en documentos custom) | ~96% texto limpio | ~85-90% limpio; baja en escaneados | ~92-95% con modelos PP-OCR |
| **Documentos administrativos** | Bueno en formularios estándar | **Excelente** (custom model trainable) | Bueno | Aceptable (requiere preprocesado) | Bueno con fine-tuning |
| **Soporte español** | Bueno | **Excelente** | Bueno | Bueno (tessdata_spa) | Bueno |
| **Tablas y formularios** | Sí (AnalyzeDocument) | Sí (Layout + Custom) | Sí (Form Parser) | No nativo | Parcial (PP-StructureV2) |
| **Documentos escaneados** | Bueno | Bueno | Bueno | Pobre sin deskew/denoise | Bueno con preprocesado |
| **Entrenamiento custom** | **No** (modelos pre-entrenados fijos) | **Sí** (custom model con 5-20 muestras) | Sí (Document AI Workbench) | No (configurable por idioma) | Sí (fine-tuning) |
| **Contenedor on-premise** | No | **Sí** (Read container, Layout container) | No | Sí | **Sí** |
| **Precio aprox.** | $1.50/1000p texto; $15/1000p tablas | $1.50/1000p prebuilt; $10/1000p custom | $1.50/1000p | Gratis (infraestructura propia) | Gratis |
| **Velocidad** | ~1-3s/pág | ~1-3s/pág | ~1-3s/pág | ~2-8s/pág (CPU) | ~0.5-2s/pág (GPU) |
| **MVP** | Aceptable si en AWS | **Recomendado** | Alternativa GCP | No recomendado en producción | **Recomendado on-premise** |
| **Producción** | Si arquitectura AWS | **Primaria (custom model)** | Alternativa | No | **Fallback on-premise** |
| **Complejidad** | Baja | Baja-Media | Baja-Media | Media-Alta | Media |
| **Riesgos** | Sin customización; documentos escaneados TDR pueden fallar | Costo si volumen alto; datos en nube Azure | Vendor lock-in GCP | Alta tasa de error sin preprocesado | Requiere GPU para velocidad óptima |

**Recomendación**: Para arquitectura cloud usar **Azure AI Document Intelligence** con custom model entrenado sobre muestras de TDR y Bases de la entidad. Es la opción con mejor balance entre precisión, customización y operación. Para escenario on-premise estricto usar **PaddleOCR** (PP-OCRv4) con preprocesado de imagen (deskew, denoising con OpenCV). Siempre incluir un campo `confidence_score` por bloque extraído.

---

## Componente 7: NLP / Extracción de Información

| Atributo | LLMs (GPT-4o, Claude) | Amazon Comprehend | spaCy + Reglas | LangChain/LlamaIndex + LLM | Embeddings + Clasificador |
|---|---|---|---|---|---|
| **Tipo** | Generativo | NER clásico cloud | NER + reglas local | RAG + extracción | Similitud semántica |
| **Precisión extracción** | **Alta** (con prompt estructurado) | Media (entidades genéricas) | Alta (con reglas bien calibradas) | **Alta** (RAG + structured output) | Media |
| **Flexibilidad** | **Muy alta** | Baja | Baja | **Alta** | Media |
| **Costo** | Alto (por token) | Bajo | Gratis | Alto (LLM) + bajo (embedding) | Bajo |
| **Velocidad** | Media (~2-5s) | Rápida | **Rápida** (<1s) | Media-Alta | Media |
| **Español** | **Excelente** | Bueno | Bueno (con modelo es_core_news_lg) | **Excelente** | Bueno |
| **Datos sensibles** | Riesgo si cloud | Riesgo si cloud | Sin riesgo | Riesgo si LLM cloud | Sin riesgo |
| **Anti-alucinación** | Requiere grounding + validación | No aplica | Determinista | Requiere RAG + citación | Determinista |
| **MVP** | GPT-4o con structured output (JSON schema) | No recomendado | Fallback determinista | LangChain + LLM + Pydantic | — |
| **Producción** | LLM on-premise + reglas híbridas | — | Combinado con LLM | **LangChain + RAG + Pydantic** | Combinado |
| **Complejidad** | Media | Baja | Media | Media | Alta |
| **Riesgos** | Alucinaciones; costo; latencia | Baja precisión en documentos administrativos peruanos | Mantenimiento de reglas; frágil ante cambios de formato | Complejidad de pipeline; debugging difícil | Requiere datos de entrenamiento |

**Enfoque recomendado (híbrido)**:

```
Documento → OCR → Texto estructurado
                        ↓
              [Extracción por Reglas] → Campos con alta certeza (RUC, fechas, montos)
                        ↓ (campos no extraídos)
              [LLM con Structured Output] → Campos complejos (descripción de objeto, especificaciones)
                        ↓
              [Validación Pydantic] → Tipado y rango
                        ↓
              [Trazabilidad] → Campo + fuente + confianza + página
```

Usar `instructor` (librería Python) sobre el LLM para forzar salidas estructuradas sin alucinaciones de formato.

---

## Componente 8: Motor de IA Generativa / LLM

| Atributo | Azure OpenAI (GPT-4o) | AWS Bedrock (Claude Sonnet) | OpenAI API | Mistral Large 3 on-premise | Qwen 3.5-72B on-premise | Llama 4 on-premise |
|---|---|---|---|---|---|---|
| **Modalidad** | Cloud (Azure) | Cloud (AWS) | Cloud | On-premise / self-hosted | On-premise / self-hosted | On-premise / self-hosted |
| **Capacidad razonamiento** | **Excelente** | **Excelente** | **Excelente** | Muy buena | **Muy buena** | Buena |
| **Soporte español** | **Excelente** | **Excelente** | **Excelente** | Excelente (80+ idiomas) | Excelente (201 idiomas) | Bueno |
| **Residencia de datos** | Azure región (configurable) | AWS región (configurable) | EE.UU. (riesgo) | **Local/on-premise** | **Local/on-premise** | **Local/on-premise** |
| **Privacidad** | Media (datos en nube) | Media (datos en nube) | Baja (datos en EE.UU.) | **Alta** | **Alta** | **Alta** |
| **Costo aprox.** | ~$15/M tokens input GPT-4o | ~$3/M tokens Claude Sonnet 3.7 | ~$15/M tokens GPT-4o | Infraestructura GPU (~$0.5-2/h) | Infraestructura GPU | Infraestructura GPU |
| **Contexto** | 128K tokens | 200K tokens | 128K tokens | 128K tokens | 128K tokens | 10M tokens (Scout) |
| **Function calling** | Sí | Sí | Sí | **Sí (Mistral Small 4)** | **Sí** | Parcial |
| **JSON output estructurado** | Sí | Sí | Sí | **Sí (excelente)** | **Sí (excelente)** | Bueno |
| **Auditoría/Gobernanza** | Azure AI Content Safety + logs | Bedrock logs + Guardrails | Limitada | **Total (local)** | **Total (local)** | **Total (local)** |
| **Integración empresarial** | Azure AD, APIM, Monitor | IAM, CloudWatch, Organizations | API Key simple | vLLM + LangChain | vLLM + LangChain | vLLM + LangChain |
| **GPU requerida** | N/A | N/A | N/A | 2x A100 80GB o 4x RTX 4090 | 2x A100 80GB | 4x A100 (Scout) |
| **MVP** | **Recomendado (si cloud permitido)** | Alternativa AWS | Evitar (residencia datos) | Alternativa on-premise | **Recomendado on-premise** | — |
| **Producción** | **Primera opción cloud** | Segunda opción cloud | No recomendado | **Primera opción on-premise** | **Primera opción on-premise** | Segunda on-premise |
| **Complejidad** | Baja | Baja | Baja | Alta (infra GPU) | Alta (infra GPU) | Alta |
| **Riesgos** | Datos en Azure; costo en volumen; dependencia de API | Datos en AWS; latencia inter-región | Datos en EE.UU. sin garantía | Costo GPU inicial alto; equipo MLOps | Modelo chino (riesgo geopolítico percibido) | Requiere mucha GPU; licencia comercial Meta |

**Recomendación**:
- **Si cloud está aprobado**: Azure OpenAI GPT-4o con Data Privacy Agreement corporativo, zona de datos Latinoamérica/EE.UU. (revisar disponibilidad región).
- **Si se requiere on-premise**: Mistral Large 3 (Apache 2.0, 80+ idiomas, excelente español, function calling nativo) servido con **vLLM** en GPU.
- **Arquitectura recomendada**: Diseñar sobre una abstracción `LLMProvider` que permita cambiar entre Azure OpenAI y modelo local sin modificar la lógica de negocio.

---

## Componente 9: RAG / Base de Conocimiento

| Atributo | Azure AI Search | Amazon OpenSearch | Amazon Kendra | PostgreSQL + pgvector | Qdrant | Weaviate |
|---|---|---|---|---|---|---|
| **Tipo** | Managed hybrid search | Managed OpenSearch | Managed enterprise search | Self-hosted extension SQL | Self-hosted/cloud vector DB | Self-hosted/cloud vector DB |
| **Búsqueda híbrida** | **Sí (BM25 + vector)** | Sí | Sí (NLP) | Parcial (pgvector + FTS) | **Sí (sparse + dense)** | **Sí** |
| **Trazabilidad de fuentes** | Sí (source fields) | Sí | Sí (confidence score) | Sí (metadata SQL) | **Sí (payload filtering)** | Sí |
| **Control de versiones** | Indexado por fecha | Por índice/alias | Por data source sync | **Por columna SQL** | Por colección y versión | Por schema version |
| **On-premise** | No | No (OpenSearch SE sí) | No | **Sí** | **Sí** | **Sí** |
| **Actualización conocimiento** | Indexador programado | API bulk ingest | Data source connector | INSERT/UPDATE SQL | Upsert por ID | Upsert por UUID |
| **Costo** | $1/1000 transacciones | Por instancia | $0.005/query | Infraestructura propia | Gratis open source | Gratis open source |
| **Integración LangChain** | Sí | Sí | Sí | Sí | **Sí (nativa)** | **Sí (nativa)** |
| **MVP** | Si Azure | Si AWS | No recomendado (costo) | **Recomendado** (ya tienen PostgreSQL) | Alternativa MVP | — |
| **Producción** | Si Azure | Si AWS | Enterprise con presupuesto | **Recomendado** hasta 5M vectores | **Recomendado** producción | Alternativa |
| **Complejidad** | Baja | Media | Baja (pero caro) | Baja | Baja-Media | Media |
| **Riesgos** | Vendor lock-in Azure; costo en escala | Complejo de operar | Muy caro para volúmenes moderados | Rendimiento a >50M vectores | Requiere backup propio | Más complejo que pgvector |

**Contenido a indexar en la base de conocimiento**:
- Plantillas de Bases (5 tipos: Bienes, Servicios, Consultoría Normal/Abreviado)
- Directivas y lineamientos OSCE
- Contratos ejemplo (anonimizados)
- Reglamento de Contrataciones del Estado (DS vigente)
- Reglas de negocio internas de la entidad
- TDRs históricos (para few-shot context)

**Recomendación**: Para MVP usar **PostgreSQL + pgvector** con `langchain-postgres` como vector store. Es la solución de menor complejidad operativa dado que ya usarán PostgreSQL para el estado. Para producción con alto volumen de documentos migrar a **Qdrant** (self-hosted, filtrado eficiente, compatible con LangChain).

---

## Componente 10: Motor de Plantillas Documentales

| Atributo | docxtpl (Python) | python-docx | Apache POI (Java) | Aspose.Words | docx4j (Java) | HTML → PDF |
|---|---|---|---|---|---|---|
| **Lenguaje** | Python | Python | Java | .NET/Java/Python | Java | Cualquiera |
| **Motor plantilla** | Jinja2 ({{ variable }}) | API programática | API programática | API programática | JAXB + API | WeasyPrint, wkhtmltopdf |
| **Salida** | `.docx` | `.docx` | `.docx` / `.xlsx` | `.docx` / `.pdf` | `.docx` | `.pdf` (no .docx) |
| **Secciones condicionales** | **Sí ({% if %})** | Manual (programático) | Manual | Sí (merge fields) | Manual | Sí (CSS display:none) |
| **Tablas variables** | **Sí ({% for %})** | Programático (más código) | Programático | Sí | Programático | Sí |
| **Numeración automática** | Hereda del .docx base | Sí | Sí | Sí | Sí | CSS counters |
| **Mantenimiento formato** | **Excelente** (heredado del template) | Bueno | Bueno | **Excelente** | Bueno | Pierde fidelidad Word |
| **Facilidad de uso** | **Muy alta** | Media | Baja | Media | Baja | Alta |
| **Costo** | Gratis (MIT) | Gratis (MIT) | Gratis (Apache 2.0) | **Costo por licencia** | Gratis | Gratis |
| **Soporte Word complex features** | Bueno | Limitado | Bueno | **Excelente** | Bueno | No |
| **MVP** | **Recomendado** | Fallback simple | No recomendado | Overkill (costo) | No recomendado | No (requieren .docx) |
| **Producción** | **Recomendado** | Complementario | Si Java stack | Si presupuesto y complejidad alta | Si Java stack | Solo para PDF adicional |
| **Complejidad** | **Baja** | Media | Alta | Media | Alta | Baja |
| **Riesgos** | Plantillas mal formadas generan errores; requiere templates .docx bien preparados | Mucho código para tablas complejas | Requiere Java en stack | Licencia y vendor lock-in | Requiere Java | Salida no es .docx |

**Recomendación**: Usar **docxtpl** como motor principal. El área funcional debe preparar las plantillas `.docx` con variables Jinja2 (`{{ objeto_contratacion }}`, `{% if tipo == 'bienes' %}`...). El equipo técnico desarrolla el mapper de datos extraídos → variables de plantilla. Complementar con **python-docx** para manipulación programática fina (insertar tablas dinámicas, ajustar estilos).

---

## Componente 11: Generación y Descarga de Documentos

| Atributo | Síncrono | Asíncrono (recomendado) |
|---|---|---|
| **Flujo** | Request → generar → response con archivo | Request → job ID → polling/webhook → descarga |
| **Tiempo respuesta** | Inmediato (si <5s) | Diferido (notificación al completar) |
| **Adecuado para** | Plantillas simples, sin OCR | Documentos con OCR + LLM (10-60s) |
| **Versiones** | ID + timestamp en nombre del archivo | Historial en BD, múltiples versiones por proceso |
| **Marca de agua borrador** | python-docx inserta encabezado/marca de agua | Idem |
| **Metadatos .docx** | python-docx `core_properties`: author, company, title, keywords | Idem |
| **Formato descarga** | Pre-signed URL con TTL 15 min | Idem |
| **Historial** | Tabla `documentos_generados` en PostgreSQL | Idem |
| **PDF opcional** | LibreOffice headless (`soffice --convert-to pdf`) | Idem, task asíncrona separada |

**Flujo de generación recomendado**:
```
1. Usuario confirma datos en frontend
2. Backend crea job en cola (Celery/Redis)
3. Worker: carga plantilla + mapea datos → docxtpl.render()
4. Worker: agrega metadatos, marca "BORRADOR" si revisión pendiente
5. Worker: sube archivo a MinIO/S3 con prefijo expediente
6. Worker: guarda URL + hash SHA-256 en PostgreSQL
7. Worker: registra trazabilidad (campo → fuente → página)
8. Backend: notifica frontend (WebSocket o polling)
9. Frontend: botón "Descargar" con pre-signed URL (TTL 15 min)
```

---

## Componente 12: Validación y Control de Calidad

| Mecanismo | Descripción | Cuándo usar | Anti-alucinación |
|---|---|---|---|
| **Reglas determinísticas** | Expresiones regulares + rangos para campos numéricos | Montos, RUC, fechas, plazos | **Alta** (determinista) |
| **Validación Pydantic** | Schema tipado, rangos, campos obligatorios | Siempre en extracción LLM | **Alta** |
| **Confidence score OCR** | Threshold ≥ 0.85 para aceptar campo | Por campo extraído en OCR | **Alta** |
| **Validación cruzada LLM** | Prompt: "¿Los datos en campo X de doc A coinciden con campo Y de doc B?" | Contratos (monto oferta = monto contrato) | Media (requiere grounding) |
| **Revisión humana** | Interface de revisión con campos resaltados | **Siempre antes de finalizar** | **Máxima** |
| **Doble verificación** | Dos usuarios independientes revisan datos críticos | Contratos de alto valor | Máxima |
| **Hash de documentos fuente** | SHA-256 del PDF procesado vs descargado | Integridad documental | **Alta** |

**Controles específicos para Contratos**:

| Campo | Control | Fuente |
|---|---|---|
| Monto del contrato | = Monto oferta económica ganadora (±0) | Oferta Económica |
| Plazo de ejecución | = Plazo en Bases Integradas | Bases Integradas |
| Forma de pago | Coincide con Bases Integradas | Bases Integradas |
| RUC contratista | Válido en SUNAT (consulta API) | Vigencia de Poder |
| Representante legal | Coincide con Vigencia de Poder | Vigencia de Poder |
| Tipo de garantía | Según Bases (fiel cumplimiento / adelanto) | Bases Integradas |
| Entregables | Coinciden con Especificaciones Técnicas | Oferta Técnica |
| Objeto del contrato | Coherente con TDR y Bases | TDR / Bases |

---

## Componente 13: Seguridad, Privacidad y Cumplimiento

| Capa | AWS | Azure | On-Premise / Open Source |
|---|---|---|---|
| **Identidad y acceso (IAM/RBAC)** | AWS IAM + Cognito + SCP | Azure AD + RBAC + Conditional Access | **Keycloak** (OAuth2/OIDC, RBAC completo) |
| **Cifrado en tránsito** | TLS 1.2+ (ALB, API GW, S3) | TLS 1.2+ (APIM, App GW, Blob) | Nginx/HAProxy con TLS + Let's Encrypt |
| **Cifrado en reposo** | SSE-KMS (S3, RDS) | CMK (Blob, DB) | PostgreSQL pgcrypto + MinIO AES-256 |
| **Gestión de secretos** | AWS Secrets Manager | Azure Key Vault | **HashiCorp Vault** |
| **Logging y auditoría** | CloudTrail + CloudWatch Logs | Azure Monitor + Activity Log | **Loki + Grafana** / ELK |
| **DLP** | Amazon Macie | Microsoft Purview DLP | OpenDLP / Presidio (Microsoft) |
| **WAF** | AWS WAF | Azure WAF | ModSecurity + OWASP CRS |
| **Mascaramiento PII** | Macie + Lambda | Purview | **Presidio** (Microsoft, open source) |
| **Escaneo vulnerabilidades** | Amazon Inspector + ECR scanning | Defender for Containers | **Trivy** + **OWASP ZAP** |
| **Segregación ambientes** | Cuentas AWS separadas (dev/stg/prod) | Suscripciones Azure separadas | Kubernetes namespaces + NetworkPolicy |
| **Retención documentos** | S3 Lifecycle + Object Lock | Blob Lifecycle + Immutable Storage | MinIO Object Locking + scripts retención |

**Roles RBAC mínimos recomendados**:

| Rol | Permisos |
|---|---|
| `admin_sistema` | Gestión de usuarios, configuración, logs |
| `operador_bases` | Crear/editar procesos de Bases, revisar, finalizar |
| `operador_contratos` | Crear/editar procesos de Contratos, revisar, finalizar |
| `revisor` | Solo lectura + aprobación de documentos |
| `auditor` | Solo lectura de logs y trazabilidad |
| `servicio_ocr` | Solo llamadas al servicio OCR (service account) |
| `servicio_llm` | Solo llamadas al servicio LLM (service account) |

**Eventos que DEBEN auditarse**:
- Login / logout / intentos fallidos
- Consulta de expediente en SIGED
- Descarga de documentos de SIGED
- Inicio/fin de proceso OCR
- Inicio/fin de extracción NLP
- Modificación manual de campos extraídos
- Generación de documento borrador
- Aprobación / rechazo de revisión humana
- Descarga de documento final
- Eliminación de expediente o proceso

---

## Componente 14: Observabilidad y Auditoría

| Herramienta | Tipo | AWS | Azure | On-Premise |
|---|---|---|---|---|
| **Logs** | Centralizados | CloudWatch Logs | Azure Monitor Logs | **Loki + Promtail** |
| **Métricas** | Series temporales | CloudWatch Metrics | Azure Metrics | **Prometheus + Grafana** |
| **Trazas** | Distributed tracing | AWS X-Ray | Azure Application Insights | **Jaeger / Tempo** (OpenTelemetry) |
| **Alertas** | Notificaciones | CloudWatch Alarms + SNS | Azure Alerts | **Alertmanager** |
| **APM** | Rendimiento app | CloudWatch Container Insights | Application Insights | **OpenTelemetry + Grafana** |
| **Auditoría funcional** | Business events | DynamoDB + CloudWatch | Cosmos DB + Monitor | PostgreSQL tabla `auditoria` |
| **SIEM** | Seguridad | AWS Security Hub + GuardDuty | Microsoft Sentinel | Wazuh (open source SIEM) |
| **Dashboards** | Visualización | CloudWatch Dashboards | Azure Workbooks | **Grafana** |

**Stack recomendado on-premise (completo open source)**:
```
OpenTelemetry SDK (en FastAPI) → Collector → [Loki (logs) + Prometheus (métricas) + Tempo (trazas)] → Grafana
```

**Métricas de negocio a monitorear**:
- Tiempo promedio de generación de documento (TDR → .docx)
- Tasa de éxito OCR por tipo de documento
- Tasa de confianza promedio por campo extraído
- Cantidad de correcciones manuales por campo (indica calidad OCR/NLP)
- Tiempo de revisión humana
- Documentos en estado "pendiente revisión" > 24h (alerta)

---

## Componente 15: Despliegue e Infraestructura

| Patrón | Descripción | Ventajas | Desventajas | Recomendación |
|---|---|---|---|---|
| **Docker Compose on-premise** | Stack completo en un servidor | Simplicidad; cero cloud; control total | Sin HA nativa; escala manual | **MVP** |
| **Kubernetes on-premise (K3s/RKE2)** | Cluster Kubernetes ligero | HA; auto-scaling; producción-grade | Curva de aprendizaje; requiere mínimo 3 nodos | **Producción on-premise** |
| **Azure Container Apps** | Serverless containers Azure | Sin gestión Kubernetes; auto-scale | Cloud Azure; dependencia proveedor | **MVP/Producción cloud Azure** |
| **AWS ECS Fargate** | Serverless containers AWS | Sin gestión EC2; integración AWS | Cloud AWS; dependencia proveedor | **MVP/Producción cloud AWS** |
| **AKS / EKS** | Kubernetes gestionado cloud | Full Kubernetes; máxima flexibilidad | Más costo y complejidad | **Producción cloud avanzada** |
| **Arquitectura híbrida** | LLM on-premise + frontend cloud | Datos sensibles locales; UX cloud | Latencia entre capas; red privada | **Producción con restricciones** |
| **VMs tradicionales** | Nginx + Gunicorn en VM | Simple; familiar | Sin elasticidad; difícil escalar | No recomendado nuevo proyecto |

**Arquitectura MVP recomendada (on-premise, Docker Compose)**:
```yaml
Servicios en Docker Compose:
  - frontend:    React + Nginx (puerto 443)
  - api:         FastAPI + Uvicorn (puerto 8000)
  - worker:      Celery worker (OCR + NLP + docxtpl)
  - redis:       Redis 7 (cola de tareas + caché)
  - postgres:    PostgreSQL 16 (estado + auditoría + pgvector)
  - minio:       MinIO (storage documental)
  - keycloak:    Keycloak (IAM/SSO)
  - loki:        Loki (logs)
  - prometheus:  Prometheus (métricas)
  - grafana:     Grafana (dashboards)
```

**Requerimientos hardware MVP** (on-premise, sin GPU para LLM cloud):
- 1 servidor: 16 vCPU, 32 GB RAM, 1 TB SSD NVMe
- Si LLM on-premise: +2x GPU NVIDIA A100 80GB o 4x RTX 4090 (Mistral Large 3)

---

## Componente 16: CI/CD y DevSecOps

| Herramienta | Tipo | Recomendación |
|---|---|---|
| **GitHub Actions** | CI/CD cloud | MVP si repositorio en GitHub |
| **GitLab CI/CD** | CI/CD self-hosted | **Recomendado** (self-hosted para entidad pública) |
| **Azure DevOps** | CI/CD cloud/híbrido | Si Azure stack |
| **Jenkins** | CI/CD self-hosted | Legacy; evitar nuevo proyecto |
| **Terraform** | IaC cloud multi-provider | Producción cloud |
| **OpenTofu** | IaC cloud open source (fork Terraform) | Alternativa open source a Terraform |
| **Ansible** | IaC on-premise (configuración) | MVP on-premise |
| **Trivy** | Escaneo vulnerabilidades containers | **Siempre en pipeline** |
| **OWASP ZAP** | DAST (Dynamic Application Security Testing) | QA/staging |
| **SonarQube** | SAST (Static Analysis Security Testing) | **Siempre en pipeline** |
| **Semgrep** | SAST open source | Alternativa a SonarQube |
| **Conftest** | Policy-as-code (OPA/Rego) | Validar IaC antes de apply |

**Pipeline CI/CD mínimo**:
```
Commit → [Lint + Tests unitarios] → [SAST (SonarQube/Semgrep)] → [Build Docker] → [Trivy scan] → [Tests integración] → [Deploy staging] → [DAST (ZAP)] → [Deploy producción (manual aprobación)]
```

---

## Componente 17: Costos y Licenciamiento

### Estimación Comparativa MVP (mensual, volumen bajo: ~100 expedientes/mes)

| Componente | Cloud Azure | Cloud AWS | On-Premise |
|---|---|---|---|
| **Compute (API + Worker)** | Container Apps: ~$80/mes | ECS Fargate: ~$90/mes | Servidor existente: $0 |
| **LLM (GPT-4o / Bedrock)** | ~$150/mes (100 procesos, ~1M tokens) | ~$80/mes (Claude Sonnet) | GPU leasing: ~$300/mes |
| **OCR** | Doc Intelligence: ~$15/mes | Textract: ~$18/mes | PaddleOCR: $0 |
| **Storage** | Blob: ~$5/mes | S3: ~$5/mes | MinIO en servidor: $0 |
| **Base de datos** | PostgreSQL Flexible B1ms: ~$25/mes | RDS t3.micro: ~$20/mes | Docker: $0 |
| **Vector DB** | Incluido PostgreSQL | Incluido PostgreSQL | Incluido PostgreSQL |
| **Observabilidad** | Monitor (básico incluido) | CloudWatch: ~$10/mes | Grafana/Loki: $0 |
| **IAM/SSO** | Azure AD Free/P1: $0/$6/usr | Cognito (primeros 50K free) | Keycloak: $0 |
| **TOTAL APROX.** | **~$275-350/mes** | **~$225-300/mes** | **~$0-300/mes** (hardware ya disponible) |

**Componentes de mayor impacto en costo**:
1. **LLM API** — Domina el costo en cloud; on-premise requiere GPU
2. **OCR** — Escala linealmente con páginas procesadas
3. **Storage** — Bajo en fase inicial; crece con histórico
4. **Compute GPU** — Solo si LLM on-premise

**Recomendación para minimizar costo**:
- Usar LLM solo donde sea necesario (no en extracción de campos con alta certeza por reglas)
- Cachear respuestas LLM para prompts idénticos (Redis)
- Procesar OCR en batch en horario off-peak si no es urgente
- Usar modelos LLM más pequeños para tareas simples (clasificación de plantilla, extracción de fechas)

---

## Componente 18: Roadmap Recomendado

Ver sección F (Bases) y G (Contratos) para detalle por fase.

| Fase | Duración estimada | Entregable principal |
|---|---|---|
| **Fase 1**: MVP Asistente Bases | 8-12 semanas | Generación de Bases desde TDR funcional |
| **Fase 2**: Fortalecimiento OCR/NLP + Plantillas | 6-8 semanas | Custom OCR model + validación campo-fuente |
| **Fase 3**: Asistente Contratos | 10-14 semanas | Generación de Contratos con validación cruzada |
| **Fase 4**: Producción + Auditoría + HA | 6-8 semanas | Despliegue productivo con observabilidad completa |

---

# C. ARQUITECTURA RECOMENDADA PARA MVP

## Diagrama de Arquitectura MVP — Asistente de Bases

```
┌─────────────────────────────────────────────────────────────────┐
│                    RED INTERNA ENTIDAD                           │
│                                                                  │
│  ┌──────────────┐    HTTPS     ┌──────────────────────────────┐ │
│  │  NAVEGADOR   │◄────────────►│  NGINX (Reverse Proxy TLS)   │ │
│  │  (React App) │              └──────────────┬───────────────┘ │
│  └──────────────┘                             │                  │
│                                               ▼                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              DOCKER COMPOSE STACK                       │    │
│  │                                                         │    │
│  │  ┌──────────────┐    ┌─────────────────────────────┐   │    │
│  │  │   KEYCLOAK   │    │   FASTAPI (API Backend)      │   │    │
│  │  │  IAM / SSO   │◄───│   - /api/expedientes         │   │    │
│  │  │  port: 8080  │    │   - /api/procesos             │   │    │
│  │  └──────────────┘    │   - /api/documentos           │   │    │
│  │                      │   - WebSocket /ws/status      │   │    │
│  │                      └──────────────┬──────────────-─┘   │    │
│  │                                     │ Celery tasks        │    │
│  │                      ┌──────────────▼───────────────┐    │    │
│  │  ┌────────────┐      │    REDIS (Cola + Caché)       │    │    │
│  │  │ PostgreSQL │      └──────────────┬───────────────┘    │    │
│  │  │ (Estado +  │◄──────────────────┐ │                    │    │
│  │  │  Auditoría │                   │ ▼                    │    │
│  │  │  pgvector) │      ┌─────────────────────────────┐    │    │
│  │  └────────────┘      │   CELERY WORKER              │    │    │
│  │                      │   1. Consulta SIGED API       │    │    │
│  │  ┌────────────┐      │   2. Descarga TDR (PDF/DOCX) │    │    │
│  │  │   MINIO    │◄─────│   3. OCR (Azure Doc Intel.   │    │    │
│  │  │  Storage   │      │        o PaddleOCR local)     │    │    │
│  │  │            │      │   4. NLP/Extracción (LLM +   │    │    │
│  │  └────────────┘      │        reglas + Pydantic)     │    │    │
│  │                      │   5. Selección de plantilla   │    │    │
│  │                      │   6. docxtpl.render()         │    │    │
│  │                      │   7. Sube .docx a MinIO       │    │    │
│  │                      │   8. Registra trazabilidad    │    │    │
│  │                      └─────────────────────────────┘    │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────┐      │    │
│  │  │  GRAFANA + PROMETHEUS + LOKI (Observabilidad)│      │    │
│  │  └──────────────────────────────────────────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────┐                           │
│  │  SIGED (Sistema Documentario)    │                           │
│  │  API REST interna (VPN/Intranet) │                           │
│  └──────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────┐
        │  SERVICIOS EXTERNOS (si cloud)   │
        │  - Azure OpenAI (LLM)            │
        │  - Azure Doc Intelligence (OCR)  │
        └──────────────────────────────────┘
```

## Flujo de Datos MVP — Asistente de Bases

```
Usuario ingresa N° expediente
        │
        ▼
API → Adapter SIGED → GET /expediente/{id}
        │
        ▼
Retorna metadata + lista de documentos
        │
        ▼
Usuario selecciona TDR del expediente
        │
        ▼
Worker: Descarga PDF/DOCX del TDR desde SIGED → MinIO
        │
        ▼
Worker: OCR del TDR → texto + posición + confidence
        │
        ▼
Worker: Extracción NLP:
  - Reglas: fechas, montos, código SNIP, código SIAF, objeto
  - LLM (GPT-4o / Mistral): especificaciones técnicas,
    condiciones, plazos complejos, perfiles requeridos
  - Validación Pydantic: tipos + rangos
  - Trazabilidad: campo → página → posición → confidence
        │
        ▼
API → Frontend: muestra datos extraídos en formulario editable
        │
        ▼
Usuario: revisa, corrige, agrega datos administrativos
        │
        ▼
Usuario: selecciona tipo de plantilla (Bienes/Servicios/Consultoría/Normal/Abreviado)
        │
        ▼
Worker: docxtpl.render(plantilla, datos_consolidados) → base.docx
        │
        ▼
Worker: marca "BORRADOR", agrega metadatos, hash SHA-256
        │
        ▼
Worker: sube a MinIO → URL firmada
        │
        ▼
Frontend: botón "Descargar Base (Borrador)"
        │
        ▼
Revisor: descarga, revisa en Word, aprueba/rechaza en sistema
        │
        ▼
Si aprobado: estado = "FINAL", documento disponible en repositorio
```

---

# D. ARQUITECTURA RECOMENDADA PARA PRODUCCIÓN

## Principios de Diseño Producción

1. **Alta disponibilidad**: Sin SPOF; réplica de base de datos; worker pool
2. **Separación de preocupaciones**: Microservicios por dominio funcional
3. **Seguridad en profundidad**: WAF, mTLS interno, secretos en Vault, RBAC granular
4. **Observabilidad completa**: Trazas distribuidas, métricas de negocio, alertas
5. **Portabilidad**: Kubernetes permite cloud y on-premise con el mismo manifiesto

## Componentes de Producción

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ZONA PÚBLICA (DMZ)                                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  WAF (ModSecurity / AWS WAF / Azure WAF)                        │ │
│  │  Load Balancer / Ingress Controller (Nginx Ingress / ALB / AGW) │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                        │ (TLS 1.3)
┌──────────────────────────────────────────────────────────────────────┐
│                  ZONA APLICACIÓN (Kubernetes Cluster)                │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  frontend-svc    │  │  api-svc          │  │  keycloak-svc    │  │
│  │  (React + Nginx) │  │  (FastAPI 3 pods) │  │  (IAM SSO 2 pods)│  │
│  └──────────────────┘  └─────────┬────────┘  └──────────────────┘  │
│                                  │ mTLS                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              WORKER NAMESPACE (Celery)                       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │   │
│  │  │ siged-adapter   │  │ ocr-worker      │  │ nlp-worker  │  │   │
│  │  │ (2 replicas)    │  │ (3 replicas)    │  │ (3 replicas)│  │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────┘  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                   │   │
│  │  │ docgen-worker   │  │ validation-svc  │                   │   │
│  │  │ (2 replicas)    │  │ (2 replicas)    │                   │   │
│  │  └─────────────────┘  └─────────────────┘                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              DATA NAMESPACE                                  │   │
│  │  ┌─────────────────┐  ┌────────────────┐  ┌─────────────┐  │   │
│  │  │ PostgreSQL HA   │  │ Redis Sentinel │  │ MinIO       │  │   │
│  │  │ (Patroni 3 nod.)│  │ (3 nodos)      │  │ (Distribuido│  │   │
│  │  │ + pgvector      │  └────────────────┘  │  4 nodos)   │  │   │
│  │  └─────────────────┘                      └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              OBSERVABILIDAD NAMESPACE                        │   │
│  │  Prometheus + Grafana + Loki + Tempo + Alertmanager          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
  ┌─────────────────┐    ┌──────────────────────┐
  │ SIGED (intranet)│    │ SERVICIOS IA (cloud o │
  │ API REST + docs │    │ on-premise)           │
  └─────────────────┘    │ - LLM (vLLM + Mistral)│
                         │ - OCR (Az Doc Intel.) │
                         │ - HashiCorp Vault      │
                         └──────────────────────┘
```

---

# E. ALTERNATIVAS SI NO EXISTE API DE SIGED

## Escenario 1: Existe API REST documentada (mejor caso)
**Acciones**: Desarrollar `SIGEDRestAdapter` con httpx + retry + circuit breaker. Solicitar al equipo SIGED: sandbox, credenciales de prueba, catálogo de endpoints, SLA y límites de tasa.

## Escenario 2: Existe web service SOAP/XML
**Acciones**: Usar librería `zeep` (Python) para consumir WSDL. Parser XML tolerante a faults. Mayor fragilidad; solicitar migración a REST si es posible.

## Escenario 3: Solo hay interfaz web (sin API)
**Opciones técnicas**:

| Opción | Descripción | Riesgo |
|---|---|---|
| **Web scraping con Playwright** | Automatización del navegador; extrae HTML | Alto (frágil ante cambios de UI; cuestionable normativamente) |
| **Exportación batch programada** | Coordinación con equipo SIGED para exportar expedientes como CSV/JSON diariamente | Bajo (preferida) |
| **Integración por base de datos** | Acceso de solo lectura a BD de SIGED (coordinación DBA) | Medio (riesgo integridad si no está documentado) |
| **Carga manual estructurada** | El usuario sube el expediente PDF + metadatos en formulario | Bajo (degradado funcional; viable para MVP) |

**Recomendación**: En ausencia de API, proponer formalmente al área de TI y al equipo SIGED el desarrollo de una API de consulta de solo lectura para el número de expediente. Mientras tanto, el MVP puede operar con **carga manual** del TDR por el usuario operador.

## Escenario 4: SIGED en otro sistema/plataforma
Si SIGED es un ERP externo (SAP, Oracle, OpenSIGED), investigar si tiene módulos de integración estándar (RFC, OData, REST) o conectores de middleware (MuleSoft, WSO2, Apache Camel).

---

# F. RECOMENDACIÓN ESPECÍFICA: INICIAR CON BASES

## ¿Por qué Bases primero?

| Criterio | Bases (Fase 1) | Contratos (Fase 3) |
|---|---|---|
| **Complejidad del flujo** | Baja (1 TDR → 1 plantilla → 1 salida) | Alta (5+ docs → validación cruzada → 1 contrato) |
| **Documentos fuente** | 1 (TDR) | 5+ (Bases, Oferta Económica, Oferta Técnica, Vigencia Poder, Garantía) |
| **Riesgo legal** | Medio (normas OSCE para Bases) | Alto (validez contractual, monto, representación legal) |
| **Validación requerida** | Administrativa + técnica | Legal + normativa + consistencia cruzada |
| **Tiempo para entregar valor** | 8-12 semanas | 18-26 semanas (total) |
| **Permite aprender la pila** | Sí (base para Contratos) | No (requiere madurez previa) |

## Plan Detallado Fase 1 — MVP Asistente Bases (semanas 1-12)

**Semanas 1-2: Fundamentos**
- Configurar repositorio Git (GitLab self-hosted)
- Configurar Docker Compose con servicios base
- Establecer estructura de proyecto FastAPI
- Diseñar esquema de base de datos
- Configurar Keycloak con roles básicos

**Semanas 3-4: Integración SIGED y Storage**
- Desarrollar `SIGEDAdapter` (REST o carga manual si sin API)
- Configurar MinIO con buckets y políticas
- Desarrollar endpoint de consulta de expediente
- Pruebas con expedientes reales (datos de prueba)

**Semanas 5-6: OCR y Extracción**
- Integrar Azure Document Intelligence o PaddleOCR
- Desarrollar pipeline de extracción de campos del TDR
- Implementar extracción por reglas (fechas, montos, códigos)
- Integrar LLM para campos complejos (especificaciones técnicas)
- Implementar modelo de trazabilidad campo-fuente

**Semanas 7-8: Motor de Plantillas y Generación**
- Preparar 5 plantillas .docx (con área funcional)
- Desarrollar mapper datos-extraídos → variables-plantilla
- Implementar docxtpl rendering
- Agregar metadatos, hash, marca de borrador
- Flujo de descarga con pre-signed URL

**Semanas 9-10: Frontend y Revisión Humana**
- Desarrollar UI: búsqueda de expediente, visualización de datos extraídos
- Formulario editable para correcciones + datos administrativos
- Selector de plantilla
- Flujo de aprobación/revisión
- Integración Keycloak (autenticación + roles)

**Semanas 11-12: QA, Seguridad y Piloto**
- Pruebas de integración end-to-end con 10 expedientes reales
- Revisión de seguridad (Trivy, OWASP ZAP básico)
- Configurar observabilidad (Grafana + Loki básico)
- Capacitación de usuarios piloto (3-5 operadores)
- Ajustes basados en feedback

---

# G. RECOMENDACIÓN ESPECÍFICA: ESCALAR A CONTRATOS

## ¿Qué debe estar maduro antes de iniciar Contratos?

| Prerequisito | Estado requerido |
|---|---|
| OCR con confianza ≥ 0.90 en TDR y Bases | Validado en producción (Fase 1+2) |
| Motor de plantillas docxtpl estable | Al menos 50 Bases generadas sin errores |
| Trazabilidad campo-fuente funcionando | Auditado por área legal/contratos |
| RBAC y auditoría operativos | Auditado por seguridad institucional |
| Equipo con experiencia en el stack | Al menos 3 meses de operación |
| Plantillas de contrato preparadas (funcional) | Validadas por área legal |
| Protocolo de revisión humana definido | Firmado por área de contratos |

## Plan Detallado Fase 3 — Asistente Contratos (semanas 21-34)

**Semanas 21-22: Análisis de Documentos Fuente**
- Mapeo de todos los campos a extraer por tipo de documento
- Definir reglas de consistencia cruzada (con área legal)
- Catalogar variables por tipo de contrato
- Preparar plantillas de contrato con área jurídica

**Semanas 23-25: Extracción Multi-Documento**
- Extender pipeline OCR para múltiples documentos por expediente
- Desarrollar extractores específicos:
  - Bases Integradas → objeto, monto referencial, plazo, forma de pago, garantía
  - Oferta Económica → monto oferta, forma de pago propuesta
  - Oferta Técnica → entregables, metodología, equipo profesional
  - Vigencia de Poder → representante legal, poderes, vencimiento
  - Tipo de Garantía → entidad garante, monto, vigencia

**Semanas 26-28: Motor de Validación Cruzada**
- Implementar validador de consistencia:
  - `monto_contrato == monto_oferta_economica`
  - `plazo_contrato == plazo_bases_integradas`
  - `representante_legal == vigencia_de_poder.representante`
  - `tipo_garantia in Bases_Integradas.garantias_aceptadas`
- Interfaz de revisión con diferencias resaltadas
- Flujo de alerta si hay inconsistencia (no bloqueo, solo advertencia)

**Semanas 29-31: Generación de Contrato y Revisión Legal**
- Motor docxtpl para contratos (más complejo que Bases)
- Flujo de revisión humana obligatoria con firma digital (o aprobación en sistema)
- Historial de versiones del contrato
- Exportación a PDF opcional (LibreOffice headless)

**Semanas 32-34: QA Legal, Seguridad y Despliegue**
- Revisión legal de 10 contratos generados vs contratos históricos
- Pruebas de regresión del Asistente de Bases (no degradar)
- Piloto con área de contratos (5 expedientes reales)
- Ajustes y despliegue en producción

---

# H. RIESGOS TÉCNICOS Y FUNCIONALES

## Riesgos de Alta Criticidad

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **Alucinaciones del LLM** generan datos incorrectos en el contrato | Media | **Crítico** | RAG con grounding obligatorio; revisión humana; confidence score; no LLM puro para campos críticos |
| R2 | **SIGED sin API disponible** bloquea el flujo automatizado | Alta | Alto | Diseñar flujo alternativo con carga manual desde día 1 |
| R3 | **TDR escaneados de baja calidad** generan OCR con errores | Alta | Alto | Preprocesado de imagen; threshold de confianza; solicitar documentos digitales |
| R4 | **Restricción de envío de datos a cloud** impide uso de Azure OpenAI / Textract | Media | Alto | Arquitectura on-premise desde el diseño; no asumir cloud desde inicio |
| R5 | **Cambios en plantillas de Bases** rompen el mapper de datos | Alta | Medio | Versionado de plantillas; tests automatizados de render |
| R6 | **Inconsistencia normativa** en contratos generados | Media | **Crítico** | Revisión legal obligatoria; no permitir descarga de versión "FINAL" sin aprobación |
| R7 | **Falta de adoption del usuario** operador | Alta | Alto | Piloto temprano; capacitación; UX intuitiva; no reemplazar el proceso manual abruptamente |
| R8 | **GPU on-premise sin disponibilidad** para LLM local | Media | Alto | Contrato de cloud como fallback; arquitectura con abstracción de proveedor LLM |

## Riesgos de Media Criticidad

| # | Riesgo | Mitigación |
|---|---|---|
| R9 | Latencia alta del LLM (>30s) frustra usuarios | Feedback de progreso en tiempo real; procesamiento asíncrono |
| R10 | Cambios en API SIGED sin notificación | Tests de contrato de API (Pact); alertas de error en integración |
| R11 | Deuda técnica por rush en MVP | Revisiones de código; no sacrificar seguridad por velocidad |
| R12 | Pérdida de documentos en MinIO sin backup | Backup automático diario; replicación; no MVP sin backup |
| R13 | Prompt injection en campos del formulario | Sanitización de inputs; no concatenar directamente al prompt |
| R14 | Acumulación de documentos sin política de retención | Lifecycle policy desde el inicio; alinearlo con normas de archivo institucional |

---

# I. PREGUNTAS CLAVE PARA CADA EQUIPO

## Para el Equipo Funcional (Bases y Contratos)

1. ¿Cuántos tipos de plantillas de Bases existen actualmente? ¿Están en formato .docx editable o solo PDF?
2. ¿Cuáles son los 10 campos más críticos a extraer del TDR para llenar las Bases?
3. ¿Existe un catálogo de variables que debe llenarse en cada tipo de plantilla?
4. ¿El proceso actual de revisión de Bases es hecho por una o varias personas? ¿En cuánto tiempo?
5. Para Contratos: ¿cuál es el proceso actual cuando hay inconsistencia entre la oferta ganadora y las Bases?
6. ¿Con qué frecuencia cambian las plantillas de Bases y Contratos (normas OSCE)?
7. ¿Cuántos expedientes de Bases y Contratos se generan mensualmente?

## Para el Equipo de Infraestructura / TI

1. ¿Existe política de seguridad que prohíba el envío de documentos fuera de la red de la entidad?
2. ¿Hay servidores disponibles para despliegue on-premise? ¿Con qué capacidad (CPU, RAM, disco)?
3. ¿Existe contrato vigente con AWS, Azure u otro proveedor cloud? ¿Con qué límites de uso?
4. ¿Hay GPU disponibles o posibilidad de adquirirlas para LLM on-premise?
5. ¿Cuál es el proceso de despliegue de nuevas aplicaciones en la entidad (aprobaciones, ventanas de mantenimiento)?
6. ¿Existe un repositorio Git institucional o se puede usar uno externo (GitHub/GitLab)?
7. ¿Cuál es el ancho de banda disponible para subir/bajar documentos grandes desde los clientes?

## Para el Equipo de Seguridad

1. ¿Existe un sistema de gestión de identidades (Active Directory, LDAP) para integrar SSO?
2. ¿Hay clasificación de datos definida para los documentos TDR, Bases y Contratos? ¿Son reservados/confidenciales?
3. ¿Existen políticas de cifrado de datos en reposo para sistemas internos?
4. ¿Se requiere firma digital (con token/certificado) para aprobar documentos generados?
5. ¿Hay logs centralizados actualmente? ¿Qué SIEM institucional se usa?
6. ¿Cuánto tiempo deben retenerse los documentos generados y los logs de actividad?
7. ¿Hay restricciones normativas (Ley 29733, directivas PCM) que apliquen a este sistema?

## Para el Equipo SIGED / Sistema Documentario

1. ¿SIGED expone una API REST o SOAP? ¿Hay documentación técnica disponible?
2. ¿Existe un ambiente de pruebas (sandbox) para desarrollo de integraciones?
3. ¿Qué datos devuelve la consulta de un expediente? ¿Incluye URLs de descarga de documentos?
4. ¿Cuál es la autenticación requerida para consumir la API (OAuth2, API Key, JWT, Basic Auth)?
5. ¿Hay límites de tasa (rate limiting) para las consultas a la API?
6. ¿Los documentos del expediente están en PDF digital o escaneados?
7. ¿Qué SLA tiene el equipo SIGED para soporte a integraciones?

---

# J. CONCLUSIÓN FINAL Y PROPUESTA PRIORIZADA

## Stack Tecnológico Recomendado (Opción Principal)

| Capa | Tecnología | Justificación |
|---|---|---|
| **Frontend** | React + TypeScript + shadcn/ui + Nginx | Maduro, equipo amplio, visor documental con PDF.js |
| **Backend** | FastAPI (Python 3.12) | Ecosistema Python ideal para NLP/OCR; async nativo; OpenAPI automático |
| **Cola de tareas** | Celery + Redis | Simple para MVP; escalable para producción |
| **Orquestador avanzado** | Temporal (producción) | Workflows duraderos con retry para flujos complejos de Contratos |
| **OCR** | Azure Doc Intelligence (cloud) / PaddleOCR (on-premise) | Mejor balance precisión-customización; fallback local |
| **NLP/Extracción** | Reglas (Python) + LLM (structured output con `instructor`) + Pydantic | Híbrido: determinista donde es posible, LLM donde necesario |
| **LLM** | Azure OpenAI GPT-4o (cloud) / Mistral Large 3 + vLLM (on-premise) | Según restricciones de datos; abstracción via `LLMProvider` |
| **Vector DB / RAG** | PostgreSQL + pgvector (MVP) → Qdrant (producción) | Mínima complejidad operativa; migración sin cambio de interfaz LangChain |
| **Plantillas** | docxtpl + python-docx | Jinja2 en Word; mantenimiento por área funcional sin código |
| **Storage** | MinIO (on-premise) / Azure Blob (cloud) | API S3-compatible; versionado; acceso temporal con pre-signed URLs |
| **Base de datos** | PostgreSQL 16 | ACID; JSONB; pgvector; trazabilidad SQL; sin costo de licencia |
| **IAM** | Keycloak | OAuth2/OIDC; RBAC; integración AD; self-hosted |
| **Secretos** | HashiCorp Vault | Gestión centralizada; rotación automática; audit log |
| **Infraestructura MVP** | Docker Compose | Operación simple; zero cloud; portable |
| **Infraestructura Producción** | K3s / Kubernetes | HA; despliegue declarativo; mismo manifiesto cloud/on-premise |
| **CI/CD** | GitLab CI self-hosted + Trivy + SonarQube | Código y pipeline en intranet; DevSecOps integrado |
| **Observabilidad** | OpenTelemetry + Grafana + Loki + Prometheus + Tempo | Stack FOSS completo; sin vendor lock-in |

## Propuesta de Inversión (3 escenarios)

| Escenario | Infraestructura | LLM | Costo mensual aprox. | Recomendado para |
|---|---|---|---|---|
| **Opción A: Todo cloud Azure** | Azure Container Apps | Azure OpenAI GPT-4o | $350-600/mes | Si ya hay convenio Azure; sin restricciones datos |
| **Opción B: Híbrido** | On-premise compute | Azure OpenAI (solo LLM) | $150-300/mes | Datos sensibles locales; LLM en Azure VPN |
| **Opción C: Todo on-premise** | Servidor propio + GPU | Mistral Large 3 (local) | $0 (OPEX) + inversión GPU ~$40-80K | Máxima privacidad; presupuesto inicial disponible |

## Decisión Recomendada Final

> **Iniciar con Opción B (Híbrida)** para el MVP:
> - Backend, OCR (PaddleOCR local), storage (MinIO), base de datos (PostgreSQL) y frontend: **on-premise en Docker Compose**.
> - LLM: **Azure OpenAI GPT-4o** vía API con Data Privacy Agreement, acceso por VPN corporativa o ExpressRoute.
> - Esta opción minimiza el riesgo de datos sensibles (TDR y Contratos nunca salen del servidor de aplicación), reduce la inversión en GPU y permite entregar el MVP en 12 semanas.
> - En Fase 4 (producción), evaluar la migración completa a on-premise con GPU si el presupuesto lo permite, o mantener el modelo híbrido con controles de seguridad documentados.

## Hoja de Ruta Resumida

```
SEMANA 1-2:   Decisiones arquitectónicas + infra base + acuerdo SIGED
SEMANA 3-12:  MVP Asistente Bases (Fase 1)
SEMANA 13-20: Fortalecimiento OCR/NLP + plantillas (Fase 2)
SEMANA 21-34: Asistente Contratos (Fase 3)
SEMANA 35-42: Validación avanzada + producción HA (Fase 4)
```

---

## Referencias Técnicas

- Azure AI Document Intelligence: https://learn.microsoft.com/azure/ai-services/document-intelligence/
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- docxtpl: https://docxtpl.readthedocs.io/
- Temporal: https://temporal.io/docs
- LangChain: https://python.langchain.com/docs/
- pgvector: https://github.com/pgvector/pgvector
- Qdrant: https://qdrant.tech/documentation/
- Mistral Large 3: https://mistral.ai/news/mistral-large-2407/
- vLLM: https://docs.vllm.ai/
- HashiCorp Vault: https://developer.hashicorp.com/vault
- Keycloak: https://www.keycloak.org/documentation
- MinIO: https://min.io/docs/minio/
- OpenTelemetry: https://opentelemetry.io/docs/
- instructor (structured LLM output): https://python.useinstructor.com/
- Reglamento de Contrataciones del Estado (OSCE): https://portal.osce.gob.pe/osce/

---

*Documento generado como investigación técnica. Las estimaciones de costo son referenciales y deben validarse con cotizaciones actuales. Revisar disponibilidad de servicios en región Latinoamérica/Perú antes de seleccionar proveedor cloud.*