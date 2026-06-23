Sistema de IA Documental para Entidad PúblicaDocumentación Técnica Consolidada (Volúmenes 1 y 2)VOLUMEN 1: Investigación de Arquitectura (Bases y Contratos)A. Resumen EjecutivoSe propone construir dos asistentes de inteligencia artificial para automatizar la generación de documentos contractuales en una entidad pública: el Asistente de Bases Estándar y el Asistente de Contratos. Ambos sistemas requieren integración con el sistema SIGED, procesamiento inteligente de documentos, extracción de información mediante OCR/NLP, y generación de archivos .docx auditables con revisión humana obligatoria.⚠️ Restricción Crítica:Los documentos procesados son sensibles (expedientes de contratación, ofertas económicas, vigencia de poder, datos del contratista). Cualquier componente cloud debe evaluarse bajo la política de datos de la entidad antes de enviar documentos al exterior. Se priorizan soluciones con residencia de datos local o cifrado extremo a extremo.Hallazgos ClaveAsistente de Bases: Flujo acotado y repetible, ideal para MVP. La mayor complejidad recae en OCR de TDR y llenado de plantillas .docx. Tiempo estimado de implementación MVP: 3–5 meses.Asistente de Contratos: Requiere validación de consistencia entre múltiples documentos fuente y supervisión legal. Se recomienda iniciarlo solo cuando el Asistente de Bases esté en producción estable. Tiempo adicional: 4–6 meses.Stack Recomendado para MVP: FastAPI + React + Tesseract/PaddleOCR + LLM vía API (Azure OpenAI o AWS Bedrock, con opción on-premise Ollama) + PostgreSQL + MinIO + docxtpl.Stack Recomendado para Producción: Kubernetes (on-premise o cloud privado) + Azure AI Document Intelligence o AWS Textract + LLM gestionado con VPC/VNET + pgvector RAG + auditoría centralizada.Riesgo Principal: Alucinaciones del LLM en campos críticos (montos, plazos, RUC). Mitigado con extracción determinística + validación de confianza + revisión humana.B. Tablas Comparativas por ComponenteB.1 · Frontend / Interfaz de UsuarioCriterioAWS Amplify + ReactAzure Static Web Apps + ReactNext.js / Streamlit (On-prem)GradioCaso de usoApp web enterprise con auth CognitoApp web con Azure AD SSOCualquier despliegue propioPrototipo rápido IAComponentes documentalesreact-pdf, docx-preview (JS)react-pdf, docx-preview (JS)react-pdf, mammoth.jsLimitado (HTML básico)Formularios dinámicosReact Hook Form, FormikReact Hook Form + Azure PnPReact Hook Form, shadcn/uiComponentes nativos simplesAutenticaciónCognito (OIDC, MFA)Azure AD B2C / Entra IDKeycloak, Auth0, JWT propioBásica (contraseña)VentajasCI/CD integrado, CDN globalIntegración nativa con AD corporativoControl total, sin vendor lock-inMuy rápido de prototiparDesventajasDependencia cloud, costo en tráficoRequiere suscripción Azure activaInfraestructura propia a mantenerNo apto para producciónMVPRecomendado: Next.js + React + shadcn/uiProducciónRecomendado: Next.js + SSO institucionalComplejidadMediaMediaBaja-MediaBajaRiesgosCosto inesperado, lock-inRequiere licencias AzureEsfuerzo de mantenimientoNo escalableB.2 · Backend / OrquestadorAlternativaTipoVentajasDesventajasMVPProducciónComplejidadFastAPI (Python)MicroservicioNativo Python/IA, async, OpenAPI auto-docRequiere gestión de servidorRecomendadoRecomendado (con K8s)BajaAWS Lambda + Step FunctionsServerlessSin servidor, escalado automáticoCold starts, límite 15 minAceptableBueno para picosMediaAzure FunctionsServerlessOrquestación stateful, ecosistema AzureLock-in, costos en uso continuoAceptableBueno en AzureMediaNestJS (Node.js)MicroservicioArquitectura modular, TypeScriptPython es más natural para IAAlternativoSíMediaSpring Boot (Java)MicroservicioEnterprise-grade, robusto, seguroPesado para IA/MLNoSi ya usan JavaAltaTemporal.ioWorkflow EngineWorkflows duraderos, retry autoCurva de aprendizaje, infraNoContratos complejosAltaAzure Logic AppsLow-codeVisual, fácil integraciónLimitado para IA complejaNoNo aptoBajaB.3 · Integración con SIGED / Sistema DocumentarioPatrónDescripciónCuándo usarVentajasRiesgosComplejidadREST APILlamadas HTTP directas con auth tokenSIGED expone API RESTSimple, estándar, tiempo realDisponibilidad, versiónBajaSOAP/WSWeb Services XML legadosSIGED usa SOAP legadoMuy estable, contratos XMLVerboso, mantenimientoMediaBatch / ETLExtracción nocturna a BD localNo hay API o tiene restriccionesReduce carga, funciona offlineDatos no actualizadosMediaColas de mensajesSIGED publica, backend consumeSIGED soporta RabbitMQ/SQSDesacoplado, resilienteRequiere soporte SIGEDAltaRPA / ScrapingRobot navega web UI para extraerSin API disponibleSin cambios en SIGEDFrágil ante cambios UIAltaAcceso DB directoConexión directa BD (solo lectura)Misma red, con autorizaciónRápido, datos completosAcoplamiento fuerteMediaB.4 · Almacenamiento DocumentalAlternativaTipoCifradoVersionadoOn-premiseCostoMVPProducciónMinIOObject Storage S3✅ AES-256✅✅Gratis (OSS)RecomendadoRecomendadoAWS S3Object Storage Cloud✅ SSE-KMS✅❌~$0.023/GB/mesSíSíAzure BlobObject Storage Cloud✅ AES-256✅❌~$0.018/GB/mesSíSíFile Server NASSistema de archivos⚠️ Configurable❌ Manual✅Solo hardwareAceptableNoSIGED RepositoryRepositorio interno✅ Propio✅✅Ya contratadoAceptableAceptableB.5 · Base de Datos / PersistenciaAlternativaTipoVentajasDesventajasMVPProducciónComplejidadPostgreSQLRelacional OSSACID, pgvector, JSON, maduroRequiere tuning avanzadoRecomendadoRecomendadoBajaSQL ServerRelacional MSComún en sector públicoLicenciamiento costosoAceptableAceptableMediaAWS RDS PostgresRelacional ManagedManaged, backups auto, HACosto cloud, datos fueraAceptableSi cloud aprobadoBajaDynamoDBNoSQL AWSSin servidor, infinito escaladoLock-in, consultas limitadasNoAceptableMediaMongoDBNoSQL DocumentalFlexible para JSON variablesSin ACID nativo completoNoAceptableMediaSQLiteRelacional EmbebidoCero configuración, portableNo concurrente, no HASolo prototipoNoBajaB.6 · OCR — Reconocimiento Óptico de CaracteresAlternativaTipoPrecisiónEspañolTablasPDF EscanCostoOn-premiseMVPProdAzure Doc IntelligenceCloud⭐⭐⭐⭐⭐ExcelenteExcelente✅~$1.5/1k pág❌AceptableRecomendadoAWS TextractCloud⭐⭐⭐⭐⭐Muy buenoExcelente✅~$1.5/1k pág❌AceptableRecomendadoGoogle Document AICloud⭐⭐⭐⭐⭐ExcelenteBueno✅~$1.5/1k pág❌NoAceptablePaddleOCROpen Source⭐⭐⭐⭐BuenoBueno✅Gratis✅RecomendadoRecomendadoTesseract OCROpen Source⭐⭐⭐AceptableLimitado⚠️Gratis✅PrototipoAceptableEasyOCROpen Source⭐⭐⭐⭐Bueno⚠️✅Gratis✅AceptableAceptableSurya OCROpen Source⭐⭐⭐⭐⭐Muy buenoBueno✅Gratis✅AceptableRecomendadoDocling (IBM)Open Source⭐⭐⭐⭐BuenoBueno✅Gratis✅AceptableRecomendadoB.7 · NLP / Extracción de InformaciónAlternativaEnfoqueVentajasDesventajasPrivacidadMVPProducciónLLM EstructuradoGenerativoMáxima flexibilidad, contextoPuede alucinar, lento⚠️ CloudRecomendado✅ Con validaciónLangChainFramework RAGOrquestación, JSON estructuradoOverhead, dependencia⚠️ Depende LLMRecomendadoRecomendadospaCy + ReglasReglas + NERDeterminístico, rápido, on-premInflexible✅ TotalAceptableAceptableRegexDeterminístico100% fiable en formatos fijosRígido✅ TotalRecomendadoRecomendadoAzure OpenAI ExtractionHíbridoNER avanzadoDatos salen de la red⚠️ CloudAceptableSi cloud aprobadoAmazon ComprehendNLP CloudNER, sentimentEspañol limitado⚠️ CloudNoAceptableB.8 · Motor de IA Generativa / LLMAlternativaPrivacidadEspañolRazonamientoCostoOn-premiseGobernanzaMVPProdAzure OpenAI (GPT-4o)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐~$0.005/1k t❌ExcelenteRec.Rec.AWS Bedrock (Claude)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐~$0.003/1k t❌ExcelenteRec.Rec.Ollama + Llama 3.1 (8B)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐Solo hardware✅Control totalRec.Solo con GPUOllama + Qwen2.5 (7B)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐Solo hardware✅Control totalRec.Rec.Mistral (7B)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐Solo hardware✅Control totalSíSíOpenAI API (Directo)⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐~$0.005/1k t❌LimitadaAceptableNoB.9 · RAG / Base de ConocimientoAlternativaOn-premiseEscalaEspañolTrazabilidadCostoMVPProducciónPostgreSQL + pgvector✅Media✅✅ SQL nativoGratisRecomendadoRecomendadoChromaDB✅Media✅✅GratisSíAceptableWeaviate✅ (OSS)Alta✅✅Gratis (OSS)AceptableRecomendadoMilvus✅Muy alta✅✅Gratis (OSS)NoSi gran escalaAzure AI Search❌Alta✅ Excelente✅~$250/mesAceptableSi AzureAmazon OpenSearch❌Alta✅✅~$150/mesAceptableSi AWSB.10 · Motor de Plantillas Documentales (.docx)AlternativaLenguajeSecciones CondTablasFormatoMadurezLicenciaMVPProddocxtplPython✅ Jinja2✅✅ AltaAltaMITRec.Rec.python-docxPython⚠️ Manual✅⚠️ MediaAltaMITSíAceptableAspose.WordsPython/Java✅ Total✅✅ TotalMáximaComercialNoSi hay budgetApache POIJava✅✅✅AltaApache 2AceptableSi ya usan JavaC. Arquitectura Recomendada para MVPEl MVP se ejecutará de forma 100% Local / On-Premise para proteger la privacidad de los documentos mientras se valida la tecnología.+-------------------------------------------------------------------------------+
|                                 USUARIO                                       |
|                  (Interfaz Next.js / React en Navegador)                      |
+-------------------------------------------------------------------------------+
                                       | HTTPS (SSO Keycloak)
                                       v
