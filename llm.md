# Estructura del Proyecto y Ubicación de Información Relevante (llm.md)

Este documento detalla la estructura del proyecto **Asistente de Bases Estándar - Osinergmin** y mapea la ubicación de toda la información relevante para facilitar el contexto y la navegación a cualquier LLM o agente de IA que trabaje en el repositorio.

---

## 📂 Directorio Raíz del Proyecto

El proyecto se encuentra ubicado en el espacio de trabajo local en `/data/proyectos/proyecto-bases/` y cuenta con la siguiente estructura de archivos principales:

*   **[app.py](file:///data/proyectos/proyecto-bases/app.py)**: Archivo principal de la aplicación. Implementa un dashboard web interactivo con **Streamlit** estructurado como un asistente paso a paso (wizard de 12 pasos) para la generación de Bases Estándar a partir de un expediente de SIGED.
*   **[mvp.md](file:///data/proyectos/proyecto-bases/mvp.md)**: Documento de análisis estratégico, arquitectura del MVP y riesgos técnicos. Detalla la integración teórica con la API de SIGED (endpoints necesarios, autenticación, contingencias como la carga manual) y el mapeo de variables del TDR a la plantilla.
*   **[diccionario.md](file:///data/proyectos/proyecto-bases/diccionario.md)**: Glosario de acrónimos y términos oficiales del proceso de contratación y sistemas de Osinergmin (ej. TDR, SIGED, GSTI, GAF, Pronunciamientos).
*   **[flujo.png](file:///data/proyectos/proyecto-bases/flujo.png)**: Diagrama del flujo de integración y pasos del asistente.
*   **[paper.md](file:///data/proyectos/proyecto-bases/paper.md)**: Nota corta descriptiva del estado del proyecto.
*   **[server protocol.mp4](file:///data/proyectos/proyecto-bases/server%20protocol.mp4)**: Video explicativo del protocolo y funcionamiento del servidor MCP.

---

## 📂 Subdirectorios Especializados

### 1. `INVESTIGACION/`
Contiene la documentación del estado del arte, investigación de mercado y comparativa de modelos de lenguaje para el procesamiento de TDRs y extracción de requerimientos.
*   `chatgpt_investigacion_alternativas.md`: Comparativa y alternativas usando OpenAI.
*   `chatgpt_investigacion_alternativas_sin_terceros.md`: Integración directa sin dependencias de terceros intermediarios.
*   `claude_investigacion_alternativas.md`: Evaluación del modelo Claude (Anthropic).
*   `gemini_investigacion_alternativas.md` y `gemini_investigacion_alternativas_sin_terceros.md`: Análisis técnico utilizando la API de Google Gemini.
*   `perplexity_investigacion_alternativas.md` y `perplexity_investigacion_alternativas_sin_terceros.md`: Análisis y comparación utilizando la API de Perplexity.

### 2. `LLM/`
Directorio con prototipos funcionales y scripts para la ejecución local de LLMs:
*   `ollama_gemma3_demo.py`: Demostración completa en Python de cómo utilizar **Ollama** con el modelo `gemma3:1b` para realizar extracciones estructuradas (JSON) y llamadas a funciones (tool calling).
*   `ollama_mcp_client.py`: Script cliente que demuestra la comunicación y consulta a un servidor MCP.
*   `ollama_non_interactive_demo.py`: Script para ejecución directa en background y automatizaciones.

### 3. `MCP/`
Implementación del estándar Model Context Protocol (MCP) de Anthropic para dar superpoderes (herramientas locales) al agente:
*   `server.py`: Servidor basado en **FastMCP** que expone herramientas de cálculo y consulta climática simuladas a través del protocolo de transporte SSE (Server-Sent Events).

### 4. `LLM-NESTED LEARNING/`
*   `nested-learning-kmccleary3301/`: Recursos de aprendizaje anidado para optimización de contexto y prompts.
