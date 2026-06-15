# Propuesta de Herramientas MCP para el Asistente de Bases Estándar (Osinergmin)

Este documento detalla una propuesta de **10 herramientas (tools)** para tu servidor de **Model Context Protocol (MCP)** desarrollado con `FastMCP` (Python). Estas herramientas están diseñadas específicamente para complementar la inferencia de tu LLM local (`gemma3:1b`), delegando tareas de cálculo, búsqueda y validación lógica al backend de Python, mejorando drásticamente el rendimiento (performance) y la confiabilidad del sistema.

---

## 1. ¿Por qué usar herramientas MCP en este proyecto?

El modelo local `gemma3:1b` es ligero y rápido en CPU, pero tiene limitaciones inherentes en:
1. **Razonamiento matemático / calendario**: Los LLMs suelen equivocarse calculando plazos de días hábiles.
2. **Contexto limitado**: Procesar un TDR completo de 30 páginas sobrecarga el contexto y genera "alucinaciones".
3. **Validación normativa estricta**: Recordar montos tope anuales de OSCE o reglas gramaticales de conversión numérica es ineficiente para un LLM.

Al delegar estas tareas a **herramientas MCP nativas**, el LLM solo actúa como el "orquestador", llamando a funciones deterministas en Python cuando es necesario.

---

## 2. Propuesta de 10 Herramientas MCP

### 1. `extraer_seccion_tdr`
* **Descripción**: Extrae fragmentos específicos de la conversión Markdown de Docling usando patrones de cabeceras.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def extraer_seccion_tdr(ruta_archivo: str, seccion: str) -> str
  ```
  *(Parámetro `seccion` puede ser: "objeto", "plazo", "calificacion", "evaluacion", "entregables")*
* **Beneficio para el LLM**: Reduce el consumo de tokens en un 80% al enviar solo la sección relevante de interés, evitando que el LLM sufra de "lost in the middle" (pérdida de atención) en documentos extensos.

---

### 2. `calcular_cronograma_legal`
* **Descripción**: Calcula los plazos y fechas del cronograma de contratación (Convocatoria, Consultas, Absolución, Presentación, Buena Pro) en base a la fecha de inicio, excluyendo fines de semana y el calendario oficial de feriados de Perú / Osinergmin.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def calcular_cronograma_legal(fecha_convocatoria: str, tipo_procedimiento: str) -> dict
  ```
* **Beneficio para el LLM**: Garantiza un cálculo 100% libre de errores matemáticos y cumple con los plazos legales mínimos establecidos por la Ley de Contrataciones del Estado (OSCE).

---

### 3. `validar_monto_limite`
* **Descripción**: Evalúa el monto estimado del proceso frente a los topes oficiales anuales de OSCE para indicar la modalidad del procedimiento (Licitación Pública, Concurso Público, Adjudicación Simplificada) y determinar la plantilla adecuada.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def validar_monto_limite(monto: float, objeto: str) -> dict
  ```
* **Beneficio para el LLM**: Evita que el modelo alucine o clasifique erróneamente el procedimiento, protegiendo al sistema de errores legales críticos.

---

### 4. `convertir_moneda_letras`
* **Descripción**: Convierte un número decimal (monto) a su representación formal en texto en español (ej. `150500.20` -> `"CIENTO CINCUENTA MIL QUINIENTOS Y 20/100 SOLES"`).
* **Firma de la función**:
  ```python
  @mcp.tool()
  def convertir_moneda_letras(monto: float, moneda: str = "PEN") -> str
  ```
* **Beneficio para el LLM**: Ahorra tokens de inferencia y asegura el cumplimiento estricto del formato legal de redacción económica requerido en el Capítulo III de las Bases.

---

### 5. `consultar_expediente_siged`
* **Descripción**: Consulta el mock (o la intranet de Osinergmin) para recuperar los metadatos verídicos de un expediente SIGED en tiempo real.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def consultar_expediente_siged(numero_expediente: str) -> dict
  ```
* **Beneficio para el LLM**: Provee datos de "ground truth" (verdad de campo) inmediatos al LLM para su llenado estructurado, sin riesgo de alucinación del nombre del responsable o del asunto.

---

### 6. `buscar_jurisprudencia_osce`
* **Descripción**: Realiza una consulta semántica contra la base de datos vectorial local (Qdrant) para recuperar directivas, resoluciones del Tribunal de OSCE o cláusulas estándar de Osinergmin.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def buscar_jurisprudencia_osce(consulta_texto: str, categoria: str, limit: int = 3) -> list
  ```
* **Beneficio para el LLM**: Integra capacidades RAG de forma transparente. El LLM puede invocar esta herramienta cuando no está seguro de la legalidad de un requerimiento técnico del postor.

---

### 7. `validar_coherencia_requisitos`
* **Descripción**: Compara mediante similitud sintáctica y semántica (Jaccard / Cosine Similarity) si un requisito mínimo exigido como "Requisito de Calificación" se está duplicando o puntuando erróneamente en los "Factores de Evaluación".
* **Firma de la función**:
  ```python
  @mcp.tool()
  def validar_coherencia_requisitos(requisitos: str, factores: str) -> dict
  ```
* **Beneficio para el LLM**: Evita la "doble evaluación" (práctica ilegal en contrataciones públicas en Perú) mediante análisis estricto en Python, liberando al LLM de complejas deducciones lógicas de texto.

---

### 8. `escanear_etiquetas_plantilla`
* **Descripción**: Analiza el archivo `.docx` de la plantilla seleccionada y extrae todas las variables de Jinja2 (`{{ ... }}`) que necesitan ser rellenadas.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def escanear_etiquetas_plantilla(nombre_plantilla: str) -> list
  ```
* **Beneficio para el LLM**: Actúa como un "checklist dinámico". Le indica al LLM exactamente qué variables debe buscar en el TDR, estructurando su plan de acción antes de la fase de llenado.

---

### 9. `consultar_glosario_osinergmin`
* **Descripción**: Recupera definiciones exactas del diccionario oficial de terminologías de Osinergmin.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def consultar_glosario_osinergmin(termino: str) -> str
  ```
* **Beneficio para el LLM**: Mantiene el prompt del sistema limpio. El modelo consulta solo el término técnico que necesita en el momento en lugar de inyectar todo el glosario en el contexto inicial.

---

### 10. `registrar_auditoria_mcp`
* **Descripción**: Registra acciones directamente en la tabla de auditoría local de SQLite para garantizar la trazabilidad de los pasos autónomos del agente IA.
* **Firma de la función**:
  ```python
  @mcp.tool()
  def registrar_auditoria_mcp(usuario_id: str, accion: str, numero_expediente: str, detalles: str) -> bool
  ```
* **Beneficio para el LLM**: Permite al LLM autogestionar el cumplimiento del requisito **RNF-1** (Trazabilidad) de manera proactiva durante la ejecución de tareas asíncronas o complejas.