+-------------------------------------------------------------------------------+
|                              API GATEWAY (NGINX)                              |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                       ORQUESTRADOR BACKEND (FastAPI)                          |
+-------------------------------------------------------------------------------+
      |                        |                        |
      | Tareas Async           | DB Access              | Object Store
      v                        v                        v
+--------------+        +--------------+        +--------------+
| CELERY WORKER|        |  POSTGRESQL  |        |    MinIO     |
|   (Redis)    |        | (+ pgvector) |        | (S3 Storage) |
+--------------+        +--------------+        +--------------+
      | (OCR / NLP / docxtpl)
      +--------------------------> Pipeline Local: PyMuPDF / PaddleOCR
                                   Modelos Locales: Ollama (Qwen2.5:7b)
                                   Generación: docxtpl + LibreOffice Headless
D. Arquitectura Recomendada para ProducciónPara la fase de producción se plantea un entorno Híbrido de Alta Disponibilidad, segregando datos sensibles a servidores on-premise y apoyando procesos de carga masiva en nubes corporativas privadas.                                  [ NAVEGADOR WEB (Next.js) ]
                                               |
                                               v
                                [ WAF / KONG API GATEWAY (HA) ]
                                               |
              +--------------------------------+--------------------------------+
              | (On-Premise / Datos Sensibles)                                  | (Cloud Privado - VNet)
              v                                                                 v
+-------------------------------+                                 +-------------------------------+
|  MICROSERVICIOS K8S LOCALES   |                                 |       SERVICIOS CLOUD         |
|  - svc-bases / svc-contratos  |                                 |  - Azure AI Doc Intelligence  |
|  - svc-documentos (docxtpl)   |                                 |  - Azure OpenAI (GPT-4o)      |
+-------------------------------+                                 +-------------------------------+
              |                                                                 |
              +--------------------------------+--------------------------------+
                                               v
                              +---------------------------------+
                              |   INFRAESTRUCTURA PERSISTENTE   |
                              |   - PostgreSQL HA (Patroni)     |
                              |   - MinIO Distributed Cluster   |
                              |   - Temporal.io Workflows       |
                              +---------------------------------+
