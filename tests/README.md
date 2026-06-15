# Pruebas de Integración y Funcionamiento - Asistente de Bases

Esta carpeta contiene los scripts de prueba utilizados para validar el funcionamiento del Asistente de Bases Estándar en su versión de desarrollo local.

## Descripción de los Scripts de Prueba

1. **[test_db.py](file:///data/proyectos/proyecto-bases/tests/test_db.py)**:
   * **Objetivo**: Validar la persistencia del estado en la base de datos relacional SQLite (`bases_osinergmin.db`).
   * **Valida**: Creación de esquemas de tablas, inserción y recuperación de metadatos de SIGED, estados técnicos extraídos e ingresos administrativos.

2. **[test_docling.py](file:///data/proyectos/proyecto-bases/tests/test_docling.py)**:
   * **Objetivo**: Probar de manera aislada el motor local de OCR e interpretación de layout (`IBM Docling`).
   * **Valida**: Conversión de PDFs u otros archivos a formato Markdown estructurado en la máquina local.

3. **[test_docx.py](file:///data/proyectos/proyecto-bases/tests/test_docx.py)**:
   * **Objetivo**: Comprobar el funcionamiento del motor de plantillas `docxtpl` (`python-docx`).
   * **Valida**: Reemplazo de etiquetas dinámicas (sintaxis tipo Jinja2) en un archivo `.docx` de prueba.

4. **[test_extract_file.py](file:///data/proyectos/proyecto-bases/tests/test_extract_file.py)**:
   * **Objetivo**: Probar el endpoint `/extract_file` de la API de FastAPI.
   * **Valida**: Recepción de un archivo binario mediante HTTP POST, ejecución del OCR, envío del Markdown al LLM local (Gemma 3) y entrega de un JSON estructurado.

5. **[test_recommend.py](file:///data/proyectos/proyecto-bases/tests/test_recommend.py)**:
   * **Objetivo**: Comprobar la base de datos vectorial local `Qdrant` y el endpoint `/recommend_clauses`.
   * **Valida**: Búsqueda semántica (RAG) de cláusulas normativas usando embeddings locales, aplicando filtros por tipo de contratación (Bienes, Servicios).

6. **[test_api_new.py](file:///data/proyectos/proyecto-bases/tests/test_api_new.py)**:
   * **Objetivo**: Validar las nuevas características de plantillas dinámicas y la auditoría.
   * **Valida**: Generación de documentos según la plantilla correspondiente (Bienes - Normal, etc.), inyección del campo `sistema_contratacion` y registro automático de la traza de auditoría en la tabla `auditoria` de SQLite.

---

## Cómo Ejecutar las Pruebas

Para ejecutar cualquiera de las pruebas, asegúrate de activar el entorno virtual e invocar el script con Python:

```bash
# Activar entorno virtual
source ./venv/bin/activate

# Ejecutar una prueba específica (ejemplo)
python tests/test_api_new.py
```
