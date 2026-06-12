Con la información recopilada, puedo ahora desarrollar una investigación completa y estructurada. Voy a generar el documento de arquitectura de soluciones cloud con todas las alternativas tecnológicas comparadas.

***

# A. Resumen Ejecutivo

Esta investigación propone una arquitectura desde cero para dos asistentes de IA en entidad pública peruana: **Asistente de Bases Estándar** (flujo acotado basado en TDR) y **Asistente de Contratos** (complejo,多-documental con validación normativa). 

**Recomendación central:** Para MVP, adoptar **arquitectura Azure-first** con Azure OpenAI + Azure AI Document Intelligence + FastAPI en contenedores, aprovechando que Perú tiene región Azure en Sudamérica y mejor cumplimiento de residencia de datos para entidades públicas. Para producción escalable, migrar a **arquitectura híbrida** con LLMs open source on-premise (Llama 3.1/Mistral/Qwen) para documentos sensibles, manteniendo servicios cloud solo para OCR y orquestación. [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)

**Decisión crítica:** Bases debe implementarse primero (Fase 1-2) porque tiene flujo más acotado, menos documentos fuente, y valida OCR/NLP+plantillas antes de enfrentar la complejidad contractual de validación de consistencia y revisión legal (Fase 3-4).

**Componentes de mayor costo:** OCR (~$1-1.67/1K páginas), LLM (~$0.001-0.03/token según modelo), y vector database para RAG. Para MVP low-cost, usar Tesseract/PaddleOCR open source + pgvector en PostgreSQL + Llama local vía Ollama. [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)

***

# B. Tabla Comparativa por Componente

## 1. Frontend / Interfaz de usuario

| Componente | Alternativa AWS | Alternativa Azure | Alternativa open source/on-premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Complejidad | Riesgos principales |
|------------|---------------|-----------------|------------------------------------|----------|-------------|-------------------|-------------------------|-------------|---------------------|
| Chatbot/Asistente web | AWS Amplify + Amazon Bot | Azure App Service + Azure AI Chat | React/Vue.js + FastAPI backend | Azure tiene mejor integración con Office/docx; Amplify es rápido para prototipos | AWS Bot tiene menos capacidades NLP nativas; React requiere más desarrollo | **Azure App Service + React** | **React + FastAPI en contenedores K8s** | Medio | UX pobre si no hay visor documental integrado; falta de validación en tiempo real |

**Frameworks recomendados:** React (mejor ecosistema) o Vue.js (más ligero). Componentes clave: visor documental (PDF.js o Microsoft PDF Viewer), formularios dinámicos (React Hook Form), revisión de datos (tabla con highlighting de extracciones).

***

## 2. Backend / Orquestador