E. Alternativas si no existe API de SIGEDSi el sistema SIGED institucional no cuenta con endpoints disponibles, se plantean las siguientes alternativas:Capa Adaptadora sobre Base de Datos (Opción Preferida): Desarrollar un microservicio que lea directamente la base de datos de SIGED con permisos de solo lectura de forma segura y exponga endpoints REST customizados.Carga Batch Programada: Crear un proceso ETL nocturno o periódico que extraiga los metadatos y documentos nuevos de la base de datos de SIGED a la base de datos del asistente.Carga Manual del Expediente (Opción MVP): El usuario descarga el expediente completo en un archivo comprimido (.zip) o PDFs individuales desde la interfaz de SIGED y los sube de manera manual al asistente.Scraping mediante RPA: Utilizar robots (Selenium/Playwright) que inicien sesión, busquen el expediente y descarguen los archivos simulando las acciones de un humano. Es la opción más inestable ante cambios en la interfaz de SIGED.F. Recomendación Específica para Iniciar con BasesEl desarrollo del Asistente de Bases debe priorizarse por las siguientes razones:Posee un flujo secuencial predecible (1 expediente -> 1 TDR -> 1 plantilla -> 1 bases).Las plantillas estándar de la OSCE están altamente normalizadas.El riesgo de impacto legal directo ante un error de alucinación es menor en comparación con el contrato final firmado.Flujo del Asistente de Bases[Ingreso Exp. SIGED] ──> [Descarga TDR] ──> [OCR / NLP Extracción] ──> [Revisión en Formulario] ──> [Borrador .docx con Marca de Agua] ──> [Aprobación Humana] ──> [Bases Finales]
G. Escalado a ContratosRequisitos Previos para el EscaladoEl Asistente de Bases debe estar operando de manera estable y madura en producción.El pipeline OCR de documentos escaneados debe registrar una tasa de precisión superior al 90%.Debe existir un canal formal de integración y sincronización de datos con el SIGED.Matriz de Complejidades en ContratosDesafíoSolución TécnicaComplejidadMúltiples fuentes concurrentes (5+ documentos)Workers paralelos asíncronos en Celery / RabbitMQ.AltaClasificación del tipo de documentoClasificador LLM con prompts de pocas muestras (few-shot).MediaValidación cruzada de consistenciaMotor de reglas Python determinístico + comparación semántica LLM.AltaTrazabilidad campo -> documento originalMapeo de coordenadas Bounding Boxes y metadatos de página en Postgres.MediaH. Riesgos Técnicos y FuncionalesRiesgoProbabilidadImpactoMitigaciónAlucinaciones del LLM en montos/fechasAltaMuy AltoProcesar datos numéricos mediante Regex estructurado y usar el LLM únicamente para resúmenes de texto libre y validación semántica.Mala calidad de OCR en PDF escaneadoMedia-AltaAltoIntegrar filtros de preprocesamiento de imagen (reducir ruido, binarización) y gatillar alertas si la confianza del OCR es inferior al 80%.Inexistencia de API o accesibilidad SIGEDMediaMuy AltoDiseñar la arquitectura desacoplada para admitir carga manual asistida y batch en el MVP como fallback.Fuga de datos confidenciales a la nubeMediaMuy AltoUtilizar modelos locales (Ollama) o nubes privadas bajo estricto contrato de protección de datos (Zero Data Retention).Resistencia al cambio por usuariosAltaAltoInvolucrar a los analistas de la OEC en la definición de la interfaz de usuario e implementar capacitaciones continuas.I. Preguntas Clave por DominioI.1 · Dominio Funcional¿Cuántos expedientes procesa la OEC mensualmente y cuáles tienen mayor prioridad?¿Cuáles son las observaciones más comunes que realiza el órgano supervisor (OSCE) a las bases autogeneradas?I.2 · Dominio TI e Infraestructura¿Se cuenta con servidores con GPU CUDA para el hosting local de LLMs?¿Cuál es el proceso y tiempo promedio de aprobación para el aprovisionamiento de recursos cloud públicos?I.3 · Dominio Seguridad¿Cuáles son los requisitos legales de la entidad para el almacenamiento de datos en la nube de acuerdo a la Ley de Protección de Datos Personales?¿Qué auditorías de código o pruebas de penetración son obligatorias antes del pase a producción?J. Conclusión Final y Propuesta PriorizadaEl stack tecnológico óptimo recomendado para la construcción del sistema combina estabilidad y control:MVP (Bases): FastAPI + Next.js + PostgreSQL + pgvector + MinIO + docxtpl + Ollama (Qwen2.5:7b) local en Docker Compose.Producción (Bases + Contratos): Arquitectura de microservicios sobre Kubernetes, almacenamiento distribuido de MinIO, orquestación de flujos de validación complejos con Temporal.io e inferencia híbrida (Local GPU para datos sensibles + Azure OpenAI para textos de plantillas públicas).VOLUMEN 2: Especificaciones Técnicas e ImplementaciónK. Esquema de Base de Datos Completo (PostgreSQL 16)El modelo de datos está diseñado para soportar ambos asistentes con trazabilidad total: cada campo del documento final puede rastrearse hasta su documento fuente, página y método de extracción. Usa PostgreSQL con extensiones pgvector (RAG), pgcrypto (hash de documentos) y pg_audit (audit trail).K.1 · Tablas de Dominio — Expedientes y ProcesosColumnaTipoRestriccionesDescripciónTABLA: expedientesidUUIDPK, DEFAULT gen_random_uuid()ID interno úniconumero_sigedVARCHAR(50)NOT NULL, UNIQUENúmero de expediente en SIGEDtipo_procesoVARCHAR(20)CHECK IN ('AS','ADS','LP','CP','MC','SIE')Tipo de proceso de contrataciónobjetoTEXTObjeto de la convocatoriavalor_referencialNUMERIC(15,2)Monto referencial en Solesestado_sigedVARCHAR(50)Estado actual en SIGEDmetadatos_sigedJSONBRespuesta JSON completa del API SIGEDultima_sincronizTIMESTAMPTZÚltima consulta de actualizacióncreated_atTIMESTAMPTZDEFAULT NOW()Fecha de creación del registroTABLA: documentos_fuenteidUUIDPKID único del archivoexpediente_idUUIDFK -> expedientes.idExpediente al que pertenecetipo_documentoVARCHAR(30)CHECK IN ('TDR','BASES_INTEGRADAS',...)Tipo de documento para el análisisnombre_archivoVARCHAR(255)NOT NULLNombre original del archivostorage_keyVARCHAR(500)NOT NULLRuta única de objeto en MinIOhash_sha256CHAR(64)NOT NULLHash de integridad SHA-256tamano_bytesBIGINTTamaño del archivo en bytesnum_paginasINTEGERCantidad de páginas del documentoes_pdf_digitalBOOLEANTRUE = Texto seleccionable de origenestado_ocrVARCHAR(20)DEFAULT 'PENDIENTE'PENDIENTE/PROCESANDO/COMPLETADO/ERRORocr_completado_atTIMESTAMPTZTimestamp de término de OCRtexto_extraidoTEXTTexto plano extraído completoconfianza_promNUMERIC(5,2)Puntuación de confianza promedio OCRorigenVARCHAR(20)CHECK IN ('SIGED','MANUAL','RPA')Origen de cargauploaded_byUUIDFK -> usuarios.idUsuario que subió el documentocreated_atTIMESTAMPTZDEFAULT NOW()Fecha de registroK.2 · Tablas de Extracción — Datos e InferenciasColumnaTipoRestriccionesDescripciónTABLA: campos_extraidosidUUIDPKID únicodocumento_fuente_idUUIDFK -> documentos_fuente.idDocumento de origenproceso_idUUIDFK -> procesos_generacion.idProceso de generación activonombre_campoVARCHAR(100)NOT NULLIdentificador del campo extraídovalor_extraidoTEXTValor literal extraídovalor_normalizadoTEXTValor después de tipado y limpiezatipo_datoVARCHAR(20)CHECK IN ('TEXTO','FECHA','MONTO',...)Tipo del campometodo_extraccionVARCHAR(20)CHECK IN ('REGEX','LLM','MANUAL',...)Método utilizadopagina_fuenteINTEGERPágina donde se ubicó la informacióncoordenadas_bboxJSONBCoordenadas delimitadoras para highlightconfianzaNUMERIC(5,2)Score de confianza (0.0 a 1.0)fue_corregidoBOOLEANDEFAULT FALSEFlag de edición manual del usuariovalor_originalTEXTValor previo a la correccióncorregido_porUUIDFK -> usuarios.idUsuario correctorreq_revisionBOOLEANDEFAULT FALSERequiere revisión humana obligatoriamotivo_revisionTEXTDetalle del flag de revisióncreated_atTIMESTAMPTZDEFAULT NOW()Fecha de inserciónTABLA: procesos_generacionidUUIDPKID del flujo de trabajo de generaciónexpediente_idUUIDFK -> expedientes.idExpediente asociadotipo_asistenteVARCHAR(20)CHECK IN ('BASES','CONTRATO')Tipo de flujo de asistentetipo_plantillaVARCHAR(30)CHECK IN ('BIENES_NORMAL',...)Identificador de plantilla objetivoestadoVARCHAR(25)CHECK IN ('INICIADO','BORRADOR',...)Estado actual del flujo de trabajodatos_adminJSONBCampos editados/cargados manualmenteversion_plantillaVARCHAR(20)Versión de la plantilla utilizadaerroresJSONBLista de errores de validación lógicainiciado_porUUIDFK -> usuarios.idUsuario creador del procesoiniciado_atTIMESTAMPTZDEFAULT NOW()Timestamp de iniciofinalizado_atTIMESTAMPTZTimestamp de término de flujoK.3 · Tablas de Documentos Generados y RevisionesColumnaTipoRestriccionesDescripciónTABLA: documentos_generadosidUUIDPKID de documentoproceso_idUUIDFK -> procesos_generacion.idProceso generadorversionINTEGERNOT NULL, DEFAULT 1Número secuencial de versiónestadoVARCHAR(20)CHECK IN ('BORRADOR','APROBADO',...)Estado del archivo finalstorage_keyVARCHAR(500)NOT NULLKey de objeto en MinIOnombre_archivoVARCHAR(255)NOT NULLNombre de salidahash_sha256CHAR(64)NOT NULLHash de integridad del archivo Wordtamano_bytesBIGINTPeso en bytestiene_marca_aguaBOOLEANDEFAULT TRUETRUE si posee texto borrador impresometadatos_docxJSONBPropiedades embebidas del archivo .docxgenerado_porUUIDFK -> usuarios.idUsuario generadorgenerado_atTIMESTAMPTZDEFAULT NOW()Fecha de renderTABLA: revisionesidUUIDPKID de revisióndoc_generado_idUUIDFK -> documentos_generados.idDocumento revisadotipo_revisionVARCHAR(20)CHECK IN ('TECNICA','LEGAL',...)Nivel de revisióndecisionVARCHAR(20)CHECK IN ('APROBADO','OBSERVADO')DictamencomentariosTEXTNotas libresobs_detalleJSONBObservaciones estructuradas por camporevisado_porUUIDFK -> usuarios.id, NOT NULLUsuario revisorrevisado_atTIMESTAMPTZDEFAULT NOW()Fecha de dictamenTABLA: auditoria(Inmutable - Trigger UPDATE/DELETE)idBIGSERIALPKID incremental secuencialtimestampTIMESTAMPTZDEFAULT NOW(), NOT NULLFecha y hora del eventousuario_idUUIDFK -> usuarios.idID de usuario actorip_origenINETDirección IP del clienteaccionVARCHAR(60)NOT NULLAcción (ej. 'LOGIN', 'GENERAR_DOC')entidad_tipoVARCHAR(40)Nombre de la tabla afectadaentidad_idUUIDUUID del registro afectadodatos_antesJSONBCaptura de datos previa a la accióndatos_despuesJSONBCaptura de datos posterior a la acciónresultadoVARCHAR(10)CHECK IN ('OK','ERROR')Resultado del procesodetalle_errorTEXTStacktrace o mensaje de errorsesion_idVARCHAR(100)Token de sesión auditadaK.4 · Tablas de Usuarios, RAG y PlantillasColumnaTipoDescripciónTABLA: usuariosidUUID PKSub de Keycloak / ID único de autenticación federadaemailVARCHAR(150) UNIQUECorreo electrónico corporativonombre_completoVARCHAR(200)Nombre completo del funcionariorolesTEXT[]Roles del sistema (['ANALISTA','REVISOR_LEGAL',...])activoBOOLEAN DEFAULT TRUEControl de estado activoultimo_loginTIMESTAMPTZFecha de último acceso exitosoTABLA: plantillas_docxidUUID PKID de plantillacodigoVARCHAR(30) UNIQUECódigo identificador (ej. BIENES_NORMAL_v3)nombreVARCHAR(200)Nombre funcionaltipo_procesoVARCHAR(30)Tipo de proceso de contratación asignableversionVARCHAR(10)Control de versión de plantillastorage_keyVARCHAR(500)Key del recurso .docx en el bucket de MinIOcampos_requeridosJSONBArreglo de variables requeridas para el render Jinja2activaBOOLEAN DEFAULT TRUEEstado de vigenciavigente_desdeDATEFecha de aprobación por directiva de OSCETABLA: knowledge_chunks(pgvector)idUUID PKID del chunktipo_fuenteVARCHAR(30)Tipo de documento de origen (ej. NORMA_OSCE)documento_nombreVARCHAR(255)Nombre del documento fuenteseccionTEXTTítulo de seccióncontenidoTEXTTexto plano del chunk indexadoembeddingVECTOR(1536)Embeddings vectoriales (Ada-002 o Nomic Local)metadatosJSONBMetadatos de referencia (artículos, decretos)vigenteBOOLEAN DEFAULT TRUEFlag de vigencia de norma-- Índices críticos para performance
CREATE INDEX idx_expedientes_numero_siged ON expedientes(numero_siged);
CREATE INDEX idx_campos_extraidos_proceso ON campos_extraidos(proceso_id, nombre_campo);
CREATE INDEX idx_auditoria_usuario_timestamp ON auditoria(usuario_id, timestamp DESC);
CREATE INDEX idx_auditoria_accion ON auditoria(accion, timestamp DESC);
CREATE INDEX idx_knowledge_embedding ON knowledge_chunks
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Trigger para audit trail inmutable
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'La tabla auditoria es inmutable. No se permite UPDATE ni DELETE.';
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_immutable
  BEFORE UPDATE OR DELETE ON auditoria
  FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
