A continuación presento la investigación profunda con alternativas tecnológicas para la arquitectura de los dos asistentes de IA, basada en comparaciones actualizadas 2025-2026.

## A. Resumen ejecutivo

Para una entidad pública peruana con documentos sensibles y salida en **.docx**, la arquitectura recomendada prioriza:

| Criterio | Elección óptima |
|----------|---------------|
| **Privacidad de datos** | Azure OpenAI o AWS Bedrock (datos no salen del tenant)  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) |
| **OCR para español/tablas** | Azure AI Document Intelligence (0.9% CER vs 1.2% de Textract)  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) |
| **Open source OCR** | PaddleOCR (92.1% accuracy vs 75.8% de Tesseract)  [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf) |
| **Motor .docx** | docxtpl (python-docx-template) para plantillas con variables  [docxtpl.readthedocs](https://docxtpl.readthedocs.io) |
| **Orquestación MVP** | AWS Step Functions o Azure Logic Apps (serverless, bajo overhead)  [linkedin](https://www.linkedin.com/posts/shajuthomas_distributedsystems-cloudarchitecture-engineeringleadership-activity-7435998889868152832-lrlr) |
| **Vector DB MVP** | PostgreSQL + pgvector (simplicidad, <5M vectores)  [firecrawl](https://www.firecrawl.dev/blog/best-vector-databases) |
| **Frontend** | React + TypeScript (demanda laboral muy alta, ecosistema amplio)  [coderhouse](https://www.coderhouse.com/pe/coderlibrary/react-vs-vue-vs-angular-cual-aprender-primero-frontend) |

**Recomendación principal**: Para MVP usar **Azure** si la entidad ya tiene infraestructura Microsoft (Azure AD, Office 365), o **AWS** si quiere mayor flexibilidad de modelos. Para producción con datos sensibles, **evitar OpenAI API directo** y usar Azure OpenAI o AWS Bedrock. [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026)

***

## B. Tabla comparativa por componente

| Componente | Alternativa AWS | Alternativa Azure | Open source/on-premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Complejidad | Riesgos principales |
|------------|---------------|-----------------|---------------------|----------|-------------|-----------------|------------------------|-------------|---------------------|
| **1. Frontend** | AWS Amplify + React | Azure Static Web Apps + React | React/Vue/Angular自hosted | React: ecosistema más amplio, demanda laboral muy alta  [coderhouse](https://www.coderhouse.com/pe/coderlibrary/react-vs-vue-vs-angular-cual-aprender-primero-frontend) | React necesita herramientas extra para routing/state | React + TypeScript | React + Azure Static Web Apps | Bajo | Choque de curva aprendizaje Angular |
| **2. Backend/Orquestador** | AWS Lambda + Step Functions | Azure Functions + Logic Apps | FastAPI + Temporal.io | Step Functions: integración AWS nativa, serverless  [linkedin](https://www.linkedin.com/posts/shajuthomas_distributedsystems-cloudarchitecture-engineeringleadership-activity-7435998889868152832-lrlr) | Step Functions: duración corta, menos flexible | Step Functions (AWS) o Logic Apps (Azure) | Temporal.io si flujos > días  [scalewithchintan](https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows) | Medio | Overhead operacional Kubernetes |
| **3. Integración SIGED** | API Gateway + SQS | API Management + Service Bus | HTTP client + Coltawas | Patrones REST/SOAP estándar, webhooks | Sin API: requiere RPA/extracción batch | API REST + colas SQS/Service Bus | Webhooks + colas asincrónicas | Medio | Fallo autenticación SIGED |
| **4. Almacenamiento documental** | AWS S3 | Azure Blob Storage | MinIO | S3: versionado nativo, cifrado, gratis estructura  [blog.tecnetone](https://blog.tecnetone.com/azure-blob-storage-vs.-amazon-simple-storage-s3) | Azure Blob: sin cifrado lado servidor  [rootstack](https://rootstack.com/es/blog/aws-s3-vs-azure-blob-diferencias) | S3 (AWS) o Blob (Azure) | MinIO si on-premise obligatorio | Bajo | Retención no configurable |
| **5. Base de datos** | DynamoDB + PostgreSQL (RDS) | Cosmos DB + SQL Server | PostgreSQL + SQLite (MVP) | PostgreSQL: universal, pgvector incluido | DynamoDB/Cosmos: costo alto a escala | SQLite (prototipo) / PostgreSQL | PostgreSQL con replicación | Bajo | Pérdida datos sin backup |
| **6. OCR** | AWS Textract | Azure AI Document Intelligence | PaddleOCR / Tesseract | Azure: 0.9% CER, mejor multilingüe  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | Textract: mejor en tablas  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | PaddleOCR (MVP gratis) | Azure Document Intelligence  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | Medio | OCR falla en documentos escaneados |
| **7. NLP/Extracción** | Amazon Comprehend + Bedrock | Azure Comprehend + OpenAI | spaCy + LangChain + Llama | RAG + LLM: reduce alucinaciones  [nerds](https://www.nerds.ai/blog/alucinaciones-en-llms-que-son-por-que-ocurren-y-como-mitigarlas-en-produccion) | Comprehend: menos flexible para español | LangChain + spaCy | Azure OpenAI + RAG  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) | Alto | Alucinaciones LLM |
| **8. Motor LLM** | AWS Bedrock (Claude, Llama) | Azure OpenAI (GPT-4o) | Llama 3 / Mistral (self-hosted) | Bedrock: multi-modelo, datos en AWS account  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) | Azure: más caro pero data residency controlada  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) | AWS Bedrock (Llama 3 70B $1/M tokens) | Azure OpenAI si stack Microsoft  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) | Medio | Costo LLM no predecible |
| **9. RAG/Vector DB** | Amazon OpenSearch + Kendra | Azure AI Search | pgvector + ChromaDB + Weaviate | pgvector: <5M vectores, $120-200, fácil  [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/) | Kendra: caro, limitado a AWS | PostgreSQL + pgvector | Weaviate (hybrid search)  [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/) | Medio | Vector DB sin actualización |
| **10. Motor plantillas** | — | — | docxtpl + python-docx | docxtpl: variables {{nombre}}, tablas, secciones  [docxtpl.readthedocs](https://docxtpl.readthedocs.io) | No maneja macros VBA complex | docxtpl | docxtpl + validación humana | Bajo | Formato perdido en tablas |
| **11. Generación .docx** | Lambda + S3 | Functions + Blob | docxtpl + PDFKit | Generación síncrona para MVP | Asíncrona necesaria para >100 docs | Síncrona (MVP) | Asíncrona + queue (producción) | Bajo | Documento no generado |
| **12. Validación/QC** | Reglas determinísticas + Bedrock | Reglas + OpenAI | Reglas + LLM + human-in-loop | Human-in-the-loop obligatorio  [aimoova](https://www.aimoova.com/post/llm-alucinan-y-riesgos-en-salud-legal) | LLM validation: costoso | Reglas determinísticas + revisión humana | Doble verificación (LLM + humano)  [aimoova](https://www.aimoova.com/post/llm-alucinan-y-riesgos-en-salud-legal) | Medio | Datos inconsistentes contrato |
| **13. Seguridad** | IAM + KMS + CloudTrail | Azure AD + Key Vault + Monitor | Vault + TLS + RBAC | Azure: SOC 2, HIPAA, FedRAMP  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) | AWS: más complejo IAM | IAM + KMS (AWS) o Azure AD + Key Vault | SIEM institucional + DLP | Alto | Brecha datos sensibles |
| **14. Observabilidad** | CloudWatch + X-Ray | Azure Monitor + Application Insights | OpenTelemetry + ELK + Grafana | CloudWatch: nativo AWS, dashboards  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) | ELK: overhead operacional | CloudWatch (AWS) o Azure Monitor | OpenTelemetry + Grafana + SIEM | Medio | Logs sin trazabilidad |
| **15. Despliegue** | AWS EKS (K8s) + serverless | Azure AKS + Functions | Kubernetes自hosted | Serverless: 35% reducción costo  [developers](https://www.developers.dev/tech-talk/serverless-vs-containers-vs-vms-the-definitive-cloud-deployment-decision-framework-for-enterprise-architects.html) | K8s: complejidad alta | Serverless (Lambda/Functions) | Kubernetes + reserved capacity  [developers](https://www.developers.dev/tech-talk/serverless-vs-containers-vs-vms-the-definitive-cloud-deployment-decision-framework-for-enterprise-architects.html) | Alto | Costo serverless alto a escala |
| **16. CI/CD** | GitHub Actions + Terraform + CloudFormation | Azure DevOps + Bicep + Terraform | GitLab CI + Terraform + OpenTofu | Terraform: multi-cloud, IaC estándar | CloudFormation: solo AWS | GitHub Actions + Terraform | Azure DevOps + Bicep (si Azure) | Medio | Despliegue no automatizado |
| **17. Costos** | Textract $90/100k páginas, Bedrock Llama $1/M tokens | Document Intelligence $85/100k páginas, OpenAI $5/M tokens | PaddleOCR gratis, Llama self-hosted $0.72/M tokens | Open source: menor costo OCR/LLM | Self-hosted: overhead operacional | PaddleOCR + Bedrock Llama | Azure Document Intelligence + OpenAI  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) | — | Costo LLM/OCR no escalable |

***

## C. Arquitectura recomendada para MVP

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (MVP)                                                   │
│  - React + TypeScript + Vite                                     │
│  - Componentes: chatbot, visor documental, formularios dinámicos │
│  - Despliegue: AWS Amplify o Azure Static Web Apps               │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ ORQUESTACIÓN (MVP)                                               │
│  - AWS Step Functions (si AWS) o Azure Logic Apps (si Azure)    │
│  - Flujos: consulta SIGED → OCR → NLP → validación → .docx      │
│  - Long-running: usar Temporal.io si flujos > 24h [web:11][web:14] │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ BACKEND SERVICES                                                 │
│  - FastAPI (Python) para OCR/NLP servicios                       │
│  - Lambda/Functions para generación documental                   │
│  - Autenticación: IAM (AWS) o Azure AD                           │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ OCR (MVP)                                                        │
│  - PaddleOCR (open source, gratis, 92.1% accuracy) [web:21][web:27] │
│  - Alternativa: Azure Document Intelligence si precisión crítica [web:1] │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ NLP / EXTRACCIÓN (MVP)                                           │
│  - LangChain + spaCy para extracción basada en reglas            │
│  - LLM: AWS Bedrock Llama 3 70B ($1/M tokens) [web:2][web:5]    │
│  - RAG: PostgreSQL + pgvector para plantillas/bases legales [web:15] │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ GENERACIÓN DOCUMENTAL (MVP)                                      │
│  - docxtpl (python-docx-template) para .docx [web:3][web:6]      │
│  - Validación: reglas determinísticas + revisión humana [web:16] │
│  - Salida: .docx + opcional PDF                                  │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ ALMACENAMIENTO (MVP)                                             │
│  - Documentos temporales: AWS S3 o Azure Blob                   │
│  - Base de datos: SQLite (prototipo) → PostgreSQL (MVP) [web:15] │
│  - Vector store: PostgreSQL + pgvector [web:12][web:15]          │
└─────────────────────────────────────────────────────────────────┘
```

**Características MVP**:
- **Costo bajo**: PaddleOCR gratis, Llama 3 $1/M tokens, SQLite gratis [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)
- **Complejidad baja**: Serverless, sin Kubernetes, PostgreSQL único
- **Tiempo estimado**: 4-6 semanas para MVP Asistente de Bases

***

## D. Arquitectura recomendada para producción

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (Producción)                                            │
│  - React + TypeScript + Next.js (SSR, performance)              │
│  - Componentes: visor documental con zoom, revisión annotada    │
│  - Despliegue: Azure Static Web Apps + CDN                      │
│  - Seguridad: Azure AD + RBAC + MFA                             │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ ORQUESTACIÓN (Producción)                                        │
│  - Temporal.io (Kubernetes) para flujos long-running [web:14][web:17] │
│  - Retry semántico, state recovery, workflows como código       │
│  - Múltiples colas: SQS/SNS (AWS) o Service Bus (Azure)         │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ BACKEND (Producción)                                             │
│  - Microservicios: FastAPI (Python) + NestJS (Node.js) [web:22] │
│  - Despliegue: Kubernetes (EKS/AKS) con auto-scaling [web:33]   │
│  - API Gateway + Load Balancer                                  │
│  - Caching: Redis para prompts frecuentes                       │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ OCR (Producción)                                                 │
│  - Azure AI Document Intelligence (0.9% CER) [web:1][web:10]    │
│  - Custom models para TDR/Bases específicos                     │
│  - Batch processing: 1200 páginas/minuto [web:1]                │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ NLP / EXTRACCIÓN (Producción)                                  │
│  - Azure OpenAI GPT-4o ($5/M input, $15/M output) [web:5]       │
│  - RAG avanzado: Weaviate (hybrid search) [web:15]              │
│  - Validación: LLM + reglas determinísticas + confidence score [web:16] │
│  - Trazabilidad: metadata documento fuente + campo llenado      │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ GENERACIÓN DOCUMENTAL (Producción)                             │
│  - docxtpl + validación multi-paso                              │
│  - Generación asíncrona: queue + worker                         │
│  - Versionado: S3/Blob con versionado + marcas agua             │
│  - PDF: PDFKit o Aspose.Words                                   │
└───────────────┬─────────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────────┐
│ ALMACENAMIENTO (Producción)                                    │
│  - Documentos: AWS S3 (versionado, cifrado KMS) o Azure Blob   │
│  - Base de datos: PostgreSQL con replicación + backup automático │
│  - Vector DB: Weaviate o Milvus (>100M vectores) [web:15][web:18] │
│  - Logs: CloudWatch/Azure Monitor + SIEM institucional          │
└─────────────────────────────────────────────────────────────────┘
```

**Características producción**:
- **Seguridad**: Cifrado en tránsito/reposo, IAM/RBAC, logging, SIEM [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026)
- **Escalabilidad**: Kubernetes + auto-scaling, colas asincrónicas [developers](https://www.developers.dev/tech-talk/serverless-vs-containers-vs-vms-the-definitive-cloud-deployment-decision-framework-for-enterprise-architects.html)
- **Costo**: Azure Document Intelligence $85/100k páginas + OpenAI $5/M tokens [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)
- **Tiempo estimado**: 8-12 semanas adicionales después de MVP

***

## E. Alternativas si no existe API de SIGED

| Escenario | Alternativa | Complejidad | Riesgos |
|-----------|-------------|-------------|---------|
| **SIGED solo web (no API)** | RPA con Playwright/Selenium para descarga automática  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/31729/comparacion-detallada-entre-playwright-y-selenium) | Medio | Fallo si UI cambia, requiere mantenimiento |
| **SIGED con export batch** | Extracción CSV/PDF periódica + procesador batch | Bajo | Latencia alta, no real-time |
| **SIGED con SOAP** | Cliente SOAP + conversión REST interno | Medio | Complexidad SOAP, validación XSD |
| **SIGED sin acceso externo** | File server interno + sincronización manual | Bajo | Proceso manual, no automatizado |
| **SIGED con webhooks** | Webhook + cola asincrónica + procesador | Medio | Configuración webhook, manejo errores |

**Recomendación**: Si no hay API, usar **Playwright** (mejor que Selenium para SPA modernas)  con: [q2bstudio](https://www.q2bstudio.com/nuestro-blog/31729/comparacion-detallada-entre-playwright-y-selenium)
- Auto-waiting nativo
- Contextos múltiples
- Debugging superior
- Extracción de metadatos + documentos

***

## F. Recomendación específica para iniciar con Bases

**Por qué Bases primero**:
1. Flujo más acotado: solo TDR → plantilla → .docx
2. Menos documentos fuente (1 TDR vs 5+ en Contratos)
3. Validación simpler (datos técnicos + administrativos)
4. Aprendizaje OCR/NLP con riesgo menor
5. MVP implementable en 4-6 semanas

**Stack recomendado para Bases (MVP)**:

| Componente | Elección | Justificación |
|------------|----------|---------------|
| **Frontend** | React + TypeScript | Demanda laboral muy alta, ecosistema  [coderhouse](https://www.coderhouse.com/pe/coderlibrary/react-vs-vue-vs-angular-cual-aprender-primero-frontend) |
| **OCR** | PaddleOCR | 92.1% accuracy, gratis, español  [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf) |
| **NLP** | LangChain + spaCy | Extracción reglas + embeddings  [nerds](https://www.nerds.ai/blog/alucinaciones-en-llms-que-son-por-que-ocurren-y-como-mitigarlas-en-produccion) |
| **LLM** | AWS Bedrock Llama 3 70B | $1/M tokens, datos en AWS  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) |
| **RAG** | PostgreSQL + pgvector | <5M vectores, $120-200, simple  [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/) |
| **Plantillas** | docxtpl | Variables {{nombre}}, tablas  [docxtpl.readthedocs](https://docxtpl.readthedocs.io) |
| **Orquestación** | AWS Step Functions | Serverless, integración AWS nativa  [linkedin](https://www.linkedin.com/posts/shajuthomas_distributedsystems-cloudarchitecture-engineeringleadership-activity-7435998889868152832-lrlr) |
| **DB** | PostgreSQL | Universal, pgvector incluido |
| **Storage** | AWS S3 | Versionado, cifrado KMS  [blog.tecnetone](https://blog.tecnetone.com/azure-blob-storage-vs.-amazon-simple-storage-s3) |

**Flujo MVP Bases**:
```
1. Usuario consulta expediente SIGED → Step Functions
2./download TDR → S3 temporal
3. PaddleOCR extracción texto → FastAPI
4. LangChain + spaCy extracción campos TDR (tipo bien/servicio, monto, plazo)
5. RAG pgvector selección plantilla (Bienes/Servicios/Consultoría, normal/abreviado)
6. Usuario ingresa datos administrativos (formulario dinámico React)
7. docxtpl llenado plantilla + validación reglas
8. Revisión humana obligatoria (visor documental con annotations)
9. Generación .docx final → S3 permanente
10. Auditoría: logs CloudWatch + metadata documento fuente
```

***

## G. Recomendación específica para luego escalar a Contratos

**Por qué Contratos después**:
1. 5+ documentos fuente (Bases Integradas, Oferta Económica, Oferta Técnica, Vigencia de Poder, Garantía)
2. Validación compleja: consistencia contrato vs Bases vs propuesta
3. Asociación manual de documentos requerida
4. Revisión normativa/legal obligatoria
5. Riesgo mayor: errores contractuales = impacto legal

**Stack recomendado para Contratos (Producción)**:

| Componente | Elección | Justificación |
|------------|----------|---------------|
| **OCR** | Azure AI Document Intelligence | 0.9% CER, custom models  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) |
| **LLM** | Azure OpenAI GPT-4o | $5/M input, data residency  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) |
| **Validación** | LLM + reglas determinísticas + doble verificación | Evitar alucinaciones  [aimoova](https://www.aimoova.com/post/llm-alucinan-y-riesgos-en-salud-legal) |
| **RAG** | Weaviate | Hybrid search, 1M-50M vectores  [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/) |
| **Orquestación** | Temporal.io | Long-running, state recovery  [scalewithchintan](https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows) |
| **Frontend** | React + Next.js | SSR, visor documental performance |
| **DB** | PostgreSQL + replicación | Trazabilidad completa |
| **Storage** | Azure Blob | Cifrado, versionado  [blog.tecnetone](https://blog.tecnetone.com/azure-blob-storage-vs.-amazon-simple-storage-s3) |

**Flujo producción Contratos**:
```
1. API SIGED consulta expediente → Temporal workflow
2. Download 5+ documentos → Blob temporal
3. Categorización automática (Bases Integradas, Oferta Económica, etc.)
4. Azure Document Intelligence OCR cada documento
5. LLM extracción campos: monto, plazo, pago, entregables, contratista, representante, garantía
6. Validación consistencia:
   - Contrato vs Bases Integradas (monto, plazo, forma pago)
   - Oferta Técnica vs Bases (entregables, especificaciones)
   - Vigencia de Poder (fecha, representante legal)
   - Garantía (tipo, monto, vigencia)
7. Confidence score + reglas determinísticas
8. Revisión humana obligatoria (doble verificación) [web:16]
9. Trazabilidad: metadata documento fuente → campo contrato
10. Generación .docx + PDF → Blob permanente
11. Auditoría: SIEM + logs + metadata completa
```

**Controls específicos Contratos**:
- **Monto**: validar coincidencia 100% entre contrato, Bases, Oferta Económica
- **Plazo**: validar consistencia Bases vs Contrato
- **Forma de pago**: validar etapas, porcentajes, condiciones
- **Entregables**: validar Oferta Técnica vs Contrato
- **Contratista**: validar RUC, nombre, representante legal
- **Garantía**: validar tipo (carta, seguro), monto (% contrato), vigencia

***

## H. Riesgos técnicos y funcionales

| Riesgo | Tipo | Impacto | Mitigación |
|--------|------|---------|------------|
| **Alucinaciones LLM** | Técnico | Datos sin fuente | RAG + rules + human-in-loop  [nerds](https://www.nerds.ai/blog/alucinaciones-en-llms-que-son-por-que-ocurren-y-como-mitigarlas-en-produccion) |
| **OCR falla escaneados** | Técnico | Extracción incorrecta | Azure Document Intelligence + custom models  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) |
| **Sin API SIGED** | Funcional | Proceso manual | Playwright RPA + batch export  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/31729/comparacion-detallada-entre-playwright-y-selenium) |
| **Costo LLM no predecible** | Técnico | Budget excedido | Cache prompts + Llama 3 barato + monitoring  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) |
| **Datos sensibles external** | Seguridad | Brecha compliance | Azure OpenAI/Bedrock (datos en tenant)  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) |
| **Formato .docx perdido** | Técnico | Documento no válido | docxtpl + validación formato + revisión humana  [docxtpl.readthedocs](https://docxtpl.readthedocs.io) |
| **Validación inconsistente** | Funcional | Contrato error legal | Doble verificación (LLM + humano) + reglas determinísticas  [aimoova](https://www.aimoova.com/post/llm-alucinan-y-riesgos-en-salud-legal) |
| **Flujo long-running falla** | Técnico | Proceso intermedio | Temporal.io retry + state recovery  [scalewithchintan](https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows) |
| **Vector DB sin actualización** | Técnico | RAG knowledge viejo | Weaviate versionado + actualización periódica  [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/) |
| **K8s overhead operacional** | Técnico | Complejidad alta | Serverless MVP → Kubernetes solo producción  [developers](https://www.developers.dev/tech-talk/serverless-vs-containers-vs-vms-the-definitive-cloud-deployment-decision-framework-for-enterprise-architects.html) |

***

## I. Preguntas clave al equipo

### Al equipo funcional:
1. ¿Qué TDR existen actualmente y cuántas páginas promedio tiene cada uno?
2. ¿Qué plantillas de Bases ya están validadas (Bienes/Servicios/Consultoría, normal/abreviado)?
3. ¿Qué campos específicos se extraen del TDR (monto, plazo, tipo bien/servicio, especificaciones)?
4. ¿Qué datos administrativos ingresa el usuario manualmente?
5. ¿Qué documentos fuente existen para Contratos y cómo se categorizan?
6. ¿Qué validaciones normativas/legal son obligatorias antes de firmar contrato?
7. ¿Quién hace la revisión humana obligatoria y cuántos niveles de aprobación existen?

### Al equipo de infraestructura:
1. ¿La entidad ya tiene infraestructura AWS, Azure o on-premise?
2. ¿Existe restricción para enviar documentos a cloud externo (data sovereignty)?
3. ¿Qué capacidad de servidores on-premise existe si se requiere híbrido?
4. ¿Qué sistema de backup/replicación existe para PostgreSQL?
5. ¿Hay Kubernetes existente o se requiere nuevo despliegue?
6. ¿Qué groupId/costo mensual hay para cloud (AWS/Azure)?

### Al equipo de seguridad:
1. ¿Qué certificaciones de compliance son obligatorias (SOC 2, HIPAA, FedRAMP, GDPR)? [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026)
2. ¿Qué nivel de cifrado en tránsito/reposo se requiere (TLS 1.3, AES-256)?
3. ¿Qué IAM/RBAC estándar existe (Azure AD, AWS IAM)?
4. ¿Qué SIEM institucional existe para auditoría?
5. ¿Qué políticas de retención/documentación existen (cuánto tiempo retener documentos)?
6. ¿Qué DLP (Data Loss Prevention) está implementado?

### Al equipo de SIGED:
1. ¿SIGED tiene API REST/SOAP disponible? ¿Qué endpoints existen?
2. ¿Si no hay API, existe export batch (CSV/PDF) periódica?
3. ¿Qué autenticación usa SIGED (OAuth2, SAML, basic auth)?
4. ¿Qué webhooks existen para notificación de nuevos expedientes?
5. ¿Qué metadatos se pueden extraer del expediente (número, tipo, fecha, estado)?
6. ¿Hay restricción de velocidad (rate limit) para descarga de documentos?
7. ¿Existe documentación de API o ejemplo de integración previa?

***

## J. Conclusión final con propuesta priorizada

### Propuesta priorizada (roadmap 6 meses):

| Fase | Duración | Objetivo | Stack | Costo estimado |
|------|----------|----------|-------|----------------|
| **Fase 1: MVP Bases** | 4-6 semanas | Asistente Bases funcional | React + PaddleOCR + Bedrock Llama + pgvector + docxtpl + Step Functions | $1,500-2,500 (OCR gratis, LLM $100-200/mes)  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) |
| **Fase 2: OCR/NLP fortalecido** | 3-4 semanas | Precisión OCR + extracción robusta | Azure Document Intelligence + LangChain + spaCy custom | $3,000-5,000 (Document Intelligence $85/100k páginas)  [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025) |
| **Fase 3: Asistente Contratos** | 6-8 semanas | Contratos con validación compleja | Temporal.io + Azure OpenAI GPT-4o + Weaviate + doble verificación | $8,000-12,000 (OpenAI $500-800/mes)  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) |
| **Fase 4: Producción** | 4-6 semanas | Escalabilidad + seguridad + auditoría | Kubernetes + SIEM + DLP + backup replicación | $15,000-25,000 (infra + licencias) |

### Decisión cloud vs on-premise:

| Escenario | Recomendación | Justificación |
|-----------|---------------|---------------|
| **Entidad ya tiene Azure (Office 365, Azure AD)** | **Azure OpenAI + Document Intelligence** | Integración nativa, data residency controlada, SOC 2/HIPAA/FedRAMP  [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026) |
| **Entidad quiere flexibilidad modelos** | **AWS Bedrock** | Multi-modelo (Claude, Llama, Titan), datos en AWS account, $1/M tokens Llama  [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje) |
| **Restricción cloud externa obligatoria** | **PaddleOCR + Llama self-hosted + MinIO** | Open source total, on-premise, costo bajo pero overhead operacional  [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf) |
| **Híbrido (parte cloud, parte on-premise)** | **Azure/AWS + MinIO local** | Documentos sensibles on-premise, LLM/OCR en cloud  [rootstack](https://rootstack.com/es/blog/aws-s3-vs-azure-blob-diferencias) |

### Recomendación final:

**Para MVP (4-6 semanas, costo bajo)**:
- **Frontend**: React + TypeScript
- **OCR**: PaddleOCR (gratis, 92.1% accuracy) [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf)
- **LLM**: AWS Bedrock Llama 3 70B ($1/M tokens) [q2bstudio](https://www.q2bstudio.com/nuestro-blog/203852/costo-real-inteligencia-artificial-plataformas-aws-bedrock-openai-autohospedaje)
- **RAG**: PostgreSQL + pgvector ($120-200) [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/)
- **Plantillas**: docxtpl [docxtpl.readthedocs](https://docxtpl.readthedocs.io)
- **Orquestación**: AWS Step Functions [linkedin](https://www.linkedin.com/posts/shajuthomas_distributedsystems-cloudarchitecture-engineeringleadership-activity-7435998889868152832-lrlr)
- **Storage**: AWS S3 [blog.tecnetone](https://blog.tecnetone.com/azure-blob-storage-vs.-amazon-simple-storage-s3)

**Para producción (seguridad + escalabilidad)**:
- **OCR**: Azure AI Document Intelligence (0.9% CER) [datascientist](https://datascientist.fr/blog/aws-textract-vs-azure-document-2025)
- **LLM**: Azure OpenAI GPT-4o (data residency) [reintech](https://reintech.io/blog/openai-api-vs-azure-openai-vs-aws-bedrock-enterprise-llm-comparison-2026)
- **RAG**: Weaviate (hybrid search) [perlod](https://perlod.com/tutorials/best-vector-database-for-rag/)
- **Orquestación**: Temporal.io (long-running) [scalewithchintan](https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows)
- **Infra**: Kubernetes +SIEM + DLP

**Priorizar Bases primero** porque es flujo acotado, riesgo menor, MVP rápido. **Contratos después** porque es complejo, requiere validación legal, mayor riesgo.

**Evitar**: OpenAI API directo (datos retienen 30 días), Tesseract (75.8% accuracy), serverless en producción alta escala (costo mayor). [ijrpr](https://ijrpr.com/uploads/V6ISSUE10/IJRPR53627.pdf)