# **Informe de Investigación y Propuesta de Arquitectura Tecnológica para Asistentes de Inteligencia Artificial en Contratación Pública**

## **A. Resumen ejecutivo**

El proceso de modernización de la gestión pública en el Estado peruano exige la incorporación de tecnologías emergentes que optimicen la eficiencia administrativa sin comprometer la seguridad, la confidencialidad ni la integridad de la información estatal.1 En este contexto, la implementación de asistentes de Inteligencia Artificial (IA) para la generación automatizada de Bases Estándar y la formalización de Contratos representa un cambio de paradigma en la gestión de adquisiciones públicas.4 El diseño de una arquitectura tecnológica robusta desde cero para estos asistentes requiere un balance preciso entre la agilidad del desarrollo y el cumplimiento de un marco regulatorio estricto. Dicho marco está delimitado por la Ley de Gobierno Digital (Decreto Legislativo N° 1412\) 6, el Modelo de Gestión Documental de la Secretaría de Gobierno y Transformación Digital (SEGDI) 6, y las obligaciones imperativas de la Ley de Protección de Datos Personales (Ley N° 29733\) y su reglamento actualizado mediante el Decreto Supremo N° 016-2024-JUS.8  
La presente investigación aborda el análisis multidimensional de alternativas tecnológicas para estructurar dos asistentes con complejidades funcionales diferenciadas. El Asistente IA para la Generación de Bases Estándar responde a un flujo de trabajo lineal, acotado y parametrizado a partir de un Término de Referencia (TDR) y plantillas normadas por el Organismo Supervisor de las Contrataciones del Estado (OSCE).4 Por su parte, el Asistente IA para la Generación de Contratos asume un escenario de alta complejidad conceptual y jurídica. Este último exige el análisis, categorización y validación cruzada de múltiples documentos de origen diverso, tales como Bases Integradas, Ofertas Económicas y Técnicas, Vigencias de Poder y Cartas Fianza.5 Para resolver ambos escenarios, se analiza un espectro de soluciones que abarca ofertas de nube pública en Amazon Web Services (AWS) y Microsoft Azure, así como infraestructuras autohospedadas (*on-premise*) basadas en software de código abierto (*open source*). El objetivo es asegurar que la entidad pública mantenga el control soberano sobre sus datos confidenciales 10, mitigue el riesgo de alucinaciones mediante esquemas híbridos de validación probabilística-determinista 12, y garantice la indispensable supervisión humana en cada fase del proceso.

## **B. Tablas comparativas por componente**

Para facilitar una evaluación estructurada de las tecnologías disponibles, la arquitectura se ha dividido en cinco capas lógicas. Las alternativas de nube de AWS y Azure se contrastan con soluciones abiertas desplegables localmente, analizando sus ventajas, desventajas, idoneidad para el Producto Mínimo Viable (MVP) y escalabilidad en producción.

### **1\. Capa de interfaz de usuario y orquestación de flujos**

| Componente | Alternativa AWS | Alternativa Azure | Alternativa Open Source / On-Premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Nivel de Complejidad | Riesgos Principales |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **1\. Frontend / Interfaz de usuario** | AWS Amplify (Hosting) 14 | Azure App Service 15 | React / Next.js autohospedado en Nginx 16 | **React/Next.js:** Flexibilidad extrema para formularios dinámicos, visor de PDF embebido (PDF.js) y marcado de texto. Cero costo de licenciamiento. | Requiere mayor esfuerzo de desarrollo de interfaz de usuario desde cero en comparación con herramientas *low-code*. | Streamlit integrado en Python para interfaz rápida de prototipo de chat y formularios. | Next.js en contenedores para renderizado híbrido y optimización de rendimiento en navegadores antiguos.16 | Medio | Incompatibilidad con navegadores institucionales legacy del Estado peruano.16 |
| **2\. Backend / Orquestador** | AWS Step Functions \+ AWS Lambda 17 | Azure Durable Functions 19 | Temporal.io con FastAPI (Python) 18 | **Temporal.io:** Orquestación basada en código-primero.20 Maneja de forma nativa flujos asíncronos persistentes de larga duración (esperas de firmas y aprobaciones legales).20 | **Step Functions:** Costo acumulativo elevado por transiciones de estado a gran escala.20 Dificultad de migración multicloud.18 | FastAPI directo con llamadas asíncronas básicas en Python. | Temporal.io montado sobre Kubernetes local o en la nube.18 | Alto | Pérdida de estado en procesos de validación de contratos que duren varios días si se usa un backend sin persistencia activa.20 |

### **2\. Capa de datos, almacenamiento e integración documental**

| Componente | Alternativa AWS | Alternativa Azure | Alternativa Open Source / On-Premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Nivel de Complejidad | Riesgos Principales |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **3\. Integración con SIGED** | Amazon API Gateway \+ AWS Lambda 17 | Azure API Management \+ Logic Apps | FastAPI con Apache Camel / Integration Engine | **REST/SOAP API:** Método estándar de comunicación entre sistemas. Permite consumo estructurado en tiempo real de metadatos y documentos.1 | La viabilidad técnica depende críticamente de la existencia de APIs abiertas en el SIGED institucional.1 | Simulación (*Mocking*) del SIGED mediante lectura de expedientes locales en formato JSON. | Microservicio integrador con colas RabbitMQ para reintentos asíncronos y desacoplamiento físico del SIGED.21 | Alto | Indisponibilidad o inestabilidad del SIGED legacy que paralice el flujo de generación documental.22 |
| **4\. Almacenamiento documental** | Amazon S3 (Object Lock y KMS) 14 | Azure Blob Storage (Immutable Storage) | MinIO Enterprise (S3 compatible) 10 | **MinIO:** Desplegable localmente dentro del centro de datos de la entidad pública, garantizando soberanía de datos y compatibilidad con APIs de S3.10 | El almacenamiento físico local requiere gestión de respaldos y mantenimiento de hardware de red. | MinIO en contenedor Docker individual de almacenamiento local rápido. | Clúster de MinIO con replicación activa, cifrado en reposo AES-256 e inmutabilidad activada contra ransomware. | Bajo | Acceso no autorizado a documentos técnicos y económicos confidenciales por políticas de baldes (*bucket policies*) erróneas. |
| **5\. Base de datos / Persistencia** | Amazon RDS PostgreSQL / DynamoDB 10 | Azure Database for PostgreSQL | PostgreSQL con extensión pgvector 10 | **PostgreSQL:** Permite almacenar de forma unificada datos relacionales de auditoría, expedientes y vectores de embeddings en una sola base.10 | Requiere administración manual del rendimiento de índices vectoriales a escala empresarial. | SQLite local para persistencia rápida en fase de prototipo. | PostgreSQL con réplica de alta disponibilidad (Patroni) y la extensión vectorial activa.10 | Medio | Fuga de logs de auditoría o alteración de registros históricos de transacciones contractuales. |

### **3\. Capa de procesamiento cognitivo (OCR, NLP y Modelos de Lenguaje)**