L. Pipeline OCR / NLP DetalladoL.1 · Detección de tipo de PDF y routing# services/ocr/detector.py
import fitz  # PyMuPDF
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class PDFType(Enum):
    DIGITAL = "digital"          # Texto seleccionable — no requiere OCR
    ESCANEADO = "escaneado"      # Solo imagen — requiere OCR
    MIXTO = "mixto"              # Algunas páginas texto, otras imagen

@dataclass
class PDFAnalysis:
    tipo: PDFType
    num_paginas: int
    paginas_con_texto: int
    paginas_solo_imagen: int
    ratio_texto: float              # 0.0 = todo imagen, 1.0 = todo texto
    requiere_ocr: bool

def detectar_tipo_pdf(ruta_pdf: Path) -> PDFAnalysis:
    doc = fitz.open(ruta_pdf)
    paginas_texto = 0
    UMBRAL_CHARS = 50  # mínimo chars para considerar página "con texto"

    for page in doc:
        texto = page.get_text("text").strip()
        if len(texto) > UMBRAL_CHARS:
            paginas_texto += 1

    total = len(doc)
    ratio = paginas_texto / total if total > 0 else 0

    if ratio >= 0.9:
        tipo = PDFType.DIGITAL
    elif ratio <= 0.1:
        tipo = PDFType.ESCANEADO
    else:
        tipo = PDFType.MIXTO

    return PDFAnalysis(
        tipo=tipo,
        num_paginas=total,
        paginas_con_texto=paginas_texto,
        paginas_solo_imagen=total - paginas_texto,
        ratio_texto=ratio,
        requiere_ocr=(tipo != PDFType.DIGITAL)
    )
L.2 · Extracción de texto completa con OCR condicional# services/ocr/extractor.py
import fitz
import pdfplumber
from paddleocr import PaddleOCR
from typing import List
import numpy as np
from PIL import Image

ocr_engine = PaddleOCR(lang='es', use_angle_cls=True, use_gpu=False)

@dataclass
class PaginaExtraida:
    numero: int
    texto: str
    confianza: float          # 0.0 - 1.0
    metodo: str               # 'DIRECTO' | 'PADDLEOCR' | 'HIBRIDO'
    bloques: List[dict]       # [{texto, bbox, confianza}]

def extraer_pagina_digital(pagina_fitz) -> PaginaExtraida:
    """Extrae texto de PDF con texto seleccionable."""
    blocks = pagina_fitz.get_text("blocks")  # [(x0,y0,x1,y1,texto,...)]
    texto_completo = pagina_fitz.get_text("text")
    bloques_fmt = [
        {"texto": b[4], "bbox": [b[0],b[1],b[2],b[3]], "confianza": 0.99}
        for b in blocks if b[4].strip()
    ]
    return PaginaExtraida(
        numero=pagina_fitz.number + 1,
        texto=texto_completo,
        confianza=0.99,
        metodo="DIRECTO",
        bloques=bloques_fmt
    )

def extraer_pagina_ocr(pagina_fitz, dpi: int = 300) -> PaginaExtraida:
    """Extrae texto de página imagen usando PaddleOCR."""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = pagina_fitz.get_pixmap(matrix=mat, alpha=False)
    img_array = np.frombuffer(pix.tobytes("png"), np.uint8)

    result = ocr_engine.ocr(img_array, cls=True)

    texto_lineas, bloques, confianzas = [], [], []
    for linea in (result[0] or []):
        bbox, (texto, conf) = linea
        texto_lineas.append(texto)
        confianzas.append(conf)
        bloques.append({"texto": texto, "bbox": bbox, "confianza": conf})

    avg_conf = sum(confianzas) / len(confianzas) if confianzas else 0.0
    return PaginaExtraida(
        numero=pagina_fitz.number + 1,
        texto="\n".join(texto_lineas),
        confianza=avg_conf,
        metodo="PADDLEOCR",
        bloques=bloques
    )

async def extraer_documento_completo(ruta_pdf: Path, analisis: PDFAnalysis) -> dict:
    """Pipeline principal: detección → extracción adaptativa → resultado."""
    doc = fitz.open(ruta_pdf)
    paginas_resultado = []

    for page in doc:
        texto_directo = page.get_text("text").strip()
        if len(texto_directo) > 50:
            paginas_resultado.append(extraer_pagina_digital(page))
        else:
            paginas_resultado.append(extraer_pagina_ocr(page))

    texto_total = "\n\n[PAGINA {}]\n".join(
        p.texto for p in paginas_resultado
    )
    confianza_promedio = sum(p.confianza for p in paginas_resultado) / len(paginas_resultado)

    return {
        "texto_completo": texto_total,
        "confianza_promedio": round(confianza_promedio, 4),
        "num_paginas": len(paginas_resultado),
        "paginas": [vars(p) for p in paginas_resultado],
        "requirio_ocr": analisis.requiere_ocr
    }
L.3 · Extractor NLP de campos del TDR (Pipeline híbrido)# services/nlp/extractor_tdr.py
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import Optional