| Componente | Alternativa AWS | Alternativa Azure | Alternativa open source/on-premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Complejidad | Riesgos principales |
|------------|---------------|-----------------|------------------------------------|----------|-------------|-------------------|-------------------------|-------------|---------------------|
| Coordinador flujos | AWS Lambda + Step Functions | Azure Functions + Logic Apps | **FastAPI + Temporal.io** | **Temporal es cloud-agnostic, deterministic replay, mejor para microservicios multi-cloud**  [debugg](https://debugg.ai/resources/queue-is-not-a-workflow-engine-durable-execution-temporal-step-functions-2025) | Step Functions es solo AWS; Logic Apps tiene coste alto | **FastAPI + Temporal** | **Temporal managed + FastAPI en K8s** | Medio-alto | Workflows largos sin durable execution pierden estado; errores en orquestación difíciles de debug |

**Comparativa clave:**
- **Temporal**: Cloud-agnostic ✅, code-first workflows ✅, alta escalabilidad ✅, ideal para microservicios [dev](https://dev.to/federico_bevione/transactions-in-microservices-part-3-saga-pattern-with-orchestration-and-temporalio-3e17)
- **Step Functions**: Solo AWS ❌, declarativo JSON ⚖️, buena integración IAM AWS ✅, rápido para automatización AWS 🔹 [dev](https://dev.to/federico_bevione/transactions-in-microservices-part-3-saga-pattern-with-orchestration-and-temporalio-3e17)
- **Logic Apps**: Azure-only ❌, retry policies built-in ✅, good for integration steps ✅ [wifitalents](https://wifitalents.com/best/workflow-orchestration-software/)

**Para MVP:** FastAPI (Python) es más rápido para IA/OCR por integración nativa con LangChain/spaPy. Para producción con Java/Spring existente, usar Spring Boot + Temporal.

***

## 3. Integración con SIGED / sistema documentario

| Pattern | API REST/SOAP | Colas (SQS/SQS) | Webhooks | Batch extracción |
|---------|---------------|---------------|----------|------------------|
| **Cuando existe API** | ✅ Patrón principal | ✅ Para asincronía | ⚠️ Si SIGED lo supporta | ❌ No necesario |
| **Autenticación** | OAuth2/API Key | OAuth2 + colas autorizadas | JWT | N/A |
| **Manejo errores** | Retry + circuit breaker |_DLQ_ (Dead Letter Queue) | Re-invocación | Batch retry |
| **Sin API disponible** | ⚠️ Usar **RPA + screen scraping** o **extracción CSV exportada** | | | |

**Buenas prácticas:**
- Descarga: usar colas para archivos grandes (>10MB), timeout 30s, retry 3 veces
- Metadatos: guardar en DB junto con referencia S3/Blob
- Auditoría: log de cada llamada SIGED con timestamp, user_id, expediente_id
- Sin API: solicitar export batch semanal CSV + archivos ZIP, o usar integración directa vía base datos si SIGED es SQL

***

## 4. Almacenamiento documental

| Componente | AWS S3 | Azure Blob Storage | MinIO | File server interno |
|------------|--------|-------------------|-------|---------------------|
| **Cifrado** | AES-256 + FIPS 140-2 ✅ | AES-256 + FIPS 140-2 ✅  [azure.microsoft](https://azure.microsoft.com/es-es/products/storage/blobs/?msockid=3a33b194ba9e618f0c17a79ebba2603d) | AES-256 (self-managed) ✅ | TLS + cifrado disco (configurable) |
| **Ciclo vida** | Lifecycle rules ✅ | Lifecycle policies ✅ | Scripts manuales ❌ | Manual ❌ |
| **Versionado** | ✅ | ✅ | ⚠️ (requiere config) | ❌ |
| **Acceso seguro** | IAM + VPC ✅ | IAM + Private Endpoint ✅ | RBAC + HTTPS ✅ | LDAP/AD + firewall |
| **Costo 1TB/mes** | ~$23 (S3 Standard) | ~$20 (Standard) | ~$0 (solo infra) | ~$0 (solo infra) |

**Recomendación MVP:** Azure Blob Storage (mejor integración con Azure OpenAI + región Sudamérica). [azure.microsoft](https://azure.microsoft.com/es-es/products/storage/blobs/?msockid=3a33b194ba9e618f0c17a79ebba2603d)

**Recomendación Producción:** **MinIO on-premise** para documentos sensibles (datos no salen de red institucional) + S3/Blob solo para plantillas y documentos generados no sensibles. [geekflare](https://geekflare.com/es/software/best-object-storage/)

***

## 5. Base de datos / Persistencia

| Componente | PostgreSQL | SQL Server | DynamoDB | Cosmos DB | MongoDB | SQLite (MVP) |
|------------|------------|------------|----------|-----------|---------|--------------|
| **Estado proceso** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Historial/auditoría** | ✅ (JSONB + índices) | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Datos extraídos** | ✅ (JSONB) | ✅ | ✅ | ✅ | ✅ (ideal) | ⚠️ |
| **Usuarios/RBAC** | ✅ | ✅ | ⚠️ | ✅ | ✅ | ❌ |
| **pgvector (RAG)** | ✅ nativo | ⚠️ (requiere ext) | ❌ | ❌ | ⚠️ (Atlas) | ❌ |
| **Costo producción** | ~$50-200/mes (RDS) | ~$100-400/mes | ~$100-500/mes | ~$200-800/mes | ~$100-400/mes | ~$0 |
| **MVP** | ✅ | ⚠️ | ❌ | ❌ | ✅ | ✅ prototipo |
| **Producción** | ✅ **Recomendado** | ⚠️ (si existe SQL institucional) | ❌ (costo alto) | ❌ (costo alto) | ⚠️ | ❌ |

**Recomendación MVP:** SQLite para prototipo local, PostgreSQL para MVP en cloud. [sangeethasaravanan.medium](https://sangeethasaravanan.medium.com/milvus-vs-pgvector-vs-chroma-which-vector-database-should-you-choose-6bf14b34242c)

**Recomendación Producción:** **PostgreSQL + pgvector** (única opción que combina datos transaccionales + vectores RAG en mismo DB, costo bajo, open source). [altexsoft](https://www.altexsoft.com/blog/vector-databases-compared/)

***

## 6. OCR

| Componente | AWS Textract | Azure AI Document Intelligence | Google Document AI | Tesseract OCR | PaddleOCR |
|------------|--------------|-------------------------------|-------------------|---------------|-----------|
| **Precisión OCR (imprimido)** | 98.8% (1.2% CER) | **99.1% (0.9% CER)** ✅  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | 95%  [aimultiple](https://aimultiple.com/es/ocr-accuracy) | 85-90% | **92.1% word accuracy**  [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf) |
| **Precisión OCR (manuscrito)** | 96.2% (3.8% CER) | 95.9% (4.1% CER)  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | ~90% | 70-80% | 85% |
| **Tablas** | **82.1%** ✅  [hackernoon](https://hackernoon.com/lang/es/puede-tu-llm-manejar-una-factura-he-probado-5-aqui-esta-la-verdad) | 78% | 75% | 60% | **85%** ✅  [oajmist](https://www.oajmist.com/index.php/12/article/download/389/285) |
| **Español** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PDFs escaneados** | ✅ | ✅ **mejor para layouts complejos**  [youtube](https://www.youtube.com/watch?v=ldE8UKs2F10) | ✅ | ⚠️ | ✅ |
| **Formularios** | ✅ pre-trained | ✅ **custom models** ✅  [youtube](https://www.youtube.com/watch?v=ldE8UKs2F10) | ✅ | ❌ | ⚠️ |
| **Costo/1K páginas** | ~$1.5 | ~$1.67 | ~$1.20 | **$0** | **$0** |
| **MVP** | ✅ si AWS | ✅ **si Azure** | ⚠️ | ❌ precisión baja | ✅ **low-cost** |
| **Producción** | ✅ enterprise | ✅ **enterprise mejor**  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | ⚠️ | ❌ | ⚠️ solo low-budget |

**Recomendación MVP:** **Azure AI Document Intelligence** para MVP Azure (mejor precisión layouts complejos, custom models). [youtube](https://www.youtube.com/watch?v=ldE8UKs2F10)

**Recomendación Producción:** **Azure AI Document Intelligence** para producción enterprise (precisión 99.1%, cumplimiento HDS, custom training). Para low-budget: **PaddleOCR** (92.1% word accuracy, mejor que Tesseract en tablas). [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf)

**Cuándo usar cada:**
- **Azure Document Intelligence**: layouts complejos, formularios custom, alta precisión requerida [youtube](https://www.youtube.com/watch?v=ldE8UKs2F10)
- **AWS Textract**: ya en AWS ecosystem, batch processing alto volumen, tablas [youtube](https://www.youtube.com/watch?v=ldE8UKs2F10)
- **PaddleOCR**: presupuesto limitado, documentos administrativos estándar, tablas [codesota](https://www.codesota.com/ocr/paddleocr-vs-tesseract/)
- **Tesseract**: solo prototipo ultra-low-cost, documentos simples impresos [codesota](https://www.codesota.com/ocr/paddleocr-vs-tesseract/)

***

## 7. NLP / Extracción de información

| Componente | Azure OpenAI | AWS Bedrock | Amazon Comprehend | spaCy | LangChain + LLM open |
|------------|--------------|-------------|-------------------|-------|---------------------|
| **Extracción campos** | ✅ **classification + extraction** | ✅ | ⚠️ solo pre-trained | ✅ regras + ML | ✅ **flexible + RAG** |
| **CLM (clasificación)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Embeddings** | ✅ | ✅ | ✅ | ⚠️ | ✅ (HuggingFace) |
| **RAG** | ✅ | ✅ | ❌ | ❌ | ✅ **mejor implementación** |
| **Español** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Datos sensibles** | ✅ **residencia EU/Perú**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | ✅ **datos no salen AWS**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | ❌ US-only | ✅ local | ✅ **100% local** |
| **Costo** | ~$0.001-0.03/token | ~$0.0008-0.02/token | ~$1-10/1K docs | **$0** | ~$0 (local) + GPU |
| **MVP** | ✅ **si Azure** | ✅ si AWS | ❌ poco flexible | ✅ prototipo | ✅ **low-cost** |
| **Producción** | ✅ enterprise | ✅ enterprise | ❌ | ⚠️ solo reglas | ✅ **sensible datos** |

**Enfoque robusto para datos sensibles:**
1. **Pipelines híbridos**: reglas determinísticas (spaCy) para campos estructurados (monto, plazo) + LLM para texto semántico (descripciones) [redwerk](https://redwerk.es/blog/mejores-practicas/)
2. **RAG Local**: embeddings local (HuggingFace) + LLM local (Ollama/vLLM) on-premise, datos no salen red [proyectosapasionantes](https://proyectosapasionantes.com/rag-retrieval-augmented-generation/)
3. **Confidence score**: LLM devuelve score 0-1; si <0.8, requiere validación humana [sangeethasaravanan.medium](https://sangeethasaravanan.medium.com/milvus-vs-pgvector-vs-chroma-which-vector-database-should-you-choose-6bf14b34242c)

***

## 8. Motor de IA generativa / LLM

| Componente | Azure OpenAI | AWS Bedrock | Amazon Q | OpenAI API | Llama 3.1/Mistral/Qwen (open) |
|------------|--------------|-------------|----------|------------|-------------------------------|
| **Privacidad** | ✅ **residencia EU**  [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd) | ✅ **datos no salen cuenta**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | ✅ AWS-only | ❌ US data center | ✅ **100% on-premise** |
| **Residencia datos** | ✅ UK/EU Frankfurt  [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd) | ✅ eu-central-1 (Frankfurt)  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | ✅ AWS | ❌ | ✅ local |
| **Costo** | ~$0.001-0.03/token | ~$0.0008-0.02/token  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | ~$0.002/token | ~$0.005-0.06/token | ~$0 (solo GPU $50-200/mes) |
| **Razonamiento** | ✅ **GPT-4o mejor** | ✅ (picks mismo modelo) | ✅ | ✅ | ⚠️ Llama 3.1 ~GPT-3.5 |
| **Español** | ✅ | ✅ | ✅ | ✅ | ✅ Qwen3 **mejor español**  [xataka](https://www.xataka.com/robotica-e-ia/nuevo-rey-ia-open-source-alibaba-su-estrategia-sencilla-ser-cansina) |
| **Integración empresa** | ✅ **Azure AD** | ✅ IAM AWS | ✅ AWS | ⚠️ | ⚠️ self-managed |
| **Auditoría** | ✅ Azure Monitor | ✅ CloudWatch | ✅ | ⚠️ | ❌ self |
| **Gobernanza** | ✅ **FedRAMP, RGPD**  [aws.amazon](https://aws.amazon.com/es/bedrock/) | ✅ **FedRAMP High, RGPD**  [aws.amazon](https://aws.amazon.com/es/bedrock/) | ✅ | ⚠️ | ❌ |
| **MVP** | ✅ **recomendado** | ✅ | ❌ | ❌ | ✅ low-cost |
| **Producción** | ✅ enterprise | ✅ enterprise | ❌ | ❌ sensibles | ✅ **datos sensibles** |

**Alternativas por escenario:**
- **Cloud (Azure-first):** Azure OpenAI (GPT-4o) + residencia EU [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd)
- **Cloud (AWS-first):** AWS Bedrock (Llama 3.1/Mistral) + datos dentro cuenta [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)
- **Híbrido:** LLM open on-premise (Qwen3/Llama 3.1) para sensibles + cloud para no sensibles [proyectosapasionantes](https://proyectosapasionantes.com/rag-retrieval-augmented-generation/)
- **On-premise total:** **Qwen3** (mejor español open source 2025) o **Llama 3.1 405B** vía Ollama/vLLM [xataka](https://www.xataka.com/robotica-e-ia/nuevo-rey-ia-open-source-alibaba-su-estrategia-sencilla-ser-cansina)

**Si entidad pública no puede enviar documentos externos:** ❌ OpenAI API (datos van US), ❌ Azure OpenAI si no tiene región local, ✅ **AWS Bedrock** (datos no salen cuenta)  o ✅ **LLM open on-premise**. [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)

***

## 9. RAG / Base de conocimiento

| Componente | Azure AI Search | Amazon OpenSearch | Amazon Kendra | PostgreSQL + pgvector | ChromaDB | Weaviate | Milvus |
|------------|-----------------|-------------------|---------------|---------------------|----------|----------|--------|
| **Indexación** | ✅ nativa Azure | ✅ | ✅ pre-trained | ✅ manual | ✅ simple | ✅ híbrida | ✅ escalable |
| **Búsqueda híbrida** | ✅ **best**  [windowsforum](https://windowsforum.com/threads/azure-only-rag-ai-delivers-latency-wins-and-lower-tco-pt-study.381600/?amp=1) | ✅ | ⚠️ | ✅ (keyword + vector) | ❌ | ✅ | ✅ |
| **Reranking** | ✅ | ⚠️ | ❌ | ⚠️ (requiere extra) | ❌ | ✅ | ✅ |
| **Trazabilidad fuentes** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **Versionado** | ✅ | ✅ | ✅ | ✅ (temp tables) | ❌ | ✅ | ✅ |
| **Actualización** | ✅ incremental | ✅ | ⚠️ batch | ✅ | ❌ | ✅ | ✅ |
| **Escala (vectores)** | ~1M | ~10M | ~1M | ~100K-1M | ~10K | ~1M | **billions**  [sangeethasaravanan.medium](https://sangeethasaravanan.medium.com/milvus-vs-pgvector-vs-chroma-which-vector-database-should-you-choose-6bf14b34242c) |
| **Costo** | ~$100-500/mes | ~$150-600/mes | ~$200-800/mes  [switchsoftware](https://www.switchsoftware.io/post/what-is-aws-kendra) | **~$50-200/mes** | **~$0** | ~$100-300/mes | ~$200-500/mes |
| **MVP** | ✅ si Azure | ✅ si AWS | ❌ caro | ✅ **recomendado** | ✅ prototipo | ✅ | ❌ sobre-engineering |
| **Producción** | ✅ enterprise | ✅ | ⚠️ | ✅ **si <1M vectores** | ❌ | ✅ mid-scale | ✅ **billions** |

**Recomendación MVP:** **PostgreSQL + pgvector** (única DB que combina datos transaccionales + vectores, costo bajo, open source). [altexsoft](https://www.altexsoft.com/blog/vector-databases-compared/)

**Recomendación Producción:**
- **<1M vectores:** PostgreSQL + pgvector ✅
- **1M-100M vectores:** Weaviate ✅
- **>100M vectores:** **Milvus** (billions de vectores, high performance) [sangeethasaravanan.medium](https://sangeethasaravanan.medium.com/milvus-vs-pgvector-vs-chroma-which-vector-database-should-you-choose-6bf14b34242c)

**Cuándo no usar Kendra:** Kendra es 88.8% más lento que Azure AI Search en search-layer, más caro, y mejor para business users no técnicos. [windowsforum](https://windowsforum.com/threads/azure-only-rag-ai-delivers-latency-wins-and-lower-tco-pt-study.381600/?amp=1)

***

## 10. Motor de plantillas documentales

| Componente | docxtpl | python-docx | Apache POI | OpenXML SDK | Aspose.Words | docx4j |
|------------|---------|-------------|------------|-------------|--------------|--------|
| **Lenguaje** | Python | Python | Java | .NET | Multi | Java |
| **Plantillas Jinja2** | ✅ **mejor**  [docs-python](https://docs-python.ru/packages/modul-python-docx-python/modul-docx-template/) | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Mantener formato** | ✅ | ✅ | ✅ | ✅ | ✅ **best** | ✅ |
| **Tablas** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Campos variables** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Secciones condicionales** | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| **Numeración** | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| **Revisión legal** | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| **Costo** | **$0** | **$0** | **$0** | **$0** | ~$1000-3000/licencia | **$0** |
| **MVP** | ✅ **recomendado** | ✅ | ⚠️ Java | ⚠️ .NET | ❌ caro | ✅ |
| **Producción** | ✅ | ✅ | ✅ (si Java) | ✅ (si .NET) | ✅ enterprise | ✅ |

**Recomendación:** **docxtpl** para MVP y producción Python (Jinja2 templates, fácil mantenimiento, $0). [docs-python](https://docs-python.ru/packages/modul-python-docx-python/modul-docx-template/)

**Alternativa enterprise:** **Aspose.Words** si requiere numeración automática compleja, revisiones legalizadas, y ya tiene licencias ($1000-3000 pero mejor soporte formatos complejos).

***

## 11. Generación y descarga de documentos

| Aspecto | Síncrona | Asíncrona |
|---------|----------|-----------|
| **cuándo** | documentos <5MB, timeout <30s | documentos >5MB, OCR lento, colas |
| **MVP** | ✅ FastAPI endpoint | ⚠️ agrega complejidad |
| **Producción** | ⚠️ timeout riesgo | ✅ **Temporal + colas** |
| **Versionado** | guardar en DB + storage | guardar en DB + storage + event log |
| **Marcas agua** | "BORRADOR" si confidence <0.8 | mismo |
| **Metadatos** | author, created, expediente_id | mismo + processing_time |

**Recomendación:** MVP síncrona (simplifica desarrollo), producción asíncrona con Temporal (evita timeouts, mejor observabilidad).

***

## 12. Validación y control de calidad

| Método | Reglas determinísticas | Validación LLM | Validación humana | Confidence score | Doble verificación |
|--------|---------------------|---------------|-----------------|----------------|------------------|
| **Campo estructurado** (monto, plazo) | ✅ **100% preciso** | ❌ overkill | ⚠️ lento | ✅ | ✅ |
| **Campo semántico** (descripción) | ❌ | ✅ | ✅ obligatorio | ✅ | ✅ |
| **Evitar alucinaciones** | ✅フィルタ | ✅ **Bedrock Barreras 99%**  [aws.amazon](https://aws.amazon.com/es/bedrock/) | ✅ | ✅ **<0.8 = humano** | ✅ |
| **Contratos: consistencia** | ✅ monto/plazo cruzado | ✅ texto | ✅ legal | ✅ | ✅ |

**Mecanismos para evitar alucinaciones:**
1. **Bedrock/Azure Barreras**: bloquean 88% contenido dañino, 99% precisión respuestas correctas [aws.amazon](https://aws.amazon.com/es/bedrock/)
2. **Reglas determinísticas**: validación monto = suma entregables, plazo dentro vigencia base
3. **Confidence score**: LLM devuelve 0-1; si <0.8, marca "REVISIÓN HUMANA OBLIGATORIA"
4. **RAG con fuentes**: LLM solo usa documentos indexados, cita fuente en cada dato

**Controles específicos contratos:**
| Campo | Validación |
|-------|-----------|
| Monto total | = suma entregables + ≥ oferta económica ganadora |
| Plazo | ≤ vigencia bases integradas |
| Forma pago | = bases integradas (ej: 30% anticipos) |
| Entregables | ≥ oferta técnica ganadora |
| Contratista | = RUC nombre bases |
| Representante | = oferta técnica firma |
| Garantía | = tipo bases (ej: 5% carta fianza) |

***

## 13. Seguridad, privacidad y cumplimiento

| Práctica | AWS | Azure | Open source |
|----------|-----|-------|-------------|
| **Cifrado tránsito** | TLS 1.3 ✅ | TLS 1.3 ✅ | TLS 1.3 (config) |
| **Cifrado reposo** | AES-256 + FIPS ✅ | AES-256 + FIPS ✅  [azure.microsoft](https://azure.microsoft.com/es-es/products/storage/blobs/?msockid=3a33b194ba9e618f0c17a79ebba2603d) | AES-256 (self) |
| **IAM** | IAM + roles ✅ | Azure AD + RBAC ✅ | LDAP/AD + RBAC |
| **Logging** | CloudWatch ✅ | Azure Monitor ✅ | ELK + OpenTelemetry |
| **Auditoría** | CloudTrail ✅ | Azure Audit ✅ | self (PG logs) |
| **DLP** | Macie ✅ | Purview ✅ | self (regex) |
| **Mascaramiento** | KMS ✅ | Key Vault ✅ | self (crypt) |
| **Retención** | Lifecycle ✅ | Lifecycle ✅ | scripts |
| **Segregación** | VPC + subnets ✅ | Private Endpoint ✅ | firewall + VLAN |
| **Secrets** | Secrets Manager ✅ | Key Vault ✅ | HashiCorp Vault |

**Restricciones entidades públicas:**
- ❌ No enviar documentos sensibles a US (OpenAI API) [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd)
- ✅ Usar región EU/LATAM (Azure EU Frankfurt, AWS eu-central-1) [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd)
- ✅ **AWS Bedrock**: datos no salen cuenta AWS [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)
- ✅ **LLM open on-premise**: 100% datos locales [proyectosapasionantes](https://proyectosapasionantes.com/rag-retrieval-augmented-generation/)

***

## 14. Observabilidad y auditoría

| Componente | CloudWatch | Azure Monitor | OpenTelemetry | ELK | Grafana | Prometheus |
|------------|------------|---------------|---------------|-----|---------|------------|
| **Logs** | ✅ | ✅ | ✅ | ✅ **best** | ✅ | ⚠️ |
| **Métricas** | ✅ | ✅ | ✅ | ⚠️ | ✅ **best** | ✅ **best** |
| **Traces** | ✅ X-Ray | ✅ | ✅ **standard** | ❌ | ✅ | ✅ |
| **Error monitor** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Auditoría func** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **SIEM integrado** | ✅ GuardDuty | ✅ Sentinel | ⚠️ | ⚠️ | ⚠️ | ❌ |
| **Costo** | ~$100-400/mes | ~$150-500/mes | **$0** | ~$100-300/mes | ~$50-200/mes | **$0** |
| **MVP** | ✅ AWS | ✅ Azure | ✅ | ⚠️ | ✅ | ✅ |
| **Producción** | ✅ | ✅ | ✅ **standard** | ✅ enterprise | ✅ | ✅ |

**Eventos que auditar:**
1. Login user (timestamp, user_id, IP)
2. Consulta SIGED (expediente_id, user_id, timestamp)
3. OCR procesamiento (doc_id, pages, confidence, user_id)
4. Extracción NLP (campo, valor, confidence, fuente_doc)
5. Generación docx (template, fields_filled, user_id, timestamp)
6. Revisión humana (campo, valor_original, valor_corregido, reviewer_id)
7. Descarga documento (doc_id, user_id, timestamp)

**Recomendación:** MVP CloudWatch/Azure Monitor (integrado), producción **OpenTelemetry + Grafana + ELK** (standard, costo bajo, multi-cloud). [devblogs.microsoft](https://devblogs.microsoft.com/ise/using-opentelemetry-for-flexible-observability/)

***

## 15. Despliegue e infraestructura

| Arquitectura | Serverless | Kubernetes | VMs | Híbrida |
|--------------|------------|------------|-----|---------|
| **Elasticidad** | ✅ instantánea | ⚠️ auto-scaling | ❌ manual | ✅ |
| **Costo tráfico esporádico** | ✅ **ahorro 30-48%**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/228458/tecnologia-lider-2026-sin-servidor-o-contenedores-ventajas-desventajas-mejor-opcion-negocio) | ❌ | ❌ | ⚠️ |
| **Costo 24x7 alto tráfico** | ❌ | ✅ **económico**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/228458/tecnologia-lider-2026-sin-servidor-o-contenedores-ventajas-desventajas-mejor-opcion-negocio) | ✅ | ⚠️ |
| **GPU/ML** | ❌ | ✅ **mejor**  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/228458/tecnologia-lider-2026-sin-servidor-o-contenedores-ventajas-desventajas-mejor-opcion-negocio) | ✅ | ✅ |
| **Portabilidad** | ❌ AWS-only | ✅ multi-cloud | ✅ | ✅ |
| **Operación** | ✅ zero-mgmt | ❌ parche K8s | ❌ parche OS | ⚠️ |
| **Superficie ataque** | ✅ menor | ⚠️ nodos | ❌ OS | ⚠️ |
| **Observabilidad** | ⚠️ trazas efímeras | ✅ local | ✅ | ✅ |
| **MVP** | ✅ Lambda | ⚠️ | ⚠️ | ❌ |
| **Producción sensibles** | ❌ | ✅ **K8s + GPU on-prem** | ✅ VM on-prem | ✅ **cloud + on-prem** |

**Recomendación MVP:** **AWS Lambda/Azure Functions** (zero ops, costo por uso). [q2bstudio](https://www.q2bstudio.com/nuestro-blog/228458/tecnologia-lider-2026-sin-servidor-o-contenedores-ventajas-desventajas-mejor-opcion-negocio)

**Recomendación Producción:** **Kubernetes + contenedores** (GPU para LLM local, portabilidad multi-cloud, costo predecible 24x7). [nivelics](https://www.nivelics.com/blog/kubernetes-vs-serverless-cuando-elegir)

**Si entidad no puede enviar sensibles cloud:** Híbrida = OCR cloud (Azure/AWS) + LLM on-premise (Qwen3/Llama) + MinIO on-prem. [proyectosapasionantes](https://proyectosapasionantes.com/rag-retrieval-augmented-generation/)

***

## 16. CI/CD y DevSecOps

| Componente | GitHub Actions | Azure DevOps | GitLab CI | Jenkins | Terraform | Bicep | CloudFormation | OpenTofu |
|------------|----------------|--------------|-----------|---------|-----------|-------|----------------|----------|
| **Integración** | ✅ GitHub nativo | ✅ Azure nativo | ✅ GitLab nativo | ❌ manual | ✅ multi-cloud | ✅ Azure | ✅ AWS | ✅ Terraform open |
| **Security scanning** | ✅ vulnerability | ✅ | ✅ | ⚠️ plugins | ❌ IAC | ❌ | ❌ | ❌ |
| **IAC** | ✅ | ✅ | ✅ | ✅ | ✅ **best** | ✅ | ✅ | ✅ (open) |
| **Costo** | ~$0-200/mes | ~$100-400/mes | ~$50-200/mes | **$0** self | **$0** | incluido | incluido | **$0** |
| **MVP** | ✅ | ✅ si Azure | ✅ | ⚠️ ops | ✅ | ✅ Azure | ✅ AWS | ✅ |
| **Producción** | ✅ | ✅ enterprise | ✅ enterprise | ❌ legacy | ✅ | ✅ | ✅ | ✅ |

**Recomendación:** **GitHub Actions + Terraform** (integración GitHub, IAC standard, security scanning built-in). [wojciechowski](https://wojciechowski.app/en/articles/github-actions-vs-azure-devops)

**Si entidad usa Azure DevOps:** Azure DevOps + Bicep (integración nativa). [wojciechowski](https://wojciechowski.app/en/articles/github-actions-vs-azure-devops)

***

## 17. Costos y licenciamiento

| Componente | Costo cloud (mensual 1K procesamientos) | Costo open source (infra) | Impacto costo |
|------------|----------------------------------------|---------------------------|---------------|
| **OCR** | ~$15-20 (Azure/AWS) | ~$0 (PaddleOCR) + GPU $50 | **ALTO** |
| **LLM** | ~$50-200 (GPT-4o) | ~$0 (Qwen3 local) + GPU $100 | **ALTO** |
| **Almacenamiento** | ~$20-30 (1TB S3/Blob) | ~$0 (MinIO) + disco $20 | Medio |
| **Vector DB** | ~$100-300 (Azure Search) | ~$0 (pgvector) | **MEDIO-ALTO** |
| **Procesamiento** | ~$30-100 (Lambda/Functions) | ~$0 (FastAPI VM) | Medio |
| **Generación docx** | ~$5-10 | ~$0 | Bajo |

**MVP low-cost (<$500/mes):**
- OCR: PaddleOCR local
- LLM: Qwen3 vía Ollama (GPU $100/mes)
- DB: PostgreSQL + pgvector
- Infra: FastAPI en VM $50/mes
- **Total:** ~$250-350/mes

**Producción escalable ($1000-3000/mes):**
- OCR: Azure AI Document Intelligence
- LLM: Azure OpenAI GPT-4o
- RAG: Azure AI Search
- Infra: K8s + contenedores
- **Total:** ~$1500-2500/mes

***

## 18. Roadmap recomendado

### Fase 1: MVP Asistente de Bases (2-3 meses)
**Por qué primero:** Flujo acotado, solo TDR + 1 plantilla, validación OCR/NLP básica, sin validación legal compleja.

**Actividades:**
1. Integración SIGED (API REST) + descarga TDR
2. OCR TDR (Azure Document Intelligence)
3. Extracción campos TDR (LangChain + GPT-4o)
4. Selección plantilla (reglas: tipo proceso → biens/servicios/consultoría)
5. Llenado docxtpl + generación .docx
6. Revisión humana (formulario validación)
7. Download documento

**KPIs:** precisión OCR >95%, precisión extracción >90%, tiempo proceso <5min.

***

### Fase 2: Fortalecimiento OCR/NLP + plantillas (1-2 meses)
**Actividades:**
1. Custom models Azure para TDR específicos
2. Pipelines híbridos: reglas (monto/plazo) + LLM (descripciones)
3. Plantillas condicionales (secciones por tipo proceso)
4. Confidence score + validación humana obligatoria <0.8
5. RAG inicial: indexar 50 bases ejemplo + normas

**KPIs:** precisión extracción >95%, reducción alucinaciones >80%.

***

### Fase 3: Asistente de Contratos (3-4 meses)
**Por qué después:** 5 documentos fuente, validación cruzada compleja, asociación manual documentos, revisión legal obligatoria.

**Actividades:**
1. DESCARGA múltiple documentos SIGED (colas async)
2. Categorización documentos (LLM classification)
3. OCR multi-documento (Bases Integradas, Oferta Económica, Oferta Técnica, Vigencia, Garantía)
4. Extracción 20+ campos (contratista, representante, monto, plazo, entregables, garantía)
5. **Validación consistencia:** contrato vs bases vs oferta (monto, plazo, pago, entregables)
6. Generación contrato .docx
7. **Trazabilidad:** campo → valor → fuente_doc → confidence
8. Revisión legal obligatoria (workflow con aprobación)

**KPIs:** precisión validación cruzada >98%, 0 alucinaciones en montos/plazos.

***

### Fase 4: Validación avanzada + auditoría + productivo (2 meses)
**Actividades:**
1. Dual verification: reglas + LLM + humano para campos críticos
2. Audit trail completo (every action logged)
3. Migration K8s + GPU on-premise (LLM local sensibles)
4. CI/CD automated + security scanning
5. Monitoring OpenTelemetry + Grafana
6. Training usuarios + documentación

**KPIs:** 99.9% uptime, <1% errores, auditoría 100% trazable.

***

# C. Arquitectura recomendada para MVP

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  - Chatbot asistente + formularios dinámicos + visor PDF    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              BACKEND (FastAPI + Temporal)                    │
│  - API REST: /bases, /contratos, /validate                   │
│  - Workflows: SIGED → OCR → NLP → plantilla → docx          │
│  - Temporal: durable execution, retry, timeout              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           SERVICIOS AZURE (cloud)                            │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Azure OpenAI   │  │ Document Intell.│  │ Blob Storage │ │
│  │ (GPT-4o)       │  │ (OCR TDR)       │  │ (docs temp)  │ │
│  └────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌────────────────┐  ┌─────────────────┐                   │
│  │ Azure AI Search│  │ PostgreSQL      │                   │
│  │ (RAG plantillas)│  │ + pgvector (DB) │                   │
│  └────────────────┘  └─────────────────┘                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│        INTEGRACIÓN SIGED (API REST)                          │
│  - OAuth2 + retry + DLQ + auditoría                          │
└─────────────────────────────────────────────────────────────┘
```

**Stack MVP:**
- Frontend: React + Vite
- Backend: FastAPI + Temporal
- OCR: Azure AI Document Intelligence
- LLM: Azure OpenAI (GPT-4o)
- RAG: Azure AI Search
- DB: PostgreSQL + pgvector
- Storage: Azure Blob
- CI/CD: GitHub Actions + Terraform

**Costo MVP:** ~$1500-2000/mes (1K procesamientos).

***

# D. Arquitectura recomendada para producción

```
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (React + K8s)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           BACKEND (FastAPI + Temporal en K8s)               │
│  - Contenedores: auto-scaling, GPU para LLM local           │
│  - Workflows: async colas para multi-doc (contratos)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────┐
│         CLOUD (Azure)              ON-PREMISE                │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Document Intel.│  │ LLM Open     │  │ MinIO          │  │
│  │ (OCR sensibles❌)│  │ (Qwen3 local)│  │ (docs sensibles)│  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Blob (no sens.)│  │ PostgreSQL   │  │ pgvector       │  │
│  │                │  │ + pgvector   │  │ (RAG local)    │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│        SIGED + SIEM institucional + OpenTelemetry           │
└─────────────────────────────────────────────────────────────┘
```

**Diferencias producción vs MVP:**
1. **LLM:** Azure OpenAI → Qwen3 local on-premise (datos sensibles no salen)
2. **Storage:** Blob solo → MinIO on-premise para sensibles
3. **Infra:** VM → K8s + GPU (auto-scaling, costo 24x7 predecible)
4. **Observabilidad:** Azure Monitor → OpenTelemetry + Grafana + ELK
5. **RAG:** Azure Search → pgvector on-premise

**Costo producción:** ~$2000-3000/mes (10K procesamientos, GPU on-prem).

***

# E. Alternativas si no existe API de SIGED

| Escenario | Alternativa | Complejidad | Riesgo |
|-----------|-------------|-------------|--------|
| **SIGED tiene export CSV/ZIP** | Extracción batch semanal CSV + unzipping | Baja | Baja (datos retraso 7 días) |
| **SIGED tiene base SQL** | Consulta directa JDBC/ODBC + metadatos | Media | Media (acceso DB requiere aprobación seguridad) |
| **SIGED solo web sin API** | **RPA + screen scraping** (Python + Selenium/Playwright) | Alta | Alta (breaks si SIGED cambia UI) |
| **SIGED SOAP legacy** | Wrapper SOAP → REST + retry | Media | Baja |

**Recomendación:** Solicitar al equipo SIGED:
1. Export batch automatizado (CSV + ZIP)
2. Acceso base SQL (si es SQL Server/PostgreSQL)
3. API REST (prioridad 1, más limpio)

Si ninguna opción: RPA con **fallback manual** (user puede upload archivos manualmente si scraping falla).

***

# F. Recomendación específica para iniciar con Bases

**Por qué Bases primero (no Contratos):**

| Factor | Bases | Contratos |
|--------|-------|-----------|
| Documentos fuente | 1 (TDR) | 5+ (Bases, Oferta Econ, Oferta Tec, Vigencia, Garantía) |
| Validación cruzada | ❌ N/A | ✅ obligatoria (monto, plazo, pago, entregables) |
| Asociación documentos | ❌ automática | ✅ manual (user categoriza) |
| Revisión legal | ⚠️ básica | ✅ obligatoria compleja |
| Campo extraídos | 5-10 | 20+ |
| Tiempo desarrollo | 2-3 meses | 3-4 meses |
| Riesgo fallo | Baja | Alta |

**Plan inicio Bases (Fase 1):**

1. **Sprint 1 (2 semanas):** Integración SIGED + descarga TDR
   - API REST OAuth2
   - Retry 3 veces + DLQ
   - Log auditoría

2. **Sprint 2 (2 semanas):** OCR TDR
   - Azure Document Intelligence
   - Custom model para TDR tipo "Bienes/Servicios/Consultoría"
   - Confidence score >0.9

3. **Sprint 3 (3 semanas):** Extracción NLP + plantillas
   - LangChain + GPT-4o extracción campos: tipo_proceso, monto_estimado, plazo, descripcion
   - Reglas: tipo_proceso → plantilla (bienes → plantilla_bienes.docx)
   - docxtpl llenado Jinja2

4. **Sprint 4 (2 semanas):** Revisión humana + download
   - Formulario validación: user corrige campos confidence <0.8
   - Download .docx + storage Blob
   - Audit trail: campo → valor → fuente → user

**KPIs éxito Fase 1:**
- Precisión OCR: >95%
- Precisión extracción: >90%
- Tiempo proceso: <5min
- US users: >80% satisfacción

***

# G. Recomendación específica para luego escalar a Contratos

**Desafíos Contratos (vs Bases):**

| Desafío | Solución |
|---------|----------|
| 5 documentos fuente | Colas async + Temporal workflows |
| Asociación manual documentos | UI con drag-drop + categorización LLM |
| Validación consistencia | Reglas determinísticas (monto = suma) + LLM cross-check |
| 20+ campos extraídos | Pipelines híbridos: reglas (monto/plazo) + LLM (descripciones) |
| Revisión legal obligatoria | Workflow con aprobación (2 reviewers) + audit trail |
| Trazabilidad completa | DB: campo → valor → fuente_doc → confidence → reviewer |

**Plan escalado Contratos (Fase 3):**

1. **Sprint 1 (3 semanas):** Multi-documento descarga + categorización
   - SIGED API + colas SQS para archivos >10MB
   - LLM classification: documento_type (Bases Integradas, Oferta Econ, etc.)
   - UI drag-drop para corrección manual

2. **Sprint 2 (4 semanas):** OCR multi-doc + extracción 20 campos
   - Azure Document Intelligence custom models por tipo
   - Campos: contratista (RUC, nombre), representante, monto_total, plazo, forma_pago, entregables (lista), tipo_garantia, vigencia
   - Pipelines híbridos: reglas (monto numeric) + LLM (descripciones texto)

3. **Sprint 3 (4 semanas):** Validación consistencia + generación contrato
   - **Reglas:** monto_contrato = suma_entregables ≥ oferta_econ_ganadora
   - **Reglas:** plazo ≤ vigencia_bases
   - **LLM:** verificar texto contradictorio bases vs oferta
   - docxtpl contrato con campos condicionales (ej: si garantía = carta_fianza → sección carta)

4. **Sprint 4 (3 semanas):** Revisión legal + trazabilidad
   - Workflow: reviewer1 → reviewer2 → aprobados
   - Audit trail: cada campo con fuente_doc, confidence, reviewer, timestamp
   - UI: highlighting diferencias bases vs oferta vs contrato

**KPIs éxito Fase 3:**
- Precisión validación cruzada: >98%
- 0 alucinaciones en montos/plazos
- Tiempo proceso: <15min
- Revisión legal: 100% obligatoria

***

# H. Riesgos técnicos y funcionales

## Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **OCR precisión baja documentos escaneados** | Media | Alto | Custom models Azure + PaddleOCR fallback + validación humana |
| **LLM alucinaciones (datos sin fuente)** | Media | Alto | RAG con fuentes + confidence score <0.8 = humano + Barreras Bedrock 99% |
| **Timeout workflows largos (contratos >30min)** | Media | Medio | Temporal async + colas + timeout configurable |
| **SIGED API cambia versión sin notify** | Media | Alto | Wrapper + version detect + fallback manual upload |
| **Costo LLM/OCR excede presupuesto** | Alta | Medio | Monitoring costo + límites daily + open source fallback |
| **GPU on-premise falla (LLM local)** | Baja | Alto | Redundancia 2 GPUs + cloud fallback (Azure OpenAI) |
| **pgvector escala mal >1M vectores** | Media | Medio | Migra a Weaviate/Milvus si >500K vectores |

## Riesgos Funcionales

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Users no confían IA (revisión 100% manual)** | Alta | Medio | Training + KPIs precisión + mejorar confidence score |
| **Revisores legales bloquean flujo (demoras)** | Alta | Alto | Workflow con 2 reviewers + SLA 48h + alertas |
| **Bases templates cambian frecuente (mantenimiento)** | Media | Medio | Versionado plantillas + docxtpl Jinja2 fácil editar |
| **Contratos inconsistentes legalmente (riesgo normativo)** | Baja | Alto | Validación reglas + review legal obligatoria + auditoría |
| **Expedientes SIGED incompletos (docs faltantes)** | Media | Medio | UI indicate missing docs + manual upload + alert admin |

***

# I. Preguntas clave al equipo

## Al equipo Funcional

1. ¿Qué tipo de procesos de contratación son más frecuentes (bienes, servicios, consultoría)?
2. ¿Cuántos expedientes SIGED se procesan mensualmente? (estimación volumen)
3. ¿Qué campos EXACTOS se extraen del TDR? (lista completa)
4. ¿Qué plantillas de Bases existen actualmente? (nombres, tipos)
5. ¿Para contratos, qué 20 campos se extraen? (lista completa con ejemplos)
6. ¿Quiénes son los revisores legales? ¿SLA de revisión?
7. ¿Qué errores frecuentes ocurren en bases/contratos actuales? (para evitar)

## Al equipo Infraestructura

1. ¿Existe API SIGED? ¿Versión? ¿Autenticación (OAuth2, API Key, SOAP)?
2. ¿Volumen archivos Expedientes SIGED? (tamaño avg, máximo, mensuales)
3. ¿Infra actual? (VMs, K8s, cloud provider, on-premise)
4. ¿GPU disponible on-premise? (modelo, cuántas)
5. ¿Límites presupuesto mensual infra?
6. ¿Backup/retención documentos? (política actual)

## Al equipo Seguridad

1. ¿Qué documentos SON SENSIBLES? (lista tipos)
2. ¿Pueden datos salir Perú? ¿Región cloud permitida? (EU, LATAM, US)
3. ¿Certificaciones requeridas? (ISO 27001, RGPD, FedRAMP, HDS)
4. ¿SIEM institucional? (producto actual)
5. ¿Política cifrado? (algoritmos, KMS propio vs cloud)
6. ¿RBAC requerido? (niveles acceso, roles)

## Al equipo SIGED

1. ¿API REST disponible? ¿Endpoint? ¿Docs?
2. ¿Si no API: export CSV/ZIP batch? ¿Frecuencia?
3. ¿Si no export: acceso base SQL? (tipo DB, credentials)
4. ¿Si solo web: screen scraping permitido? ¿RPA tool institucional?
5. ¿Metadatos expedientes? (qué campos, estructura)
6. ¿Cambios próximos API/versión? (roadmap SIGED)

***

# J. Conclusión final con propuesta priorizada

## Propuesta Priorizada (por orden implementación)

### Prioridad 1: MVP Asistente Bases (2-3 meses, ~$1500-2000/mes)

**Stack recomendado:**
- **Frontend:** React + Vite
- **Backend:** FastAPI + Temporal (cloud-agnostic, durable execution)
- **OCR:** Azure AI Document Intelligence (99.1% precisión, custom models)
- **LLM:** Azure OpenAI GPT-4o (residencia EU, FedRAMP High)
- **RAG:** Azure AI Search (búsqueda híbrida + reranking)
- **DB:** PostgreSQL + pgvector (única DB transaccional + vectores)
- **Storage:** Azure Blob Storage (cifrado AES-256 + FIPS)
- **CI/CD:** GitHub Actions + Terraform (IAC standard, security scanning)

**Por qué Azure-first:**
1. Región EU Frankfurt (residencia datos RGPD) [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd)
2. Mejor OCR para layouts complejos (99.1% vs 98.8% AWS) [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)
3. Integración nativa Office/docx (plantillas)
4. Cumplimiento HDS para entidades públicas [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)

***

### Prioridad 2: Fortalecimiento OCR/NLP (1-2 meses, +~$300-500/mes)

**Acciones:**
1. Custom models Azure para TDR específicos
2. Pipelines híbridos: reglas (monto/plazo numeric) + LLM (descripciones semántico)
3. Confidence score + validación humana <0.8
4. RAG: indexar 50 bases ejemplo + normas

**ROI:** precisión extracción >95%, reducción alucinaciones >80%.

***

### Prioridad 3: Asistente Contratos (3-4 meses, +~$1000-1500/mes)

**Stack adicional:**
- Colas async para multi-documento (SQS/SQS)
- Validación cruzada: reglas determinísticas + LLM cross-check
- Workflow revisión legal: 2 reviewers + SLA 48h
- Trazabilidad: campo → valor → fuente → confidence → reviewer

**Por qué después Bases:** Contratos tiene 5 documentos fuente, validación compleja, revisión legal obligatoria. Bases valida OCR/NLP+plantillas primero.

***

### Prioridad 4: Producción Híbrida (2 meses, ~$2000-3000/mes)

**Cambios crítico:**
1. **LLM:** Azure OpenAI → **Qwen3 on-premise** (datos sensibles 100% locales) [xataka](https://www.xataka.com/robotica-e-ia/nuevo-rey-ia-open-source-alibaba-su-estrategia-sencilla-ser-cansina)
2. **Storage:** Blob → **MinIO on-premise** para sensibles
3. **Infra:** VM → **K8s + GPU** (auto-scaling, costo predecible)
4. **Observabilidad:** Azure Monitor → **OpenTelemetry + Grafana + ELK**

**Por qué híbrida:** Cumple restricción "no enviar documentos sensibles cloud" + mantiene OCR cloud (más preciso) + LLM local (sensible).

***

## Decisiones Críticas

| Decisión | Recomendación | Razón |
|----------|---------------|-------|
| **Cloud provider** | Azure-first | Región EU, mejor OCR, cumplimiento HDS |
| **LLM sensibles** | Qwen3 on-premise | 100% datos locales, mejor español open  [xataka](https://www.xataka.com/robotica-e-ia/nuevo-rey-ia-open-source-alibaba-su-estrategia-sencilla-ser-cansina) |
| **OCR** | Azure AI Document Intelligence | 99.1% precisión, custom models  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) |
| **Orquestador** | Temporal + FastAPI | Cloud-agnostic, durable execution  [dev](https://dev.to/federico_bevione/transactions-in-microservices-part-3-saga-pattern-with-orchestration-and-temporalio-3e17) |
| **DB** | PostgreSQL + pgvector | Única transaccional + vectores, costo bajo |
| **Plantillas** | docxtpl | Jinja2 fácil, $0, mantiene formato |
| **MVP vs Producción** | Diferenciar claramente | MVP cloud rápido, producción híbrida sensible |

***

## Advertencias Clave

❌ **NO usar OpenAI API** si entidad no puede enviar datos a US (datos van región US). [levanteapp](https://www.levanteapp.com/blog/transferencias-internacionales-ia-rgpd)

❌ **NO usar Tesseract** para producción (precisión 85-90%, malo en tablas). [aimultiple](https://aimultiple.com/es/ocr-accuracy)

❌ **NO usar serverless** para producción 24x7 alto tráfico (más caro que K8s). [q2bstudio](https://www.q2bstudio.com/nuestro-blog/228458/tecnologia-lider-2026-sin-servidor-o-contenedores-ventajas-desventajas-mejor-opcion-negocio)

❌ **NO usar Kendra** para RAG (88.8% más lento que Azure Search, más caro). [windowsforum](https://windowsforum.com/threads/azure-only-rag-ai-delivers-latency-wins-and-lower-tco-pt-study.381600/?amp=1)

✅ **USAR Azure AI Document Intelligence** para OCR enterprise (99.1% precisión, custom models). [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)

✅ **USAR Temporal** para orquestación (cloud-agnostic, mejor para microservicios). [dev](https://dev.to/federico_bevione/transactions-in-microservices-part-3-saga-pattern-with-orchestration-and-temporalio-3e17)

✅ **USAR PostgreSQL + pgvector** para RAG MVP (única DB transaccional + vectores). [sangeethasaravanan.medium](https://sangeethasaravanan.medium.com/milvus-vs-pgvector-vs-chroma-which-vector-database-should-you-choose-6bf14b34242c)

✅ **USAR Qwen3/Llama 3.1 on-premise** para LLM sensibles (100% datos locales). [xataka](https://www.xataka.com/robotica-e-ia/nuevo-rey-ia-open-source-alibaba-su-estrategia-sencilla-ser-cansina)

***

**Esta arquitectura prioriza seguridad, auditabilidad y mantenibilidad, con roadmap claro MVP → producción híbrida, diferenciando claramente Bases (primero) vs Contratos (segundo).**