| Componente | Alternativa AWS | Alternativa Azure | Alternativa Open Source / On-Premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Nivel de Complejidad | Riesgos Principales |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **6\. OCR (Procesamiento)** | AWS Textract (Queries & Tables) 14 | Azure AI Document Intelligence 24 | PaddleOCR / Tesseract OCR | **Azure AI Doc Intelligence:** Extraordinaria precisión en el análisis de tablas y layouts complejos en idioma español, ideal para documentos administrativos públicos.23 | **Open Source:** Precisión notablemente menor ante documentos PDF escaneados con baja resolución o firmas manuscritas. | Azure AI Document Intelligence en modalidad SaaS Cloud para desarrollo ágil.24 | Contenedores de Azure AI Document Intelligence desplegados en local en el clúster Kubernetes (AKS Edge / OpenShift).24 | Medio | Extracción errónea de montos de ofertas económicas debido a mala resolución del PDF escaneado.5 |
| **7\. NLP / Extracción de información** | Amazon Comprehend \+ AWS Bedrock 23 | Azure OpenAI \+ Cognitive Services 10 | SpaCy (modelos en español) \+ LLM local (vLLM) 11 | **Híbrido (SpaCy \+ LLM):** Combina el procesamiento semántico flexible de modelos de lenguaje con la velocidad de clasificadores deterministas locales.11 | **Cloud:** Exposición de datos a flujos transfronterizos no autorizados bajo normativas peruanas de privacidad.9 | LangChain con esquemas estructurados de Pydantic utilizando APIs directas de bajo costo. | Pipeline híbrido local: Modelos SpaCy refinados para clasificación y vLLM local para extracción semántica.11 | Alto | Alucinaciones conceptuales de la IA al clasificar términos de penalidades complejas.12 |
| **8\. Motor de IA generativa / LLM** | AWS Bedrock (Claude / Llama) | Azure OpenAI (GPT-4o) 10 | Modelos locales (Llama 3.1 70B / Mistral / Qwen) con vLLM 10 | **vLLM local:** Máxima soberanía de datos, ausencia de costos transaccionales de tokens en la nube, optimización extrema mediante PagedAttention.25 | Requiere inversión inicial alta de capital (CapEx) para adquisición de tarjetas de video GPU empresariales.10 | Ollama local ejecutando Llama 3.1 8B cuantizado en formato GGUF.25 | vLLM desplegado en alta disponibilidad con Llama 3.1 70B o Mistral Large local.10 | Alto | Costo inmanejable de suscripción SaaS o latencias de red lentas que afecten la experiencia del funcionario.11 |
| **9\. RAG / Base de conocimiento** | Amazon OpenSearch / Amazon Kendra 18 | Azure AI Search 24 | Qdrant / PostgreSQL (pgvector) 10 | **pgvector / Qdrant:** Búsqueda híbrida de alta precisión (semántica más palabra clave), fácil actualización de conocimiento sin necesidad de reentrenamiento.10 | **Azure Search:** Costo fijo mensual restrictivo para presupuestos de TI del sector público. | Búsqueda vectorial directa implementada en PostgreSQL local con pgvector.10 | Clúster dedicado de Qdrant integrado con Elasticsearch local para búsqueda híbrida avanzada a gran escala.10 | Medio | Respuestas del chatbot fundamentadas en normativas de contrataciones que ya han sido derogadas.4 |

### **4\. Capa de generación y validación de documentos**

| Componente | Alternativa AWS | Alternativa Azure | Alternativa Open Source / On-Premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Nivel de Complejidad | Riesgos Principales |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **10\. Motor de plantillas documentales** | Generación binaria en AWS Lambda 17 | Orquestación mediante Durable Functions 19 | docxtpl (Python) \+ Jinja2 29 | **docxtpl:** Permite el uso directo de plantillas reales de Microsoft Word (.docx) diseñadas por abogados, sin necesidad de codificar layouts complejos.29 | Fragilidad ante la edición incorrecta de las etiquetas Jinja por usuarios no técnicos dentro del documento base.31 | docxtpl integrado en memoria en la API de FastAPI procesando plantillas básicas.30 | Microservicio dedicado con docxtpl para mapeo estructurado y Aspose.Words para formateo complejo de tablas.30 | Medio | Corrupción del archivo XML interno del archivo .docx debido a etiquetas Jinja2 mal formadas en Word.29 |
| **11\. Generación y descarga de documentos** | S3 Pre-signed URLs con expiración temporal 14 | Azure SAS (Shared Access Signatures) | FastAPI sirviendo flujos binarios asíncronos con MinIO | **Asíncrona:** Descarga robusta que no bloquea la API web al procesar archivos de contratos voluminosos. | Requiere manejo de estados intermedios y colas de tareas para notificar al usuario cuando el archivo esté listo. | Generación síncrona en memoria entregada directamente como flujo binario HTTP. | Generación asíncrona mediante trabajadores Celery o Temporal, almacenamiento en MinIO y descarga vía enlaces temporales cifrados. | Medio | Fuga de contratos finales por enlaces de descarga expuestos permanentemente a internet pública. |
| **12\. Validación y control de calidad** | Amazon Bedrock Guardrails | Azure AI Content Safety | Pipeline híbrido de validación determinista \+ probabilista 12 | **Validación Híbrida:** Garantiza precisión absoluta mediante validadores aritméticos de código para montos, y validación semántica del LLM para cláusulas.12 | Alta complejidad para modelar la totalidad de restricciones contractuales y reglas lógicas del negocio.13 | Extracción con LLM estructurada con Pydantic y validación en backend con expresiones regulares (Regex) para fechas y montos.13 | Implementación de Predictika LVE (Logic Validation Engine) o pipeline personalizado de validación de tres niveles (sintáctico, aritmético, conceptual).33 | Alto | Validación fallida que pase por alto discrepancias críticas en los plazos de entrega entre la oferta técnica y el contrato.35 |

### **5\. Capa de infraestructura, seguridad y operaciones**

| Componente | Alternativa AWS | Alternativa Azure | Alternativa Open Source / On-Premise | Ventajas | Desventajas | Recomendación MVP | Recomendación Producción | Nivel de Complejidad | Riesgos Principales |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **13\. Seguridad, privacidad y cumplimiento** | AWS IAM, KMS, Macie 17 | Azure RBAC, Key Vault, Purview 14 | Keycloak (OIDC) \+ HashiCorp Vault \+ SSL local | **Enfoque Local:** Total alineación con la Ley de Protección de Datos Personales N° 29733, evitando transferencia transfronteriza.8 | Exige que el equipo de TI del Estado asuma de forma exclusiva la responsabilidad sobre la seguridad física y de red. | Autenticación basada en JSON Web Tokens (JWT) y cifrado AES-256 a nivel de base de datos local. | Integración OIDC con el Active Directory corporativo, HashiCorp Vault para secretos, firewalls locales y encripción mediante hardware TPM.11 | Alto | Vulneración de la base de datos que exponga propuestas técnicas o identidades protegidas de postores.8 |
| **14\. Observabilidad y auditoría** | Amazon CloudWatch \+ AWS CloudTrail 17 | Azure Monitor \+ Log Analytics 15 | OpenTelemetry \+ Clúster Grafana \+ Prometheus \+ Loki | **OpenTelemetry:** Estándar independiente que evita dependencia del proveedor y unifica la trazabilidad técnica con la funcional de la IA.20 | Requiere aprovisionamiento de almacenamiento significativo para retener históricos de logs estructurados. | Logs integrados estándar en formato JSON en el backend FastAPI y captura básica de eventos en PostgreSQL. | Pipeline centralizado con OpenTelemetry y Loki para auditoría de acciones funcionales y trazabilidad de cada llamada al LLM. | Medio | Manipulación malintencionada de los logs de auditoría para ocultar modificaciones manuales sobre contratos o bases. |
| **15\. Despliegue e infraestructura** | AWS ECS Fargate / AWS EKS 18 | Azure Kubernetes Service (AKS) 24 | Kubernetes local (Rancher / MicroK8s) | **Kubernetes local:** Portabilidad absoluta, escalabilidad elástica de contenedores de inferencia y aislamiento de red nativo.11 | Requiere un equipo con experiencia avanzada en operaciones (*Ops*) de clústeres Kubernetes en servidores físicos. | Despliegue con Docker Compose en una máquina virtual robusta provista de GPUs locales de grado de desarrollo. | Clúster de Kubernetes en topología de nube híbrida, aislando físicamente el plano de inferencia de IA en una subred privada local.2 | Alto | Caídas de rendimiento del servicio de inferencia de IA ante picos masivos de usuarios durante cierres de convocatorias públicas. |
| **16\. CI/CD y DevSecOps** | GitHub Actions \+ AWS CodePipeline | Azure DevOps (Pipelines) 15 | GitLab CI/CD \+ OpenTofu (Terraform Open Source) | **GitLab CI/CD local:** Entorno de integración y entrega continuas autoalojable, con herramientas de análisis de vulnerabilidades integradas. | Curva de aprendizaje técnica para automatizar el aprovisionamiento de recursos locales con herramientas IaC. | GitHub Actions con despliegue semi-automatizado a través de túneles SSH seguros. | GitLab CI/CD integrado con OpenTofu para despliegue inmutable sobre Kubernetes, realizando escaneos SAST y DAST automáticos. | Medio | Introducción de vulnerabilidades críticas de seguridad o secretos expuestos en el código fuente de los asistentes de IA. |
| **17\. Costos y licenciamiento** | Pago por uso (SaaS) elástico con riesgo de variación cambiaria 20 | Pago por uso (SaaS) elástico con riesgo de variación cambiaria 20 | Licenciamiento gratuito de código abierto, inversión en hardware físico (CapEx) | **Software Libre:** Costo operativo directo predecible y recurrente a largo plazo de cero dólares en licencias de IA.10 | Mayor inversión inicial de capital (CapEx) para adquirir infraestructura de servidores físicos de cómputo GPU. | Consumo de recursos de nube pública bajo cuotas controladas en modalidad de pago por uso para prototipado. | Modelo híbrido: Inferencia y OCR local en GPUs físicas para el tráfico base; escalado elástico a nube con encripción solo bajo picos de carga.10 | Alto | Suspensión inesperada del servicio web por agotamiento de créditos presupuestales para pago de servicios de nube extranjeros. |