# ── STEP 1: Extracción determinística con regex ──────────────────────────
PATRONES_REGEX = {
    "ruc_contratista": re.compile(r'\b(10|15|17|20)\d{9}\b'),
    "valor_referencial": re.compile(r'S/[.\s]?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    "plazo_dias": re.compile(r'(\d+)\s*(?:días?\s*calendario|días?\s*hábiles)', re.IGNORECASE),
    "numero_expediente": re.compile(r'(?:expediente|exp\.?)[:\s#]*([A-Z0-9\-/]+)', re.IGNORECASE),
}

def extraer_campos_deterministicos(texto: str) -> dict:
    resultados = {}
    for campo, patron in PATRONES_REGEX.items():
        match = patron.search(texto)
        if match:
            valor = match.group(1) if match.lastindex else match.group(0)
            resultados[campo] = {
                "valor": valor.strip(),
                "confianza": 0.98,
                "metodo": "REGEX",
                "posicion_char": match.start()
            }
    return resultados

# ── STEP 2: Extracción LLM para campos de texto libre ───────────────────
class CamposTDR(BaseModel):
    objeto_convocatoria: Optional[str] = Field(None, description="Objeto o descripción de la contratación")
    especificaciones_tecnicas: Optional[str] = Field(None, description="Especificaciones o requisitos técnicos")
    forma_de_pago: Optional[str] = Field(None, description="Modalidad de pago descrita")
    entregables: Optional[list] = Field(None, description="Lista de entregables o productos a entregar")
    lugar_ejecucion: Optional[str] = Field(None, description="Lugar donde se ejecutará el servicio/obra")
    perfil_proveedor: Optional[str] = Field(None, description="Requisitos del proveedor")
    tipo_proceso_sugerido: Optional[str] = Field(None, description="Tipo de proceso inferido: AS, ADS, LP, CP, MC")
    paginas_referencia: Optional[list] = Field(None, description="Números de página donde se encontró la información")

llm = ChatOllama(model="qwen2.5:7b", temperature=0, format="json")
parser = JsonOutputParser(pydantic_object=CamposTDR)

PROMPT_EXTRACCION_TDR = ChatPromptTemplate.from_messages([
    ("system", """Eres un especialista en contrataciones públicas del Perú (Ley 30225 y RLCE).
Tu tarea es extraer información estructurada de un Término de Referencia (TDR).
Responde ÚNICAMENTE con un JSON válido con la estructura indicada.
NO inventes información. Si no encuentras el dato, usa null.
Incluye el número de página donde encontraste cada dato principal."""),
    ("human", """Extrae los campos del siguiente TDR:

TEXTO DEL TDR:
{texto_tdr}

CAMPOS A EXTRAER:
{format_instructions}

IMPORTANTE:
- Para valor_referencial y plazo_dias, confirma o deja null si no encuentras (serán extraídos por regex separado)
- Para entregables, devuelve una lista de strings con cada entregable
- paginas_referencia debe ser una lista de enteros""")
])

chain = PROMPT_EXTRACCION_TDR | llm | parser

async def extraer_campos_llm(texto_tdr: str) -> dict:
    try:
        resultado = await chain.ainvoke({
            "texto_tdr": texto_tdr[:8000],  # limitar context window
            "format_instructions": parser.get_format_instructions()
        })
        return {k: {"valor": v, "confianza": 0.82, "metodo": "LLM"}
                for k, v in resultado.items() if v is not None}
    except Exception as e:
        return {"error_llm": str(e)}

# ── STEP 3: Merge y resolución de conflictos ────────────────────────────
def merge_extracciones(regex_fields: dict, llm_fields: dict) -> dict:
    """Regex tiene prioridad sobre LLM para campos formateados."""
    merged = {**llm_fields, **regex_fields}
    for campo, data in merged.items():
        if isinstance(data, dict) and data.get("confianza", 1) < 0.75:
            data["requiere_revision"] = True
            data["motivo_revision"] = f"Confianza baja: {data['confianza']:.0%}"
    return merged
M. Diseño de API REST (FastAPI)M.1 · Endpoints del Asistente de BasesGET /api/v1/siged/expediente/{numero_expediente}Descripción: Consulta de expediente en SIGED y retorna metadatos más lista de documentos disponibles. Cacheado en Redis por 15 minutos.POST /api/v1/procesos/bases/iniciarDescripción: Inicia proceso de generación de Bases. Payload: {"expediente_id", "numero_siged"}. Retorna proceso_id para seguimiento.POST /api/v1/documentos/{doc_id}/procesar-ocrDescripción: Dispara tarea Celery de OCR/NLP asíncrono. Retorna task_id para polling de estado.GET /api/v1/tareas/{task_id}/statusDescripción: Retorna el estado actual de la tarea asíncrona: {"status": "PENDING|PROCESSING|SUCCESS|FAILURE", "progress": 65, "result": {...}}.GET /api/v1/procesos/{proceso_id}/campos-extraidosDescripción: Devuelve todos los campos extraídos del TDR con sus valores, confianzas, fuentes y banderas de revisión.PUT /api/v1/procesos/{proceso_id}/campos-extraidosDescripción: Guarda las correcciones del analista a los campos extraídos. Registra en la tabla de auditoría el cambio (valor original y el nuevo).POST /api/v1/procesos/{proceso_id}/datos-administrativosDescripción: Guarda los campos ingresados manualmente por el usuario (comité, fechas del proceso, etc.).POST /api/v1/procesos/{proceso_id}/generar-borradorDescripción: Renderiza la plantilla .docx. Guarda el archivo en MinIO y retorna la URL firmada para previsualización. Estado en base de datos: BORRADOR.GET /api/v1/documentos-generados/{doc_id}/descargarDescripción: Genera una URL pre-firmada de MinIO (TTL de 5 minutos) para la descarga segura del archivo generado. Registra el evento en auditoría.POST /api/v1/documentos-generados/{doc_id}/revisarDescripción: Dictamen de aprobación, observación o rechazo de un revisor. Payload: {"decision": "APROBADO|OBSERVADO|RECHAZADO", "comentarios": "...", "observaciones_detalle": [...]}.M.2 · Estructura de respuesta estándar// Todas las respuestas exitosas siguen este envelope
{
  "success": true,
  "data": {
    "proceso_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "estado": "INICIADO"
  },
  "meta": {
    "timestamp": "2026-06-15T10:23:45.123Z",
    "request_id": "c62f275e-85e6-4903-8d69-cb181e18d69a",
    "version": "1.0.0"
  }
}

// Estructura en caso de error
{
  "success": false,
  "error": {
    "code": "OCR_CONFIDENCE_TOO_LOW",
    "message": "La confianza promedio del OCR es inferior al umbral mínimo del 65%",
    "details": { "confianza_obtenida": 0.42, "umbral": 0.65 },
    "campo_afectado": "valor_referencial"
  }
}
M.3 · Autenticación y middleware de seguridad# middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

KEYCLOAK_JWKS_URL = "http://keycloak:8080/realms/ia-documental/protocol/openid-connect/certs"
ALGORITHM = "RS256"
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        jwks = await get_jwks_cached()
        payload = jwt.decode(
            credentials.credentials,
            jwks,
            algorithms=[ALGORITHM],
            audience="ia-documental-api"
        )
        await registrar_acceso_api(
            usuario_id=payload["sub"],
            endpoint="...",  # Inyectado dinámicamente por middleware
            ip="..."
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def require_roles(*roles: str):
    async def checker(user: dict = Depends(get_current_user)):
        user_roles = user.get("realm_access", {}).get("roles", [])
        if not any(r in user_roles for r in roles):
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return user
    return checker
N. Prompts LLM EspecializadosN.1 · Prompt de extracción de TDR (Sistema de Bases)SYSTEM:
Eres un especialista senior en contrataciones públicas del Perú con 15 años de experiencia en la aplicación de la Ley 30225 y su Reglamento (RLCE DS-344-2018-EF). Tu función es extraer información estructurada de documentos de Términos de Referencia (TDR) o Especificaciones Técnicas.

REGLAS ESTRICTAS:
1. NUNCA inventes o infieras información que no esté explícitamente en el texto.
2. Si un campo no se encuentra, devuelve null para ese campo.
3. Siempre indica la página o sección donde encontraste el dato.
4. Para montos, mantén el valor exacto como aparece en el texto (no redondees).
5. Responde ÚNICAMENTE con JSON válido. Sin texto adicional, sin markdown.

USER:
Analiza el siguiente TDR y extrae los campos especificados.

TEXTO DEL TDR (páginas 1-{num_paginas}):
---
{texto_tdr}
---

Extrae y devuelve este JSON:
{
 "objeto_convocatoria": "descripción completa del objeto | null",
 "tipo_proceso_sugerido": "AS|ADS|LP|CP|MC|SIE | null",
 "especificaciones_tecnicas": "texto completo de especificaciones | null",
 "lugar_prestacion": "lugar de ejecución | null",
 "forma_pago": "descripción de forma de pago | null",
 "entregables": ["entregable 1", "entregable 2"] o null,
 "perfil_proveedor": "requisitos del proveedor | null",
 "supervision_responsable": "nombre del responsable de supervisión | null",
 "penalidades": "descripción de penalidades | null",
 "confidencialidad": "menciona confidencialidad? true/false | null",
 "paginas_referencia": {"objeto": [1,2], "especificaciones": [3,4,5]}
}
N.2 · Prompt de validación de consistencia para ContratosSYSTEM:
Eres un validador de consistencia para contratos de contrataciones públicas peruanas. Tu función es comparar datos extraídos de múltiples documentos y detectar inconsistencias que deben resolverse antes de generar el contrato.

USER:
Compara los siguientes datos extraídos de diferentes documentos del proceso y detecta inconsistencias:

DATOS EXTRAÍDOS DE BASES INTEGRADAS:
{datos_bases_integradas}

DATOS EXTRAÍDOS DE OFERTA ECONÓMICA:
{datos_oferta_economica}

DATOS EXTRAÍDOS DE OFERTA TÉCNICA:
{datos_oferta_tecnica}

DATOS EXTRAÍDOS DE VIGENCIA DE PODER:
{datos_vigencia_poder}

Devuelve JSON con esta estructura:
{
 "inconsistencias": [
  {
   "campo": "nombre del campo",
   "gravedad": "CRITICA|ALTA|MEDIA|BAJA",
   "descripcion": "descripción clara de la inconsistencia",
   "valor_en_bases": "...",
   "valor_en_oferta": "...",
   "accion_sugerida": "qué debe hacer el revisor"
  }
 ],
 "es_consistente": true o false,
 "campos_validados": ["lista de campos validados sin inconsistencias"],
 "resumen": "resumen ejecutivo de 2-3 oraciones para el revisor"
}

CAMPOS CRÍTICOS a comparar: monto_total, plazo_ejecucion_dias, objeto_contrato, nombre_contratista, representante_legal, ruc_contratista.
Una inconsistencia en monto o representante legal es siempre CRÍTICA.
N.3 · Prompt para generación de cláusulas condicionalesSYSTEM:
Eres un asistente para generación de cláusulas contractuales en el marco de la Ley 30225 del Perú. Solo puedes usar las cláusulas y textos que están en la base de conocimiento proporcionada. NO generes cláusulas nuevas ni modifiques el texto legal aprobado.

USER:
Con base en los datos del proceso y las cláusulas disponibles en el RAG, selecciona y adapta las cláusulas de garantía apropiadas para:

- Tipo de proceso: {tipo_proceso}
- Monto del contrato: {monto_contrato}
- Tipo de garantía requerida: {tipo_garantia}
- Modalidad: {modalidad}

CLÁUSULAS DISPONIBLES EN RAG:
{contexto_rag}

Devuelve JSON: {"clausula_garantia": "texto exacto de la cláusula", "fuente_rag": "nombre del documento fuente", "requiere_adaptacion": false}

Si no encuentras cláusula apropiada en el RAG, devuelve: {"clausula_garantia": null, "motivo": "No se encontró cláusula para los parámetros indicados", "requiere_revision_legal": true}
O. Motor de Plantillas docxtpl — ImplementaciónO.1 · Estructura de la plantilla .docxLas plantillas se definen en MS Word utilizando marcadores con sintaxis compatible con Jinja2, facilitando el mantenimiento a los usuarios del negocio.{# Campo simple #}
{{ objeto_convocatoria }}

{# Bloque condicional en el documento #}
{% if tipo_proceso == "LP" %}
LICITACIÓN PÚBLICA N° {{ numero_proceso }}-{{ anio }}-{{ entidad }}
{% elif tipo_proceso == "AS" %}
ADJUDICACIÓN SIMPLIFICADA N° {{ numero_proceso }}-{{ anio }}-{{ entidad }}
{% endif %}

{# Tabla dinámica iteradora para entregables #}
{% for entregable in entregables %}
| {{ loop.index }} | {{ entregable.descripcion }} | {{ entregable.plazo_dias }} días |
{% endfor %}

{# Formateo numérico y conversión a letras #}
S/ {{ "{:,.2f}".format(valor_referencial) }} ({{ valor_referencial_letras }})
O.2 · Servicio de generación de documentos# services/documentos/generador.py
from docxtpl import DocxTemplate
from pathlib import Path
from datetime import datetime
import hashlib, io, uuid
from num2words import num2words
from services.storage import MinioClient

def monto_a_letras(monto: float) -> str:
    """S/ 125,000.00 → 'CIENTO VEINTICINCO MIL Y 00/100 SOLES'"""
    entero = int(monto)
    decimales = round((monto - entero) * 100)
    letras = num2words(entero, lang='es').upper()
    return f"{letras} Y {decimales:02d}/100 SOLES"

async def generar_documento_bases(
    proceso_id: str,
    codigo_plantilla: str,
    campos_extraidos: dict,
    datos_administrativos: dict,
    es_final: bool = False
) -> dict:

    # 1. Obtener plantilla desde MinIO
    plantilla_bytes = await MinioClient.get(
        bucket="plantillas",
        key=f"bases/{codigo_plantilla}.docx"
    )
    tpl = DocxTemplate(io.BytesIO(plantilla_bytes))

    # 2. Preparar contexto (merge campos extraídos + administrativos)
    monto = float(campos_extraidos.get("valor_referencial", {}).get("valor", 0))
    context = {
        **{k: v["valor"] for k, v in campos_extraidos.items()},
        **datos_administrativos,
        # Campos calculados dinámicamente
        "valor_referencial_letras": monto_a_letras(monto),
        "fecha_generacion": datetime.now().strftime("%d de %B de %Y"),
        "proceso_id": proceso_id,
        "marca_agua": "" if es_final else "BORRADOR - SUJETO A REVISIÓN",
    }

    # 3. Renderizar plantilla
    tpl.render(context, autoescape=True)

    # 4. Modificar metadatos nativos del archivo Word
    core_props = tpl.docx.core_properties
    core_props.title = f"Bases Estándar - Exp. {datos_administrativos.get('numero_expediente')}"
    core_props.author = datos_administrativos.get("usuario_nombre", "Sistema IA")
    core_props.description = f"Proceso ID: {proceso_id} | Generado: {datetime.utcnow().isoformat()}"
    core_props.keywords = f"bases,{codigo_plantilla},{proceso_id}"

    # 5. Serializar archivo y calcular hash de integridad
    output = io.BytesIO()
    tpl.save(output)
    doc_bytes = output.getvalue()
    doc_hash = hashlib.sha256(doc_bytes).hexdigest()

    # 6. Guardar archivo final en MinIO
    version = await get_next_version(proceso_id)
    estado = "final" if es_final else "borrador"
    storage_key = f"documentos-generados/{proceso_id}/v{version}_{estado}.docx"
    await MinioClient.put(
        bucket="documentos-generados",
        key=storage_key,
        data=doc_bytes,
        metadata={"proceso_id": proceso_id, "version": str(version), "hash": doc_hash}
    )

    return {
        "storage_key": storage_key,
        "hash_sha256": doc_hash,
        "tamano_bytes": len(doc_bytes),
        "version": version,
        "tiene_marca_agua": not es_final
    }
P. Motor de Validación — ContratosP.1 · Reglas de validación determinísticas# services/validacion/reglas_contratos.py
from dataclasses import dataclass
from typing import List
from enum import Enum
import re

class Gravedad(Enum):
    CRITICA = "CRITICA"
    ALTA = "ALTA"
    MEDIA = "MEDIA"

@dataclass
class ResultadoValidacion:
    campo: str
    gravedad: Gravedad
    descripcion: str
    valor_encontrado: str
    valor_esperado: str

class ValidadorContratos:

    def validar_ruc(self, ruc: str) -> List[ResultadoValidacion]:
        errores = []
        if not re.fullmatch(r'\d{11}', ruc):
            errores.append(ResultadoValidacion(
                campo="ruc_contratista", gravedad=Gravedad.CRITICA,
                descripcion="El RUC debe tener exactamente 11 dígitos numéricos",
                valor_encontrado=ruc, valor_esperado="11 dígitos numéricos"
            ))
        elif not self._verificar_digito_ruc(ruc):
            errores.append(ResultadoValidacion(
                campo="ruc_contratista", gravedad=Gravedad.CRITICA,
                descripcion="El RUC no supera la verificación del dígito de control",
                valor_encontrado=ruc, valor_esperado="RUC válido con dígito de control correcto"
            ))
        return errores

    def validar_consistencia_montos(
        self,
        monto_bases: float,
        monto_oferta: float,
        monto_contrato: float,
        tolerancia_pct: float = 0.01  # 1% de tolerancia por redondeo
    ) -> List[ResultadoValidacion]:
        errores = []
        diff_oferta_bases = abs(monto_oferta - monto_bases) / monto_bases
        if diff_oferta_bases > tolerancia_pct:
            errores.append(ResultadoValidacion(
                campo="monto", gravedad=Gravedad.CRITICA,
                descripcion=f"Monto de la oferta difiere del valor referencial en {diff_oferta_bases:.1%}",
                valor_encontrado=f"S/ {monto_oferta:,.2f}",
                valor_esperado=f"S/ {monto_bases:,.2f} (±{tolerancia_pct:.0%})"
            ))

        if abs(monto_contrato - monto_oferta) > 1.0:  # diferencia máxima de S/ 1.00
            errores.append(ResultadoValidacion(
                campo="monto", gravedad=Gravedad.CRITICA,
                descripcion="El monto del contrato debe ser idéntico al monto de la oferta ganadora",
                valor_encontrado=f"S/ {monto_contrato:,.2f}",
                valor_esperado=f"S/ {monto_oferta:,.2f}"
            ))
        return errores

    def validar_representante_legal(
        self,
        rep_vigencia_poder: str,
        rep_oferta: str,
        rep_contrato: str
    ) -> List[ResultadoValidacion]:
        errores = []
        def normalizar(s): return s.upper().strip()
        if normalizar(rep_vigencia_poder) != normalizar(rep_oferta):
            errores.append(ResultadoValidacion(
                campo="representante_legal", gravedad=Gravedad.CRITICA,
                descripcion="El representante legal registrado en Vigencia de Poder difiere del firmante en la Oferta",
                valor_encontrado=rep_oferta,
                valor_esperado=f"Debe coincidir con: {rep_vigencia_poder}"
            ))
        return errores

    def _verificar_digito_ruc(self, ruc: str) -> bool:
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(d) * f for d, f in zip(ruc[:10], factores))
        resto = suma % 11
        dig_control = 11 - resto if resto > 1 else resto
        return str(dig_control) == ruc[10]
P.2 · Flujo de validación completo para Contratos[Paso 1: Clasificación de Documentos]
  └─ El sistema recibe y categoriza documentos mediante metadatos y LLM.
         │
         ▼
[Paso 2: Procesamiento OCR / NLP en Paralelo]
  └─ Tareas Celery por documento extraen campos mediante OCR adaptativo y regex/LLM.
         │
         ▼
[Paso 3: Validación Determinística de Negocio]
  └─ Verificación estricta de formatos (RUC verificador, plazos positivos).
         │
         ▼
[Paso 4: Validación Cruzada de Coherencia]
  └─ Comparación cruzada de variables críticas (monto_oferta vs bases_referencial).
         │
         ▼
[Paso 5: Validación de Consistencia Semántica]
  └─ El LLM evalúa similitudes de alcance narrativo (Objeto Bases vs Oferta Técnica).
         │
         ▼
[Paso 6: Sincronización Externa de Datos]
  └─ Consulta externa online con SUNAT para validar estado de RUC activo/habido.
         │
         ▼
[Paso 7: Panel de Mitigación y Confirmación]
  └─ Interfaz de usuario donde el analista mitiga o justifica observaciones.
         │
         ▼
[Paso 8: Firma de Aprobación en Cadena]
  └─ Cadena de aprobación jerárquica para generar y liberar el documento final.
Q. Arquitectura de Seguridad DetalladaQ.1 · Flujo de autenticación con KeycloakEl usuario accede a la aplicación web -> Redirigido a Keycloak para autenticación.Keycloak valida contra la base Active Directory institucional (LDAP/AD).De requerirse, se solicita segundo factor (MFA vía TOTP).Keycloak emite Access Token (JWT firmado, expira en 15 minutos) y un Refresh Token (8 horas).El cliente web almacena los tokens únicamente en memoria volátil (nunca en localStorage).Cada llamado de API envía la cabecera Authorization: Bearer {token}.FastAPI valida de manera local utilizando las claves públicas (JWKS) expuestas por Keycloak (con caché en Redis por 10 minutos).// Estructura de Payload JWT emitido por Keycloak
{
  "sub": "2f4e4271-8be2-447a-8b1e-05a8f949c81a",
  "email": "analista.compras@entidad.gob.pe",
  "name": "Juan Pérez López",
  "realm_access": {
    "roles": ["ANALISTA", "offline_access"]
  },
  "resource_access": {
    "ia-documental-api": {
      "roles": ["ANALISTA"]
    }
  },
  "iat": 1718000000,
  "exp": 1718000900,
  "iss": "http://keycloak:8080/realms/ia-documental"
}
Q.2 · Control de acceso basado en roles (RBAC)RolPermisos HabilitadosLimitaciones / RestriccionesANALISTAIniciar flujos, subir documentos, corregir campos extraídos, generar borradores.No puede dictaminar aprobaciones, alterar plantillas o modificar el registro de auditoría.REVISOR_TECNICOPermisos de analista + validar, observar o aprobar documentos en etapa técnica.No puede aprobar dictámenes legales.REVISOR_LEGALAcceso a auditorías de procesos, revisar y aprobar dictámenes legales.No puede iniciar nuevos expedientes de bases.JEFATURAAprobación en última instancia, generación del documento final sin marca de agua.No realiza correcciones manuales de variables.ADMINGestión de usuarios, asignación de roles, carga y versionado de plantillas base.Restricciones de negocio estándar de analista.AUDITORAcceso de solo lectura de auditoría (logs inmutables), reportes del sistema.Bloqueado para cualquier acción de escritura o modificación.Q.3 · Gestión de secretos con HashiCorp Vaultsecret/
  ia-documental/
    database/               # Credenciales PostgreSQL (rotación automática)
      host, port, dbname, username, password
    minio/                  # Access key y Secret key de MinIO
      access_key, secret_key
    siged/                  # API Key y base URL del SIGED
      api_key, base_url
    keycloak/               # Parámetros del cliente Keycloak
      client_id, client_secret
# Ejemplo de lectura de credenciales de DB seguras al inicio de FastAPI
from hvac import Client as VaultClient

vault = VaultClient(url="http://vault:8200", token="${VAULT_TOKEN}")

def get_secret(path: str) -> dict:
    return vault.secrets.kv.v2.read_secret_version(path=path)["data"]["data"]

db_secret = get_secret("ia-documental/database")
DATABASE_URL = f"postgresql://{db_secret['username']}:{db_secret['password']}@host:port/dbname"
Q.4 · Checklist de seguridad por capaCapaControl Técnico ImplementadoHerramientaEstado MVPRedProtocolo de cifrado TLS 1.3 en canales de comunicación.NGINX + Let's Encrypt✅ ObligatorioRedPuertos de acceso restringidos (únicamente 80 y 443 expuestos).iptables / firewalld✅ ObligatorioRedRed interna privada aislada para backend y bases de datos.Docker Network aisladas✅ ObligatorioAPIImplementación de Rate Limiting por endpoint y cliente.Kong API Gateway✅ ObligatorioAPIValidación estricta del esquema de entrada y deserialización.Pydantic v2✅ ObligatorioAuthMulti-Factor Authentication (MFA) para perfiles de jefatura.Keycloak TOTP✅ ObligatorioDatosCifrado de objetos en reposo en almacén de archivos.MinIO SSE (AES-256)✅ ObligatorioDatosHashing de documentos finales para control de alteración.SHA-256 Python✅ ObligatorioSecretosProhibición de almacenamiento de secretos en repositorios.HashiCorp Vault / GitLeaks✅ ObligatorioCódigoEscaneo de vulnerabilidades y dependencias en tuberías CI.pip-audit / Bandit✅ ObligatorioLogsAuditoría histórica inmutable a nivel de base de datos.Triggers PostgreSQL✅ ObligatorioR. Estimación de Costos (Contexto Perú)R.1 · Escenario A: Infraestructura Física On-Premise (Recomendado)Inversión Inicial (CapEx) — Hardware FísicoServidor de Aplicación (Backend + DB + MinIO): Dual CPU Intel Xeon, 64GB RAM, SSD 2TB NVMe -> S/ 23,000.00Servidor de Procesamiento GPU (Ollama + OCR): Intel Core i9, 64GB RAM, NVIDIA RTX 4090 (24GB VRAM) -> S/ 28,000.00Switching y Redes (Switch Gestionado 10G): S/ 4,500.00Sistema de Energía Ininterrumpida (UPS 3KVA): S/ 6,000.00TOTAL Inversión CapEx Estimado: S/ 61,500.00 (Pago único de adquisición)Gastos Operativos Recurrentes (OpEx)Consumo Eléctrico de Servidores (~800W continuos): S/ 340.00 / mesSoporte y Mantenimiento de Hardware (1.5% CapEx anual): S/ 920.00 / mesSoporte Administrador de Sistemas (DevOps / SysAdmin): S/ 4,000.00 / mesTOTAL Recurrente Mensual Estimado OpEx: S/ 5,260.00 / mesR.2 · Escenario B: Nube Híbrida AWS / Azure (Alternativo)Categoría de ServicioAWS (USD/mes)Azure (USD/mes)ComentariosServicio de Cómputo$180.00 (ECS Fargate)$190.00 (Container Apps)Auto-scaling activoBase de Datos$120.00 (RDS PostgreSQL)$130.00 (Azure DB Postgres)Multi-AZ activoObject Storage$15.00 (S3 Standard 500GB)$14.00 (Blob Storage Hot)Cifrado KMS incluidoOCR Inteligente$110.00 (Textract)$110.00 (Doc Intelligence)Estimado 1,000 docs/mesModelos de Inferencia LLM$350.00 (Bedrock Claude)$350.00 (Azure OpenAI)Depende de tokens de entradaCaché y Mensajería$25.00 (ElastiCache Redis)$25.00 (Cache for Redis)Micro-instanceTOTAL Cloud Mensual (USD)$800.00$819.00TOTAL Cloud Mensual (S/)S/ 3,000.00S/ 3,071.25(Tipo de cambio S/ 3.75)💡 Análisis simplificado de Retorno de Inversión (ROI):Suponiendo que la entidad emite 40 expedientes mensuales y la estructuración manual de las bases toma un promedio de 4 horas por proceso, la automatización reduce este tiempo a un máximo de 45 minutos. Representa un ahorro directo de 130 horas de analistas al mes. Con un costo de personal especializado estimado en S/ 40.00/hora, la eficiencia generada se traduce en un ahorro interno de S/ 5,200.00 mensuales, amortizando la inversión total del servidor en un promedio de 12 meses.S. Métricas de Éxito y KPIsS.1 · KPIs de Calidad del Sistema[Precisión Extracción Campos Críticos]  ──────>  Meta: ≥ 95.0%
[Tasa de Procesos que van a Revisión]  ──────>  Meta: ≤ 5.0%
[Latencia Media OCR + NLP (20 páginas)] ──────>  Meta: ≤ 120 segundos
[Uptime Operativo de Infraestructura]  ──────>  Meta: ≥ 99.5%
[Contratos Emitidos con Error Humano]  ──────>  Meta: Absoluta de 0
S.2 · KPIs Funcionales de NegocioIndicador clave (KPI)Estado Base (Proceso Manual)Meta MVPMeta ProducciónTiempo de Elaboración de Bases3.5 horas por proceso2.0 horas< 45 minutosTiempo de Elaboración de Contrato3.0 horas por proceso1.5 horas< 60 minutosTasa de Error de Escritura ManualEstimado 8% a 12%< 2%< 0.5%Porcentaje de Adopción InternaN/A70%> 90%Nivel de Satisfacción de Usuario (1-5)N/A> 3.8> 4.5S.3 · Dashboard de Monitoreoreo Recomendado (Grafana)Panel de Pipeline: Volúmenes de procesamiento concurrente, latencia de render docxtpl, porcentaje de tareas fallidas en la cola de Celery.Panel de Calidad OCR: Confianza analítica promedio detectada, conteo de caracteres procesados por segundo, tasa de fallas en binarización de imagen.Panel de Seguridad de Datos: Alertas ante intentos de login fallidos, tasa de transferencia saliente anómala de documentos, logs del trigger inmutable de base de datos.T. Plan de PruebasT.1 · Tipos de prueba por faseClasificación de PruebaHerramientaCobertura / Criterio de AceptaciónEjecución AutomatizadaUnitarias (Backend)pytest + mockCobertura de código superior al 80%✅ En tubería CI/CDIntegración de APIpytest + httpxValidación completa de endpoints✅ En tubería CI/CDPrecisión OCRDataset TDR de controlPrecisión de localización de bounding boxes > 90%✅ Ejecución periódicaCalidad de Extracción LLMRagas EvaluationF1-Score semántico superior al 85%⚠️ Manual por sprintsFormatos de Salida .docxdocxtpl-testsEstructuras complejas renderizadas sin distorsión✅ Scripts de controlSeguridad de AplicaciónOWASP ZAPCero vulnerabilidades críticas o altas✅ Automatizado en CDPrueba de CargaLocustSimulación de 30 usuarios concurrentes sin degradación⚠️ Previo a despliegueT.2 · Dataset de prueba para OCR/NLPEl dataset de validación inicial debe estar compuesto por un mínimo de 100 expedientes reales históricos que sirvan como muestra de control (Ground Truth):30 TDRs de Adquisición de Bienes (formato digital nativo).30 TDRs de Contratación de Servicios (mixto: páginas escaneadas y digitales).30 Contratos históricos (física digitalizada de baja calidad).10 Documentos complejos que presenten tablas con bordes distorsionados o notas marginales.U. Checklist de Implementación por FaseU.1 · Fase 1 — MVP Asistente de Bases (Semanas 1-20)[Semanas 1-4: Infraestructura Base]
  ├── Instalar Docker, Docker Compose y configurar redes internas.
  ├── Desplegar Keycloak e integrarlo con el Active Directory corporativo.
  ├── Instalar PostgreSQL 16 y habilitar extensiones pgvector y pgcrypto.
  ├── Configurar MinIO, crear buckets cifrados y activar versionado.
  └── Levantar Ollama de forma local con el modelo Qwen2.5:7b.

[Semanas 5-8: Sincronización e Ingesta OCR]
  ├── Implementar llamadas HTTP seguras al API del SIGED.
  ├── Desarrollar el detector de tipo de archivo PDF.
  ├── Configurar la tarea Celery asíncrona para el pipeline de PaddleOCR.
  └── Diseñar el esquema persistente de campos extraídos en base de datos.

[Semanas 9-13: Extracción NLP y Generación Word]
  ├── Desarrollar la lógica de filtros regex determinísticos.
  ├── Refinar el prompt y estructurar la salida JSON del LLM para el TDR.
  ├── Cargar plantillas estándar de bases en MinIO.
  └── Programar la rutina docxtpl para renderizar y firmar el archivo temporal.

[Semanas 14-17: Capa Frontend e Interfaces]
  ├── Desarrollar pantallas funcionales en Next.js.
  ├── Implementar previsualizador nativo de Word mediante mammoth.js.
  ├── Desarrollar el panel interactivo de corrección de campos.
  └── Configurar el workflow de aprobación del borrador de bases.

[Semanas 18-20: Cierre MVP, Auditoría y Go-Live]
  ├── Habilitar el trigger inmutable de la tabla de auditoría.
  ├── Validar la matriz RBAC de roles de usuarios.
  ├── Desplegar dashboards de monitoreo en Grafana.
  ├── Ejecutar pruebas de aceptación de usuario (UAT) con 10 expedientes reales.
  └── Desplegar en producción el MVP y capacitar a los analistas de la OEC.
V. Glosario Técnico y ReferenciasV.1 · GlosarioSIGED: Sistema de Gestión Documental. Repositorio transaccional del Estado.TDR: Términos de Referencia. Especificaciones contractuales del servicio a contratar.OSCE: Organismo Supervisor de las Contrataciones del Estado (Perú). Ente regulador.RLCE: Reglamento de la Ley de Contrataciones del Estado (Decreto Supremo N° 344-2018-EF).RAG: Retrieval-Augmented Generation. Técnica para enriquecer el contexto del LLM con datos externos recuperados semánticamente de un almacén vectorial.Bboxes: Bounding Boxes. Coordenadas delimitadoras bidimensionales de un segmento de texto en un plano de documento.V.2 · Referencias Técnicas ClaveOSCE Perú - Directivas y Bases Estándar Oficiales: portal.osce.gob.peDocumentación oficial de PaddleOCR: github.com/PaddlePaddle/PaddleOCRFramework LangChain: python.langchain.comLibrería de plantillas docxtpl: docxtpl.readthedocs.ioGuías de Privacidad de Datos de Inferencia de OpenAI Enterprise: openai.com/enterprise-privacy