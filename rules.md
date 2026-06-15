# Reglas de Comportamiento y Estándares de Codificación (rules.md)

Este documento establece las reglas, estándares de codificación y directrices que dictan el comportamiento de cualquier agente de IA al interactuar, modificar o extender la base de código del proyecto **Asistente de Bases Estándar - Osinergmin**.

---

## ⚖️ Principios Generales del Agente

1.  **Preservación del Contexto**: Nunca elimines comentarios o documentación existente a menos que se te indique explícitamente. Mantén las explicaciones lógicas de integración presentes en `mvp.md` y `diccionario.md`.
2.  **Idioma del Proyecto**:
    *   **Interfaz de Usuario (UI) y Textos**: Todo el contenido visible para el usuario (Streamlit dashboard, alertas, botones, descripciones) debe estar redactado en **Español (Castellano)** formal y técnico.
    *   **Código**: El código Python, comentarios técnicos y nombres de funciones/variables pueden utilizar inglés o español, manteniendo la coherencia de la base de código actual (ej. `current_step`, `historial_expedientes`).
3.  **Seguridad de Datos**: Respeta el carácter confidencial y estructurado de los documentos de contratación de Osinergmin. No asumas flujos externos inseguros y asegúrate de validar datos de entrada.

---

## 🎨 Estándares de Interfaz y Diseño (Streamlit)

1.  **Paleta de Colores Oficial de Osinergmin (Manual de Identidad)**:
    *   Azul Institucional Primario (Primary): `#0039aa` (para cabeceras `h1`, `h2`, `h3`, botones principales y elementos destacados).
    *   Amarillo Corporativo (Accent): `#fbe122` (para destaques y acentos).
    *   Gris Oscuro / Contraste (Surface): `#101828` (para el menú lateral / sidebar y fondos oscuros).
    *   Superficies y Bordes Neutros: Gris Claro `#f2f2f2`, Celeste Claro `#d2f7fc` (para fondos de app y recuadros).
    *   Acentos Complementarios: Naranja `#f6a229`, Verde `#35cc29`, Celeste `#03a9f4`.
2.  **Estilos CSS Premium**:
    *   Toda modificación en la UI debe inyectarse a través del bloque de estilos CSS definido en la parte superior de `app.py` respetando estrictamente las variables `:root` definidas.
    *   Utiliza de forma obligatoria la fuente institucional `'Poppins', sans-serif;`.
    *   **Elemento Fijo (Línea de Identidad)**: Es obligatorio mantener la franja combinada "Azul y Amarilla" con un alto estándar de entre `21px` y `30px` en la cabecera principal y de menú lateral.
    *   Evita layouts desordenados. Usa tarjetas con bordes redondeados (`border-radius: 12px`), sombreados sutiles (`box-shadow`) y transiciones suaves (`transition: all 0.2s ease`).
3.  **Integridad del Flujo Multipaso**:
    *   No rompas la navegación del asistente. Cualquier paso agregado o modificado debe estar integrado dentro del estado de sesión de Streamlit (`st.session_state.current_step`) y reflejarse correctamente en el indicador visual superior.

---

## 🐍 Guía de Codificación en Python

1.  **Formato y Estilo**:
    *   Sigue los principios de **PEP 8**.
    *   Declara explícitamente los tipos de datos en la firma de las funciones (Type Hinting) para mayor legibilidad y prevención de fallos.
2.  **Manejo de Estados en Streamlit**:
    *   Inicializa siempre las variables de estado en `st.session_state` antes de utilizarlas en la renderización para evitar errores del tipo `AttributeError` o `KeyError`.
3.  **Integraciones de IA e Ingeniería de Prompts**:
    *   Al trabajar con llamadas a LLM (Ollama o servicios Cloud), define siempre modelos estructurados mediante **Pydantic** para garantizar respuestas consistentes.
    *   Separa claramente el Prompt de sistema del contenido del usuario.
    *   Incluye manejo de excepciones y fallas (fallbacks) en las llamadas a APIs de lenguaje para evitar caídas completas del asistente.

---

## 📄 Gestión de Git y commits

1.  **Ramas**:
    *   La rama principal de desarrollo es `main`.
2.  **Mensajes de commit**:
    *   Escribe mensajes de commit claros, concisos y en español que expliquen de forma breve el cambio realizado.