## **C. Arquitectura recomendada para MVP**

La arquitectura diseñada para el Producto Mínimo Viable (MVP) se enfoca en validar con rapidez las hipótesis técnicas de extracción documental y autollenado de variables del Asistente de Bases Estándar, minimizando la fricción operativa y los costes iniciales de infraestructura.4

### **Esquema arquitectónico conceptual (MVP)**

       (Streamlit / React simple en máquina virtual)  
                  │  
                  ▼ (Llamadas REST seguras vía HTTPS con Tokens JWT)  
       (FastAPI \- Python asíncrono)  
                  │  
        ┌─────────┴────────────────────────┐  
        ▼                                  ▼  
              
(Mock SIGED \- Lectura JSON)        (LangChain Pipeline con Pydantic)  
        │                                  │  
        ▼                                  ▼  
            (Azure AI Doc Intelligence Cloud SaaS)  
(Contenedor Docker \- Temp PDFs)    (Extracción estructurada de tablas del TDR)  
        │                                  │  
        └─────────────────┬────────────────┘  
                          ▼  
             (Ollama \- Llama 3.1 8B cuantizado en GPU L4)  
                          │  
                          ▼  
             (Librería docxtpl aplicando Jinja2)  
                          │  
                          ▼  
             (Base de datos PostgreSQL básica)

En la capa de presentación de este MVP se implementa una interfaz web interactiva ágil mediante el framework Streamlit, que se conecta con un backend robusto basado en FastAPI (Python). Al tratarse de un entorno controlado para validación, la comunicación con el Sistema de Gestión Electrónica de Documentos (SIGED) se realiza a través de un simulador (*Mock*) que emula el comportamiento de descarga de archivos leyendo estructuras de carpetas locales y devolviendo metadatos estandarizados en formato JSON, evitando así bloqueos por falta de conectividad con la red del SIGED.1 Cuando un funcionario carga un TDR de prueba en la interfaz, el backend FastAPI almacena temporalmente el binario en un contenedor local de MinIO que emula una API compatible con Amazon S3.10  
El procesamiento cognitivo del TDR combina servicios en nube de bajo costo con inferencia local de alta privacidad. El archivo se envía inicialmente a la API en la nube de Azure AI Document Intelligence para su análisis a través del modelo de Layout, el cual extrae con un altísimo nivel de precisión la estructura de las tablas del TDR (especificaciones técnicas, entregables, penalidades y plazos).24 Este JSON de salida de Azure se procesa localmente en el backend utilizando LangChain y un esquema de validación estricto con Pydantic, y es enviado a una instancia de Ollama alojada en una máquina de desarrollo de la entidad equipada con una tarjeta gráfica NVIDIA L4 (24GB de VRAM).10 Ollama ejecuta de manera completamente desconectada un modelo Llama 3.1 8B cuantizado en formato GGUF, lo cual garantiza que la interpretación del contenido se realice con total privacidad.11 Una vez que el modelo de lenguaje devuelve las variables estructuradas, la aplicación FastAPI utiliza la librería docxtpl para abrir en memoria la plantilla de Bases seleccionada en formato .docx y reemplazar de forma directa las etiquetas Jinja2 con los datos extraídos.29 El documento resultante se almacena en MinIO y se entrega al usuario para su descarga, registrando la traza de la transacción en una base de datos PostgreSQL local.

## **D. Arquitectura recomendada para producción**

Para el despliegue a gran escala de la plataforma, la arquitectura transiciona hacia un enfoque empresarial de alta disponibilidad, tolerancia a fallos, auditoría completa y total soberanía de los datos, diseñado para operar de forma híbrida o completamente local dentro de la red del Estado peruano.2

### **Esquema arquitectónico empresarial (Producción)**

                             
                                          │  
                                          ▼ (HTTPS / TLS 1.3 / Certificados Digitales)  
                             
                                          │  
                  ┌───────────────────────┴───────────────────────┐  
                  ▼                                               ▼  
                                
       (FastAPI en Pods Kubernetes)                  (FastAPI en Pods Kubernetes)  
                  │                                               │  
                  └───────────────────────┬───────────────────────┘  
                                          ▼  
                       
                                          │  
                                          ▼  
                       
                                          │  
          ┌───────────────────────┼───────────────────────┬───────────────────────┐  
          ▼                       ▼                       ▼                       ▼  
                 
