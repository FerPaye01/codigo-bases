# Revisión de Especificación de Requerimientos y Análisis Funcional (Actualizado)

Este documento  realiza un análisis de brechas (gap analysis) comparando los requisitos especificados con la implementación en el codebase.

> [!NOTE]
> Las brechas técnicas identificadas en la revisión inicial (trazabilidad, multi-plantillas y campos del Word) han sido resueltas e integradas al 100% en el MVP actual.

---

## 1. Matriz de Requisitos vs. Estado de Implementación

A continuación se presenta la correspondencia de los requisitos funcionales (RF) y no funcionales (RNF) especificados en el documento con el estado en el sistema (Streamlit + FastAPI + SQLite/Qdrant + Ollama/Docling):

| Código | Requisito / Funcionalidad | Estado | Implementación Actual | ¿Qué falta para Producción? |
| :--- | :--- | :--- | :--- | :--- |
| **RF-1** | **Identificación y Clasificación del TDR / Consulta SIGED** | **Completo (MVP)** | Interfaz en [app.py](file:///data/proyectos/proyecto-bases/app.py) simula consulta por ID de 11 dígitos contra Mock en memoria. Además, permite subir archivos TDR locales y procesarlos con Docling local para clasificar (Bienes, Servicios, Consultorías). | El adaptador en `api.py` está en modo mock/simulado. Para producción, requiere la implementación del `SIGEDAdapter` real (API REST/SOAP o RPA con Playwright). |
| **RF-2** | **Generación de Borrador basada en 6 Plantillas Estándar** | **Completo** | Interfaz permite seleccionar las 6 variantes (Bienes/Servicios/Consultorías en Normal/Abreviado). El backend `/generate_docx` mapea la selección a los 6 archivos físicos generados: `plantilla_bienes_normal.docx`, `plantilla_bienes_abreviado.docx`, etc. | Integrar las plantillas oficiales finales con los logos de Osinergmin cuando el área legal las proporcione. |
| **RF-3** | **Extracción de Datos Técnicos del TDR (OCR/NLP)** | **Completo** | Implementado mediante `docling` para Layout OCR y el modelo local `gemma3:1b` en `/extract` y `/extract_file`. Extrae y mapea: objeto, plazo, valor estimado, sistema de contratación, requerimiento completo, requisitos de calificación y factores de evaluación. | Ajustes de temperatura o prompts del LLM según la estructura particular de nuevos TDRs. |
| **RF-4** | **Ingreso de Datos Administrativos** | **Completo** | Formulario multipaso en Streamlit que captura Nomenclatura, Valor Estimado, Unidad Solicitante, Responsable, Fechas del Cronograma y Fuente de Financiamiento. | Nada, el mapeo y flujo de captura de datos administrativos está completo y alineado con las interfaces del documento. |
| **RF-5** | **Salida, Previsualización y Descarga** | **Completo** | Visor lateral en Markdown de bases previsualizadas, historial persistente que recarga estados previos de expedientes y descarga en formato `.docx` dinámica. | Asegurar que la descarga histórica en la pantalla 6 utilice el mapeo de plantillas dinámico. |
| **RNF-1**| **Seguridad y Trazabilidad (Auditoría)** | **Completo** | Se ha integrado `database.log_audit_action(...)` en los endpoints principales de FastAPI (`/extract`, `/extract_file`, `/generate_docx` y `/recommend_clauses`). Cada acción del usuario se guarda con ID, acción, expediente, detalles y fecha. | Configurar el almacenamiento seguro y centralizado de la base de datos sqlite en un volumen Docker o migrar a Oracle Database en producción. |
| **RNF-2**| **Plataforma Tecnológica (AWS)** | **Mismatched (MVP local)**| El documento exige infraestructura de AWS (S3, Lambda, AWS NLP/OCR). La solución actual corre localmente (SQLite, Qdrant incrustado, Docling, Ollama) para evitar costos de pago en MVP. | El stack local es excelente para pruebas y desarrollo autónomo (CPU-first), pero se debe documentar que la transición a producción requerirá migrar los servicios a AWS Lambda/ECS/Bedrock. |
| **RNF-3**| **Interfaz en Español** | **Completo** | Toda la interfaz web en Streamlit, alertas y logs de flujo interactivos están redactados en español técnico de contrataciones del estado. | Nada. |
| **RNF-4**| **Persistencia** | **Completo** | El estado de elaboración de Bases se guarda en SQLite en las tablas `expedientes` y `procesos`. Permite reanudar cualquier expediente al ingresarlo de nuevo en la pantalla 1. | Nada. |

---

## 2. Gaps Resueltos e Integrados (Nuevas Funcionalidades)

### 1. Invocación de la Trazabilidad / Auditoría (RNF-1)
La función de auditoría `database.log_audit_action` se invoca en cada endpoint core de `api.py`.
* **Verificación:** Ejecutando pruebas unitarias de API, se validó que se inserta una fila en la tabla de auditoría por cada generación de documento, búsqueda de cláusulas similares o extracción de archivo, registrando el usuario solicitante e indicando los parámetros exactos.

### 2. Soporte Real para las 6 Plantillas Estándar (RF-2)
El sistema genera y resuelve dinámicamente las bases correspondientes a los 6 modelos oficiales de Osinergmin:
1. `plantilla_bienes_normal.docx` (Bases para la Adquisición de Bienes)
2. `plantilla_bienes_abreviado.docx` (Bases Simplificadas para la Adquisición de Bienes)
3. `plantilla_servicios_normal.docx` (Bases para la Contratación de Servicios en General)
4. `plantilla_servicios_abreviado.docx` (Bases Simplificadas para la Contratación de Servicios)
5. `plantilla_consultoria_normal.docx` (Bases para la Contratación de Servicios de Consultoría)
6. `plantilla_consultoria_abreviado.docx` (Bases Simplificadas para la Contratación de Servicios de Consultoría)
* **Verificación:** Al enviar un payload de generación con `"plantilla_usada": "Bienes - Normal"`, el backend lee y renderiza el archivo `plantilla_bienes_normal.docx` con la cabecera correspondiente de Osinergmin.

### 3. Integración de "Sistema de Contratación"
El TDR extrae el sistema de contratación (ej. "Suma Alzada" o "Precios Unitarios") y se mapea directamente en la tabla de Datos Generales del Word generado.
* **Verificación:** Validado mediante el script `test_api_new.py`. El Word resultante contiene la fila de "Sistema de Contratación" mapeada a la variable correspondiente en la tabla del Capítulo I.