(Contenedores locales     (vLLM Cluster local     (Clúster MinIO local     (PostgreSQL HA con Patroni  
Azure DocIntel en K8s)    Llama 3.1 70B en GPUs)   con Object Lock e IAM)   y pgvector para RAG local)  
                                      
          │                       │                       │                       │  
          └───────────────────────┼───────────────────────┴───────────────────────┘  
                                  ▼  
                      
                   (Microservicio dedicado con \`docxtpl\`  
                    y biblioteca empresarial Aspose.Words)  
                     \[29, 32\]  
                                  │  
                                  ▼  
                     (Integración de firmas digitales oficiales) 

La arquitectura productiva se despliega sobre un clúster de Kubernetes autohospedado en servidores físicos locales de la entidad pública para cumplir estrictamente con los lineamientos del Sistema Nacional de Transformación Digital y la seguridad nacional.2 El tráfico entrante se gestiona a través de la puerta de enlace Kong API Gateway, que valida la identidad de los funcionarios públicos mediante el Active Directory institucional y tokens OAuth2/OIDC. Los microservicios de generación de Bases y de Contratos se ejecutan en pods independientes de Kubernetes de manera aislada, comunicándose de forma asíncrona mediante el broker de mensajería RabbitMQ para evitar congestiones y pérdidas de peticiones ante picos de carga de trabajo.21  
La orquestación de los flujos de negocio complejos —especialmente el de contratos, que requiere validaciones de consistencia de múltiples documentos y aprobaciones humanas obligatorias— se confía a un clúster de **Temporal.io**.20 Temporal.io realiza el seguimiento del estado de cada expediente de forma duradera en una base de datos relacional PostgreSQL con alta disponibilidad.20 Si un proceso se detiene en espera de que un abogado de asesoría jurídica revise y apruebe las diferencias de un contrato, el workflow se pausa de manera persistente sin consumir recursos del servidor y se reanuda de manera exacta cuando se recibe el evento del usuario, tolerando caídas completas del clúster físico de Kubernetes sin perder el progreso del flujo de contratación.20  
Para garantizar que ningún documento administrativo sensible sea enviado fuera de los límites de la red institucional (evitando la transferencia transfronteriza no autorizada prohibida por la Ley N° 29733\) 8, todos los componentes cognitivos se ejecutan de manera local (*On-Premise*) en un clúster de servidores dedicados dotados de aceleradoras de hardware GPU (por ejemplo, 4x NVIDIA A100 de 80GB VRAM) 10:

* **OCR Enterprise Local:** Se despliegan contenedores locales de **Azure AI Document Intelligence** bajo Kubernetes utilizando su soporte oficial de imágenes autoalojadas (*Container Support*).24 El tráfico de OCR se procesa de forma ultrarrápida dentro del centro de datos local utilizando los modelos preentrenados de lectura de tablas, listados y estructuras de la suite cognitiva de Azure sin conectividad externa obligatoria.15  
* **Inferencia de Alto Rendimiento:** Se despliega un clúster de **vLLM** para servir modelos de lenguaje avanzados como Llama 3.1 70B o Mistral Large en español.10 vLLM optimiza el hardware local mediante la asignación dinámica de memoria de **PagedAttention**, lo cual permite procesar hasta un 320% más de peticiones de funcionarios concurrentes en comparación con servidores de inferencia básicos, eliminando la latencia del procesamiento semántico de contratos masivos de más de 100 páginas.11  
* **Almacenamiento y Persistencia Híbrida:** Los archivos se guardan con cifrado inmutable AES-256 en un clúster local de MinIO Enterprise con replicación distribuida.10 La base de datos vectorial para el RAG de bases legales y directivas del OSCE se consolida en el mismo motor de base de datos relacional PostgreSQL de alta disponibilidad mediante la extensión de código abierto pgvector, lo que facilita la sincronización de transacciones e históricos de auditoría.4  
* **Generación Avanzada y Firma:** El motor de documentos utiliza un microservicio dedicado que combina docxtpl para la lógica dinámica de reemplazo de variables 29 con la biblioteca comercial **Aspose.Words para Python**.32 Aspose.Words realiza el renderizado exacto de tablas complejas de la oferta ganadora, recalcula tablas de contenido automáticamente, formatea de manera estricta los párrafos y genera una salida en formato Word editable y una versión no modificable en formato estándar PDF/A.32 El documento resultante se envía a la API del firmador digital del Estado peruano (Firma Perú) para capturar la firma criptográfica válida del funcionario antes de marcar el contrato como formalizado.1

## **E. Alternativas si no existe API de SIGED**

Frente a la realidad tecnológica de múltiples entidades del sector público donde el Sistema de Gestión Electrónica de Documentos (SIGED) es un desarrollo legacy cerrado que carece de APIs de integración REST, SOAP o webhooks disponibles para consumo 1, el arquitecto de soluciones cloud debe plantear patrones alternativos de integración no invasivos que eviten la parálisis del proyecto.

### **Robotización de Procesos con Playwright o Selenium (RPA)**

La primera alternativa viable consiste en implementar un agente de automatización robótica de procesos (RPA) de código abierto utilizando la herramienta de automatización de navegadores Playwright o Selenium. Este agente de software se ejecuta de manera programada o disparada por eventos dentro de un contenedor en Kubernetes:

* El agente de RPA inicia sesión de manera segura en la interfaz web de usuario del SIGED utilizando credenciales institucionales dedicadas y cifradas en HashiCorp Vault.  
* Ante una nueva solicitud de expediente, el robot emula la navegación del usuario humano, ingresa al buscador del trámite, digita el número de expediente administrativo y extrae la estructura jerárquica de los documentos adjuntos.39  
* El robot descarga de forma automatizada los archivos binarios de interés (TDR, propuestas, bases) al repositorio inmutable de MinIO, extrae los metadatos expuestos en la interfaz HTML del portal de SIGED y notifica al microservicio de los asistentes de IA mediante una llamada API que la descarga e ingesta de documentos del expediente ha concluido de forma exitosa.

### **Replicación a Nivel de Base de Datos y Sistema de Archivos NFS/NAS**

Si la entidad pública tiene el control directo sobre la infraestructura física de base de datos del SIGED (frecuentemente motores como Oracle Database o Microsoft SQL Server montados localmente), se puede acordar una integración directa a nivel de base de datos y sistemas de almacenamiento compartidos:

* Se configura una **Vista de Base de Datos de Solo Lectura (Read-Only Replica)** que exponga únicamente las tablas relevantes de trámite documentario que contienen la metadata de los expedientes, tipos de documento, estados de los flujos y nombres físicos de los archivos binarios asociados.  
* El microservicio de integración de los asistentes de IA ejecuta consultas periódicas (*Polling*) sobre esta vista para identificar expedientes que hayan cambiado de estado (por ejemplo, transicionar a "Otorgamiento de Buena Pro Consentido" o "Pendiente de Elaboración de Bases").  
* Los archivos PDF y Word reales, que el servidor del SIGED deposita físicamente en carpetas compartidas de red mediante protocolos NAS, NFS o SMB, son leídos de forma directa por el asistente de IA utilizando montajes de volumen de almacenamiento de red compartidos en modo de solo lectura, procesándolos de manera directa e instantánea.

### **Intercepción de Entrada vía Mesa de Partes Digital**

En los escenarios donde la ley de gobierno digital exige la interoperabilidad en la entrada de documentos de mesa de partes virtual 16:

* Se interceptan los documentos de forma temprana durante la fase de carga y registro en el portal web de la Mesa de Partes Digital de la entidad pública antes de que estos ingresen al flujo cerrado del SIGED.16  
* El sistema de Mesa de Partes, al recibir los PDF firmados digitalmente del TDR o de la propuesta del postor ganador, ejecuta una notificación de fondo (*Webhook*) enviando los binarios directamente al almacenamiento de MinIO del asistente de IA.10  
* La metadata preliminar se indexa en la base de datos PostgreSQL, dejando el expediente en un estado de procesamiento previo listo para que, cuando el funcionario abra su bandeja en el SIGED de forma manual, el asistente ya tenga preparados y analizados los borradores de las bases o del contrato correspondiente.

## **F. Recomendación específica para iniciar con Bases**

La estrategia recomendada para iniciar el despliegue del proyecto con la máxima probabilidad de éxito funcional y menor resistencia operativa consiste en priorizar obligatoriamente el **Asistente IA para generación de Bases Estándar (Fase 1\)** frente al asistente de contratos.

### **Justificación de la prioridad de inicio**

#### **Menor variabilidad e incertidumbre documental**

El flujo del asistente de bases requiere únicamente el análisis de un único documento técnico estructurado de entrada: el Término de Referencia (TDR) o las Especificaciones Técnicas (EE.TT.). El procesamiento cognitivo de OCR y extracción mediante el LLM se enfoca de manera exclusiva en mapear secciones predecibles, tales como las especificaciones técnicas del servicio, el cronograma de entregables, el porcentaje de penalidades y los plazos de ejecución.5 Por el contrario, el asistente de contratos es un sistema multi-documental sumamente complejo que debe leer, categorizar y realizar validaciones cruzadas entre cinco o más fuentes con diseños tipográficos, calidades de escaneo e idiomas técnicos variables (propuestas técnicas, económicas, consorcios, cartas fianza, vigencias de poder).5

#### **Plantillas institucionales predefinidas y estandarizadas**

Las plantillas oficiales de bases estándar emitidas por el OSCE poseen una estructura modular sumamente madura y rígida en formato Word, con secciones bien diferenciadas para Bienes, Servicios y Consultorías.4 Esta estandarización permite pre-etiquetar las plantillas del OSCE con variables de Jinja2 de manera sumamente precisa en el motor docxtpl, minimizando fallos de diagramación al sustituir variables dinámicas.29

#### **Menor riesgo de responsabilidad administrativa y civil**

La emisión de un borrador de bases estándar constituye una fase preparatoria de convocatoria pública y libre concurrencia de postores. Cualquier discrepancia o error material que la inteligencia artificial pueda dejar pasar puede ser identificado y subsanado de manera regular y legal por los postores durante la fase obligatoria de "Consultas y Observaciones" regulada por la Ley de Contrataciones del Estado, antes de la integración definitiva de las bases.5 Un error material en un contrato formalizado, sin embargo, genera un impacto inmediato y vinculante de carácter financiero y legal, exponiendo a los funcionarios públicos a rigurosas investigaciones y responsabilidades administrativas del Órgano de Control Institucional (OCI).

### **Plan de acción estructurado para la Fase 1: MVP de Bases**

1. **Paso 1: Normalización de Plantillas OSCE.** El equipo legal descarga las plantillas de Bases Estándar actualizadas según las directivas del OSCE.4 Utilizando Microsoft Word, se insertan etiquetas Jinja2 de forma limpia y rigurosa en el texto (por ejemplo, {{ objeto\_licitacion }}, {{ cronograma\_entregables }}).29 Se definen condiciones booleanas de renderizado dinámico para diferenciar procedimientos normales de procedimientos abreviados.30  
2. **Paso 2: Entrenamiento del Extractor Layout OCR.** Se cargan historiales de TDRs institucionales en formato PDF escaneado en el servicio de Azure AI Document Intelligence para mapear la posición física de las tablas de entregables y la sección de penalidades.24 Se refina el sistema de prompts locales del LLM para forzar la salida estructurada de estas secciones en formato JSON aplicando esquemas tipados de Pydantic.13  
3. **Paso 3: Desarrollo del Portal del Funcionario (Streamlit/FastAPI).** Se construye la interfaz de usuario dividida en tres columnas lógicas:  
   * Columna Izquierda: Carga del TDR en PDF, selección automática de la plantilla de bases recomendada por la IA (Bienes, Servicios o Consultoría).4  
   * Columna Central: Panel dinámico de formularios web con los datos extraídos por el OCR/NLP para que el funcionario pueda realizar modificaciones, correcciones manuales o ingresar datos puramente administrativos faltantes en el TDR.  
   * Columna Derecha: Visor de PDF integrado de solo lectura con el TDR original para contrastar visualmente la información extraída.43  
4. **Paso 4: Generación y Control de Calidad del Word.** Al presionar "Generar Bases", el backend FastAPI procesa en memoria el JSON aprobado de variables con la plantilla en la librería docxtpl.29 El sistema guarda la versión final editable .docx en el clúster local de MinIO y habilita su descarga inmediata 10, registrando en PostgreSQL qué datos fueron modificados manualmente por el funcionario respecto al borrador original sugerido por la IA para auditoría futura de la precisión del modelo.

## **G. Recomendación específica para luego escalar a Contratos**

El escalamiento hacia el **Asistente IA para Generación de Contratos (Fase 2\)** capitaliza toda la infraestructura de hardware, clústeres de inferencia local de vLLM 25, servicios locales de OCR 24 y persistencia ya estabilizados en la Fase 1\. No obstante, por su complejidad, este asistente requiere un diseño de control de calidad mucho más riguroso enfocado en validaciones analíticas y trazabilidad.

### **Pautas para el control de calidad y validación de consistencia**

Para mitigar por completo el riesgo de alucinaciones del modelo de lenguaje y asegurar que la formalización del documento contractual guarde correspondencia estricta con las etapas de selección previas 5, el sistema de contratos implementa un protocolo de validaciones cruzadas obligatorias divididas en tres categorías analíticas:

                           

        ┌────────────────────────────────────────────────────────────────────────┐  
        ▼ (Paso 1: Extracción de Estructuras JSON mediante Azure OCR \+ vLLM)    │  
               
        │                                │                              │  
        ▼                                ▼                              ▼  
 ┌──────────────────────────────────────────────────────────────────────────────────────┐  
 │                     │  
 │                                                                                      │  
 │  1\. CONTROL DE MONTO:                                                                │  
 │     Monto Contrato \== Monto Oferta Económica \<= Valor Estimado Bases Integradas.     │  
 │                                                                                      │  
 │  2\. CONTROL DE PLAZO:                                                                │  
 │     Plazo Ejecución Contrato \== Plazo Oferta Técnica \<= Plazo Máximo Bases.          │  
 │                                                                                      │  
 │  3\. CONTROL DE FORMA DE PAGO Y ENTREGABLES:                                          │  
 │     Cronograma de Entregables Contrato \== Cronograma Oferta \== Cronograma Bases.      │  
 │                                                                                      │  
 │  4\. CONTROL DE GARANTÍA:                                                             │  
 │     Monto Garantía Carta Fianza \== 10% del Monto Total Adjudicado del Contrato.      │  
 │                                                                                      │  
 │  5\. CONTROL DE DATOS DE CONTRATISTA Y REPRESENTANTE LEGAL:                           │  
 │     RUC Activo Sunat \== RUC Postor Ganador.                                          │  
 │     DNI Representante Contrato \== DNI Representante de Vigencia de Poder (SUNARP).   │  
 └──────────────────────────────────────────────────────────────────────────────────────┘  
        │  
        ├─────────────────────────────┐  
        ▼ (Aprobación Exitosa)        ▼ (Fallo en Algún Control)  
   

* **Validaciones de Consistencia Financiera y Plazos:** El microservicio de contratos ejecuta un motor de validaciones matemáticas determinísticas escritas en código nativo de Python que evalúa las discrepancias de los JSON extraídos de los documentos de origen:  
  * El sistema valida que el monto total consignado en el borrador de contrato equivalga con precisión de centavos al monto extraído de la Oferta Económica del postor adjudicado, y que este monto no exceda en ningún caso el valor estimado especificado en las Bases Integradas finales de la licitación.5  
  * Valida que el plazo de ejecución estipulado en el contrato coincida exactamente con el plazo ofertado en el anexo de propuesta técnica del postor y que sea menor o igual al plazo máximo permitido por las bases de convocatoria.5  
  * Compara de forma automática mediante algoritmos de similitud de cadenas (*String Similarity*) el cronograma de entregables y la forma de pago (porcentaje de adelantos, pagos contra entrega) entre las Bases Integradas y la propuesta ganadora.5  
  * Valida que el monto y la vigencia de la Carta Fianza o Póliza de Garantía de Fiel Cumplimiento presentada por el contratista equivalga exactamente al diez por ciento (10%) del monto total de la adjudicación, comprobando además que la fecha de vencimiento de la fianza cubra la totalidad del plazo de ejecución más el proceso de liquidación.5  
* **Validaciones de Representación Legal e Identidad:** El microservicio extrae mediante OCR el número de Registro Único de Contratistas (RUC) del consorcio o postor ganador y el nombre del representante legal consignado en el contrato de consorcio o propuesta.5 El backend valida mediante consultas API a la SUNAT que el estado del RUC esté activo y habido. Asimismo, cruza el DNI y nombre del representante firmante contra el texto extraído del documento de Vigencia de Poder emitido por los Registros Públicos (SUNARP), verificando que la vigencia del poder de firma no haya expirado al momento del perfeccionamiento del contrato.5

### **Protocolo de trazabilidad y visor dual con grounding**

Para asegurar la supervisión humana de forma ágil y cumplir con la revisión humana obligatoria (*Human-in-the-Loop*), el frontend del asistente de contratos implementa una interfaz de "Visor Dual con Grounding":

* La pantalla se divide en dos paneles paralelos con desplazamiento sincronizado.  
* En el panel izquierdo, el funcionario legal revisa el borrador de contrato generado en formato .docx enriquecido, donde las variables dinámicas se muestran con marcas de resaltado de colores según el documento de origen (por ejemplo, el monto del contrato resaltado en verde, el plazo en azul).  
* Al hacer clic sobre cualquiera de las variables resaltadas en el contrato, el panel derecho se actualiza de forma automática mostrando el archivo PDF de origen correspondiente (como la Oferta Económica del proveedor o la Vigencia de Poder).43  
* Utilizando las coordenadas de cuadros delimitadores (*Bounding Box*) provistas por el OCR local de Azure AI Document Intelligence durante el procesamiento inicial 24, el panel derecho resalta y hace zoom directo sobre la línea exacta, párrafo u hoja específica del PDF fuente de donde se extrajo el dato.43  
* Este nivel de transparencia y trazabilidad técnica elimina la necesidad de que el abogado del Estado revise físicamente expedientes de cientos de páginas para validar los datos, permitiéndole aprobar el borrador con plena confianza, registrar su conformidad con firma digital oficial y ordenar el perfeccionamiento legal en el SIGED.1

## **H. Riesgos técnicos y funcionales**

La incorporación de sistemas inteligentes de procesamiento documental en el ámbito de la administración pública conlleva riesgos específicos y complejos que deben ser prevenidos de forma rigurosa desde la etapa inicial del diseño de la solución cloud.

### **Fragilidad estructural de plantillas de Word (.docx) por edición de usuarios**

El uso de la librería docxtpl con motor Jinja2 permite una automatización flexible de plantillas de Word creadas por abogados.29 Sin embargo, la edición directa de estas plantillas en Microsoft Word por usuarios legales no técnicos introduce un riesgo sumamente alto de corrupción del archivo XML subyacente de Word.31 Un usuario que accidentalmente modifique un estilo, rompa un bloque de etiquetas con saltos de línea (por ejemplo, dividiendo un bloque {% if %} en varias ejecuciones de texto interno de Word) o introduzca caracteres inválidos en la sintaxis Jinja, provocará fallos inmediatos y caídas silenciosas en el backend de FastAPI que imposibilitarán la compilación del contrato.30

#### **Estrategia de Mitigación**

Se establece un pipeline de pre-validación sintáctica estricta para la carga de nuevas plantillas en la biblioteca de la aplicación. Al cargar un nuevo documento base .docx, el backend analiza el árbol XML subyacente buscando inconsistencias de etiquetas rotas de Jinja2, balancines faltantes o instrucciones inválidas antes de registrar la plantilla como activa.30 Asimismo, en producción se recomienda migrar la edición y parametrización de etiquetas complejas hacia formularios de mapeo de metadatos integrados directamente en el frontend, donde las secciones dinámicas y tablas condicionales son procesadas de forma segura y transparente por librerías empresariales robustas como Aspose.Words.32

### **Alucinaciones y degradación de exactitud en lectura de documentos escaneados**

A pesar del extraordinario rendimiento de los modelos fundacionales de lenguaje (LLMs), su naturaleza es probabilística y no determinista.12 Al procesar documentos administrativos del Estado con firmas manuscritas, sellos marginales del comité de selección, resoluciones borrosas o fotocopias de baja calidad que han atravesado múltiples conversiones físicas 5, los motores de OCR genéricos pueden interpretar de forma errónea caracteres críticos, lo que lleva al LLM a alucinar cláusulas, exenciones de responsabilidad o montos numéricos que no figuran en los documentos originales de licitación.12

#### **Estrategia de Mitigación**

Se limita rigurosamente la autonomía de toma de decisiones del modelo de lenguaje en producción. El LLM se restringe exclusivamente a tareas de traducción semántica intermedia y extracción de variables estructuradas bajo tipos de datos rigurosos mediante esquemas estrictos de Pydantic.13 Cualquier extracción de datos clave debe ir acompañada obligatoriamente de un puntaje de confianza (*Confidence Score*) numérico emitido por el OCR local de Azure AI Document Intelligence y por el modelo vLLM.24 Si cualquier variable crítica del contrato o base posee un puntaje de confianza inferior al 95%, el sistema bloquea inmediatamente la autogeneración, emite una alerta detallada de baja precisión e invita al usuario legal a realizar un llenado manual guiado del campo afectado.13

## **I. Preguntas clave que se deben hacer al equipo funcional, infraestructura, seguridad y SIGED**

Para refinar el alcance del proyecto y asegurar que la arquitectura diseñada responda de forma exacta a las restricciones reales de la entidad pública, se debe formular el siguiente pliego de preguntas técnicas estructuradas a los distintos líderes de departamento de la institución.

### **Preguntas funcionales y de negocio (Abastecimiento y Área Legal)**

* ¿Cuáles son las tipologías exactas de contratos que gestiona la entidad y cuáles son las variaciones de las plantillas oficiales del OSCE para procedimientos especiales de selección (por ejemplo, la reactivación de obras públicas paralizadas bajo la Ley N° 31589 o procedimientos utilizando metodologías BIM)? 4  
* ¿Qué nivel de discrepancia aritmética o de plazo toleran legalmente antes de catalogar una propuesta ganadora como inconsistente con las bases integradas, y cómo se documenta formalmente la aprobación de las subsanaciones de las ofertas? 5  
* ¿Cuál es el volumen mensual y anual promedio de expedientes de bases estándar y contratos que se elaboran en la entidad pública, y cuántos usuarios concurrentes interactuarán con la plataforma en el escenario de máxima demanda en los cierres de año fiscal?

### **Preguntas de infraestructura y redes (Operaciones y DevOps)**

* ¿Se dispone actualmente de servidores físicos locales provistos de aceleradoras GPU con arquitectura de memoria unificada (como NVIDIA A100, H100, L40 o A10G) en el centro de datos corporativo de la entidad para el alojamiento dedicado del clúster vLLM? 10  
* ¿El clúster institucional de Kubernetes está basado en distribuciones comerciales con soporte a contenedores perimetrales (como RedHat OpenShift o SUSE Rancher) y cuenta con recursos de almacenamiento persistente rápido para la replicación activa de MinIO? 10  
* ¿La entidad pública opera bajo un entorno de red completamente aislado de internet pública (*Air-Gapped*) o se permite la conexión saliente controlada mediante proxies y VPNs hacia servicios específicos en nubes públicas extranjeras? 11

### **Preguntas de seguridad de la información y cumplimiento (CISO)**

* ¿Cuál es el procedimiento interno de la entidad para autorizar y registrar formalmente bancos de datos personales ante la Autoridad Nacional de Protección de Datos Personales (ANPD) conforme a las exigencias regulatorias de la Ley N° 29733 y el DS 016-2024-JUS? 9  
* ¿El Oficial de Seguridad de la Información exige la encriptación de datos en tránsito utilizando protocolos específicos como TLS 1.3 con certificados de cifrado firmados por una entidad de certificación de confianza nacional?  
* ¿Qué políticas de retención, borrado definitivo y clasificación de información confidencial de las adquisiciones estatales deben aplicarse para asegurar el cumplimiento de la ley de archivos del Perú? 8

### **Preguntas de integración documental (Líder del SIGED)**

* ¿El SIGED institucional cuenta con servicios de integración web (REST/JSON o SOAP/XML) activos y documentados que permitan consultar el árbol del expediente, buscar metadatos y descargar documentos binarios, o se requerirá acceso directo a las tablas de base de datos? 1  
* ¿Qué protocolo de autenticación e identificación utiliza la API del SIGED para autorizar la lectura de expedientes confidenciales (por ejemplo, autenticación basada en certificados digitales, firmas HMAC o tokens OAuth), y cómo se registran estas consultas automáticas en el historial de auditoría del expediente original? 1  
* ¿En qué formatos físicos se almacenan los binarios en el SIGED (por ejemplo, PDFs firmados digitalmente, imágenes TIFF escaneadas sin OCR, documentos Word originales) y cuál es el tamaño promedio y máximo de un expediente administrativo completo de adquisición pública?

## **J. Conclusión final con una propuesta priorizada**

El diseño propuesto para los Asistentes de IA de Bases Estándar y Contratos ofrece un camino claro hacia la transformación del proceso de adquisiciones públicas, integrando de manera balanceada agilidad funcional y rigurosidad legal.4 La recomendación metodológica y técnica priorizada de este análisis concluye en dos decisiones arquitectónicas clave para la entidad pública:  
En primer lugar, **iniciar obligatoriamente con el Asistente de Bases Estándar (Fase 1\)** de forma exclusiva durante los primeros tres meses de ejecución del roadmap. Este enfoque permite estabilizar la infraestructura de hardware local de GPUs 10, depurar el rendimiento del clúster de inferencia de vLLM 25, calibrar los modelos de OCR de español 44 y entrenar al personal del área legal en la correcta formulación de plantillas parametrizadas con docxtpl.29 Todo esto se realiza bajo un escenario operativo acotado y de bajo riesgo normativo, garantizando la maduración de la pila tecnológica antes de abordar la complejidad de la fase de contratos.  
En segundo lugar, se propone la adopción de una **arquitectura híbrida/local y soberana** que aproveche las virtudes de la nube pública solo para las interfaces de cara al usuario en fases de desarrollo, pero consolide la totalidad del procesamiento cognitivo, OCR, inferencia LLM y almacenamiento documental de producción dentro de la red corporativa autohospedada de la entidad pública.2 La selección tecnológica recomendada para el despliegue a gran escala combina de forma sinérgica la flexibilidad y resiliencia de herramientas de software libre con la robustez y precisión de suites de automatización empresarial:

                         

\* Orquestación de Procesos de Larga Duración: Clúster de Temporal.io sobre Kubernetes.  
\* Extracción OCR de Alta Precisión en Español: Contenedores locales de Azure AI Doc Intelligence.  
\* Procesamiento Semántico / Extracción de Datos: vLLM con modelo Mistral o LLaMA 3.1 70B local.  
\* Base de Datos Relacional y Vectorial Integrada: PostgreSQL distribuido con la extensión \`pgvector\`.  
\* Almacenamiento Inmutable de Binarios: Clúster distribuido local de MinIO Enterprise.  
\* Generación Documental Avanzada y Segura: Librería \`docxtpl\` complementada con la suite Aspose.Words.  
\* Firma y Autenticación Oficial: Integración nativa con Firma Perú y Keycloak mediante protocolo OIDC.\[1, 11\]

Este diseño técnico robusto, respaldado por un riguroso esquema híbrido de validación que bloquea alucinaciones mediante controles de código tradicionales 12, dota a la institución de un sistema altamente auditable y escalable. Asimismo, garantiza el cumplimiento sin fisuras de la Ley de Protección de Datos Personales N° 29733 8 y sitúa a la entidad pública a la vanguardia de la innovación gubernamental confiable en la región.

#### **Obras citadas**

1. El Sistema de Gestión Documental (SGD) \- Orientación, fecha de acceso: junio 12, 2026, [https://www.gob.pe/62915-el-sistema-de-gestion-documental-sgd](https://www.gob.pe/62915-el-sistema-de-gestion-documental-sgd)  
2. Plataforma Nacional de Gobierno Digital (PNGD) \- Campañas, fecha de acceso: junio 12, 2026, [https://www.gob.pe/institucion/pcm/campa%C3%B1as/32388-plataforma-nacional-de-gobierno-digital-pngd](https://www.gob.pe/institucion/pcm/campa%C3%B1as/32388-plataforma-nacional-de-gobierno-digital-pngd)  
3. Sistema de Gestión de Seguridad de la Información Normativa Nacional, fecha de acceso: junio 12, 2026, [https://info.qaliwarma.gob.pe/pubweb/sgsi/normatividad\_n.php](https://info.qaliwarma.gob.pe/pubweb/sgsi/normatividad_n.php)  
4. Bases Estándar \- Ley N° 30225 y otras normas, fecha de acceso: junio 12, 2026, [https://www.gob.pe/institucion/osce/colecciones/1104-legislacion-y-documentos-normativos-osce-directivas-vigentes](https://www.gob.pe/institucion/osce/colecciones/1104-legislacion-y-documentos-normativos-osce-directivas-vigentes)  
5. Aprobado mediante Directiva N° 001-2019-OSCE/CD \- Ministerio Publico, fecha de acceso: junio 12, 2026, [https://portal.mpfn.gob.pe/descargas/normas/d70680.pdf](https://portal.mpfn.gob.pe/descargas/normas/d70680.pdf)  
6. RESOLUCION N° 000048-2021-DP/SG \- Presidencia de la República del Perú, fecha de acceso: junio 12, 2026, [https://www.presidencia.gob.pe/docnormas/RS\_048\_2021\_DP\_SG.pdf](https://www.presidencia.gob.pe/docnormas/RS_048_2021_DP_SG.pdf)  
7. PL-13-04 Versión: 01 PLAN DE GOBIERNO DIGITAL Fecha, fecha de acceso: junio 12, 2026, [https://www.seal.com.pe/Plan%20de%20Gobierno%20Digital/PLAN%20DE%20GOBIERNO%20DIGITAL/PLAN%20DE%20GOBIERNO%20DIGITAL.pdf](https://www.seal.com.pe/Plan%20de%20Gobierno%20Digital/PLAN%20DE%20GOBIERNO%20DIGITAL/PLAN%20DE%20GOBIERNO%20DIGITAL.pdf)  
8. Cómo cumplir con la ley 29733 para la protección de datos personales en Perú \- ManageEngine, fecha de acceso: junio 12, 2026, [https://download.manageengine.com/latam/images/law-29733-peru-ebook.pdf](https://download.manageengine.com/latam/images/law-29733-peru-ebook.pdf)  
9. Revista SAPERE Facultad de Derecho – USMP Vol. 1 Núm. 28 (2025) Gobierno digital y protección de datos personales en la ad, fecha de acceso: junio 12, 2026, [https://portalrevistas.aulavirtualusmp.pe/index.php/SP/article/download/3271/4039/11549](https://portalrevistas.aulavirtualusmp.pe/index.php/SP/article/download/3271/4039/11549)  
10. Deploying Local LLMs for Enterprise: Ollama, vLLM, and RAG Pipelines \- Seypro, fecha de acceso: junio 12, 2026, [https://sey.pro/insights/local-llm-enterprise-deployment](https://sey.pro/insights/local-llm-enterprise-deployment)  
11. Local LLM Deployment: Privacy-First AI Complete Guide \- Digital Applied, fecha de acceso: junio 12, 2026, [https://www.digitalapplied.com/blog/local-llm-deployment-privacy-guide-2025](https://www.digitalapplied.com/blog/local-llm-deployment-privacy-guide-2025)  
12. The Capabilities and Limitations of Large Language Models in Document Automation, fecha de acceso: junio 12, 2026, [https://parseur.com/blog/llms-document-automation-capabilities-limitations](https://parseur.com/blog/llms-document-automation-capabilities-limitations)  
13. Designing an LLM-Based Document Extraction System | by Dikshith | Medium, fecha de acceso: junio 12, 2026, [https://medium.com/@dikshithraj03/turning-messy-documents-into-structured-data-with-llms-d8a6242a31cc](https://medium.com/@dikshithraj03/turning-messy-documents-into-structured-data-with-llms-d8a6242a31cc)  
14. AWS Textract vs Google Document AI vs Azure Doc Intelligence, fecha de acceso: junio 12, 2026, [https://invoicedataextraction.com/blog/aws-textract-vs-google-document-ai-vs-azure-document-intelligence](https://invoicedataextraction.com/blog/aws-textract-vs-google-document-ai-vs-azure-document-intelligence)  
15. Language and locale support for Read and Layout document analysis \- Document Intelligence \- Foundry Tools | Microsoft Learn, fecha de acceso: junio 12, 2026, [https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support/ocr?view=doc-intel-4.0.0](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support/ocr?view=doc-intel-4.0.0)  
16. MESA DE PARTES DIGITAL \- PCM, fecha de acceso: junio 12, 2026, [https://mesapartesdigital.pcm.gob.pe/](https://mesapartesdigital.pcm.gob.pe/)  
17. Durable functions or Step Functions \- AWS Lambda \- AWS Documentation, fecha de acceso: junio 12, 2026, [https://docs.aws.amazon.com/lambda/latest/dg/durable-step-functions.html](https://docs.aws.amazon.com/lambda/latest/dg/durable-step-functions.html)  
18. Top Temporal Alternatives for Workflow Orchestration | Kestra, fecha de acceso: junio 12, 2026, [https://kestra.io/resources/infrastructure/temporal-alternatives](https://kestra.io/resources/infrastructure/temporal-alternatives)  
19. Durable Functions Overview: Stateful Serverless Workflows | Microsoft Learn, fecha de acceso: junio 12, 2026, [https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview)  
20. AWS Step Functions vs. Temporal: Long-Running Workflow ..., fecha de acceso: junio 12, 2026, [https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows](https://scalewithchintan.com/blog/step-functions-vs-temporal-long-running-workflows)  
21. Decreto Supremo \- Publicacion Oficial \- Diario Oficial El Peruano, fecha de acceso: junio 12, 2026, [https://edicioneslegales.com.pe/wp-content/uploads/2025/07/098-2025-PCM.pdf](https://edicioneslegales.com.pe/wp-content/uploads/2025/07/098-2025-PCM.pdf)  
22. Software de Gestión Documental – Siged \- Archivos y Sistemas AYS SAS, fecha de acceso: junio 12, 2026, [https://www.archivosysistemas.com/software-de-gestion-documental-siged/](https://www.archivosysistemas.com/software-de-gestion-documental-siged/)  
23. Best AI for Document Analysis in 2026 \- Tested & Ranked | Mixpeek, fecha de acceso: junio 12, 2026, [https://mixpeek.com/curated-lists/best-ai-for-document-analysis](https://mixpeek.com/curated-lists/best-ai-for-document-analysis)  
24. Azure Document Intelligence (now part of Azure Content Understanding in Foundry Tools), fecha de acceso: junio 12, 2026, [https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence](https://azure.microsoft.com/en-us/products/ai-foundry/tools/document-intelligence)  
25. Ollama vs vLLM: A Comprehensive Guide to Local LLM Serving | by ..., fecha de acceso: junio 12, 2026, [https://medium.com/@mustafa.gencc94/ollama-vs-vllm-a-comprehensive-guide-to-local-llm-serving-91705ec50c1d](https://medium.com/@mustafa.gencc94/ollama-vs-vllm-a-comprehensive-guide-to-local-llm-serving-91705ec50c1d)  
26. Ley N° 29733 – Ley de Protección de Datos Personales, fecha de acceso: junio 12, 2026, [https://doc.contraloria.gob.pe/documentos/Cuadro\_Ley\_Proteccion\_Datos\_Personales.pdf](https://doc.contraloria.gob.pe/documentos/Cuadro_Ley_Proteccion_Datos_Personales.pdf)  
27. vLLM vs Ollama vs LocalAI: Best tools for self-hosting LLMs in 2025\. \- Engineer Master Labs, fecha de acceso: junio 12, 2026, [https://emasterlabs.com/self-hosting-llms-in-2025/](https://emasterlabs.com/self-hosting-llms-in-2025/)  
28. Parse PDF text and table data with Azure AI Document Intelligence \- Elastic, fecha de acceso: junio 12, 2026, [https://www.elastic.co/search-labs/blog/azure-ai-document-intelligence-parse-pdf-text-tables](https://www.elastic.co/search-labs/blog/azure-ai-document-intelligence-parse-pdf-text-tables)  
29. docxtpl \- PyPI, fecha de acceso: junio 12, 2026, [https://pypi.org/project/docxtpl/](https://pypi.org/project/docxtpl/)  
30. Welcome to python-docx-template's documentation\! — python-docx-template 0.20.x documentation, fecha de acceso: junio 12, 2026, [https://docxtpl.readthedocs.io/](https://docxtpl.readthedocs.io/)  
31. Stop Fighting Outdated DOCX Libraries: Modern API-Based Generation for SaaS, fecha de acceso: junio 12, 2026, [https://dev.to/kesimo/stop-fighting-outdated-docx-libraries-modern-api-based-generation-for-saas-578j](https://dev.to/kesimo/stop-fighting-outdated-docx-libraries-modern-api-based-generation-for-saas-578j)  
32. Python .docx tutorial | Create, open, and convert .docx file \- Paid Consulting \- Aspose, fecha de acceso: junio 12, 2026, [https://consulting.aspose.com/kb/python-docx-tutorial/](https://consulting.aspose.com/kb/python-docx-tutorial/)  
33. Guiding AI agents to reason correctly \- Predictika, fecha de acceso: junio 12, 2026, [https://predictika.com/assets/doc/Guiding\_AI\_agents\_to\_reason\_correctly.html](https://predictika.com/assets/doc/Guiding_AI_agents_to_reason_correctly.html)  
34. Compiled AI: Deterministic Code Generation for LLM-Based Workflow Automation \- arXiv, fecha de acceso: junio 12, 2026, [https://arxiv.org/html/2604.05150v1](https://arxiv.org/html/2604.05150v1)  
35. Benchmarking LLM-Based Static Analysis for Secure Smart Contract Development: Reliability, Limitations, and Potential Hybrid SolutionsThis work is an extended version of the paper accepted for publication at IEEE COMPSAC 2026\. \- arXiv, fecha de acceso: junio 12, 2026, [https://arxiv.org/html/2605.11163v1](https://arxiv.org/html/2605.11163v1)  
36. Seguridad digital \- Gobierno del Perú, fecha de acceso: junio 12, 2026, [https://www.gob.pe/seguridaddigital](https://www.gob.pe/seguridaddigital)  
37. Comprehensive Guide \- Creating Word Documents Using Python, fecha de acceso: junio 12, 2026, [https://tutorials.aspose.com/words/python-net/document-creation/creating-word-documents-using-python/](https://tutorials.aspose.com/words/python-net/document-creation/creating-word-documents-using-python/)  
38. Dynamic Data and Tables: Powering Up Your Documents with python-docx-template, fecha de acceso: junio 12, 2026, [https://medium.com/@lukas.forst/supercharge-your-word-reports-using-python-docx-template-4e9ebfc66b9e](https://medium.com/@lukas.forst/supercharge-your-word-reports-using-python-docx-template-4e9ebfc66b9e)  
39. Sistemas Automatizados de Gestión Documental \- YouTube, fecha de acceso: junio 12, 2026, [https://www.youtube.com/watch?v=Q1iUK06qozc](https://www.youtube.com/watch?v=Q1iUK06qozc)  
40. Document Management Model and its advances \- YouTube, fecha de acceso: junio 12, 2026, [https://www.youtube.com/watch?v=Ea3s27kLYn4](https://www.youtube.com/watch?v=Ea3s27kLYn4)  
41. Sistema de Tramite Documentario y mesa partes virtual \- Informes y publicaciones, fecha de acceso: junio 12, 2026, [https://www.gob.pe/institucion/pcm/informes-publicaciones/2002680-sistema-de-tramite-documentario-y-mesa-partes-virtual](https://www.gob.pe/institucion/pcm/informes-publicaciones/2002680-sistema-de-tramite-documentario-y-mesa-partes-virtual)  
42. Cómo entender las bases estándar bajo la nueva Ley de Contrataciones Públicas (sin morir en el intento) | CEAR LATINOAMERICANO, fecha de acceso: junio 12, 2026, [https://cearlatinoamericano.pe/blog/ley-n-32069-bases-estandar-contrataciones-publicas](https://cearlatinoamericano.pe/blog/ley-n-32069-bases-estandar-contrataciones-publicas)  
43. Best Document Parsing APIs 2026 \- LandingAI, fecha de acceso: junio 12, 2026, [https://landing.ai/llms/best-document-parsing-apis-2026](https://landing.ai/llms/best-document-parsing-apis-2026)  
44. azure-ai-docs/articles/ai-services/document-intelligence/language-support/ocr.md at main \- GitHub, fecha de acceso: junio 12, 2026, [https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-services/document-intelligence/language-support/ocr.md](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-services/document-intelligence/language-support/ocr.md)