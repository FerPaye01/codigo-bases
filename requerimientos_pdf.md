Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

Nombre del Requerimiento
Cod. Req.
Tipo de
Req.

RQ-12
Creación

Piloto de Asistente IA para Bases
Gerencia/
Nombre Software
División
Cod. Software

Nuevo

GAF

16/12/2025

Creador

Asistente IA para Contratos
Carlos Chirinos

Versión

Modificación 16/12/2025 Modificador Carlos Chirinos

1.0

1. INTRODUCCIÓN
El presente documento establece los requerimientos para el desarrollo de un Asistente de
Inteligencia Artificial Generativa (AIGEN) destinado a automatizar la redacción de las Bases
Estándar de los procedimientos de selección en Osinergmin. El objetivo es mitigar las
problemáticas identificadas en el proceso de elaboración de Bases.
Problemáticas a mitigar:
•

Inconsistencias y errores en la redacción: Errores o falta de uniformidad en las Bases
debido a la dependencia de múltiples fuentes documentales (TDRs, plantillas).

•

Tiempo y esfuerzo significativo: La elaboración de Bases es un proceso intensivo que
requiere la recopilación y conciliación de información del TDR con los campos de la
plantilla.

2. DEFINICIONES Y ABREVIACIONES
•

TDR (Términos de Referencia): Documento que especifica los requisitos, condiciones y
características que deben cumplir los servicios a contratar.
GSTI (Gerencia de Sistemas y Tecnologías de la Información): Área de Osinergmin
encargada de gestionar los sistemas y tecnologías de información.
GAF (Gerencia de Administración y Finanzas): Área de Osinergmin responsable de la
administración y las finanzas de la organización.
Pronunciamientos: Respuestas y decisiones emitidas por entidades competentes en
relación con consultas o solicitudes formales.
Inteligencia Artificial (IA): Campo de estudio y aplicación de sistemas informáticos capaces
de realizar tareas que normalmente requieren de la inteligencia humana.
Chatbot: Programa informático que simula una conversación humana a través de una
interfaz de chat, utilizando IA para responder preguntas y realizar tareas.
Prompts: Indicaciones o preguntas utilizadas por el Chatbot para guiar al usuario en la
generación de contenido.
Contrato: Documento legal que formaliza la relación entre Osinergmin y el proveedor
seleccionado, basado en la propuesta ganadora y las Bases Integradas.
SIGED (Sistema de Trámite Documentario): Sistema utilizado para gestionar expedientes,
donde se encuentra la documentación del proceso de contratación, incluyendo la
propuesta ganadora.
Bases Estándar: Plantillas preaprobadas por Osinergmin para la redacción de Bases
(Bienes, Servicios, Consultoría).
Datos Administrativos: Campos obligatorios para la Base, introducidos manualmente por
el usuario (Nomenclatura, Cronograma, Valor Estimado, etc.).

•
•
•
•
•
•
•
•
•
•

3. OBJETIVO
•

Implementar una solución de modelo de Inteligencia Artificial (IA) generativa
(Chatbot/Asistente Web) que asista en la redacción y llenado automático de las Bases
Estándar en Osinergmin, reduciendo el error manual y el tiempo de elaboración.

4. ALCANCE
El asistente se centrará en la generación del documento de Bases completo, utilizando
información clave extraída automáticamente del TDR y complementada con datos
administrativos ingresados por el usuario. La implementación será sobre servicios de AWS.
Funcionalidades Clave:
•

Selección de Plantilla: Gestión de las 6 plantillas de Bases Estándar (Bienes, Servicios,
Consultorías, en versiones normal y abreviada).

•

Extracción de Datos: Capacidad de extraer, mediante NLP/OCR, los datos del TDR
(Objeto, Plazo, Requerimiento).

•

Llenado Automático: Uso de los datos extraídos para el llenado de secciones
específicas (Monto, Plazo, Factores de Evaluación, etc.).

5. REQUISITOS FUNCIONALES
RF N°

Descripción

P á g i n a 1 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

RF-1
RF-2
RF-3
RF-4
RF-5

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

El asistente debe poder consultar el número de expediente SIGED para identificar
el TDR asociado y, mediante consulta al usuario, determinar el Objeto y Tipo de
Procedimiento para seleccionar la Base Estándar correcta.
El asistente debe generar el borrador de Bases basándose en el modelo de Base
Estándar correspondiente a la selección de RF-1 (Bienes/Servicios/Consultoría;
Normal/Abreviado).
El asistente debe realizar la extracción de datos técnicos del TDR (Ej. Objeto, Plazo,
Requerimiento Completo) para el llenado de las secciones del borrador de Bases.
El asistente debe solicitar y usar los datos administrativos (Nomenclatura,
Cronograma, Valor Estimado/Referencial, Fuente de Financiamiento) para
completar las secciones faltantes de la Base.
El sistema debe generar un documento de salida (.DOCx).

6. REQUISITOS NO FUNCIONALES
RNF N°
RNF-1
RNF-2
RNF-3
RNF-4

Descripción
Seguridad: Cumplir con los estándares de seguridad de Osinergmin, protegiendo
los datos del TDR y garantizando la trazabilidad de las acciones del usuario.
Plataforma Tecnológica: La solución debe ser implementada y soportada en la
infraestructura de AWS (S3, Lambda, NLP/OCR services).
Interfaz en Español: La interfaz de la asistencia virtual estará completamente en
español.
Persistencia: La aplicación debe utilizar un mecanismo (ej. localStorage o Base de
Datos) para guardar el estado de un proceso de elaboración de Bases y permitir su
posterior reanudación.

7. DIAGRAMA DE PROCESO DE SOLUCIÓN

P á g i n a 2 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

8. DIAGRAMA DE ACTIVIDADES O PROCESOS

9. DETALLE FUNCIONAL
El proceso se inicia al proporcionar el número de expediente y sigue un flujo de tres
columnas para la interacción y el feedback.
RF-1: Identificación y Clasificación del TDR
Descripción: El sistema debe iniciar el proceso solicitando el código del expediente SIGED
(ver UI_01) y clasificar el TDR para asociarlo a la plantilla de Bases correcta
(Bienes/Servicios/Consultoría - Normal/Abreviado) (ver UI_02).
Criterios Técnicos de Implementación:
●
●

Implementar un proceso de clasificación de documentos para seleccionar una de las 6
Bases Estándar disponibles.
Integrar la lógica multiplantilla para la selección de la estructura de la Base.

UI_01. Ingreso de número de expediente.

P á g i n a 3 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

UI_02. Selección de plantilla.

RF-2, RF-3, RF-4: Extracción, Mapeo y Llenado
Descripción: Después de la clasificación, el sistema debe extraer automáticamente los datos
del TDR y solicitar al usuario los datos administrativos faltantes para el llenado de la plantilla.
Datos Técnicos Extraídos (RF-3): Objeto de la Contratación, Plazo de Ejecución, Sistema de
Contratación, Requerimiento Completo (Capítulo III), Requisitos de Calificación, Factores de
Evaluación.
Datos Administrativos Ingresados (RF-4): Nomenclatura del Procedimiento, Valor
Estimado/Referencial, Solicitante, Fechas clave del Cronograma, Fuente de Financiamiento
(ver UI_03, UI_04, UI_05, UI_06, UI_07 respectivamente).
Criterios Técnicos de Implementación:
●
●

Implementar un proceso de extracción de información (OCR/NLP) sobre el TDR para
cargar los datos en variables estructuradas.
El Orquestador debe mapear las variables extraídas a los campos directos de la plantilla
de Bases, reemplazando las etiquetas sombreadas [ABC].

UI_03. Ingreso de número de proceso.

P á g i n a 4 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

UI_04. Ingreso del valor referencial.

UI_05. Ingreso de la unidad orgánica solicitante.

UI_06. Ingreso de las fechas del proceso.

P á g i n a 5 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

UI_07. Ingreso de la fuente de financiamiento.

RF-5: Salida y Previsualización
Descripción: El sistema debe generar el borrador final de Bases, mostrando el resultado en
un visor y permitiendo la descarga del documento formateado.
Criterios Técnicos de Implementación:
●
●
●

El visor debe permitir la previsualización del documento y el scroll independiente del
panel (ver UI_08).
Debe permitir elegir un documento anterior generado de la lista de “Historial de
expedientes” (ver UI_09)
La descarga debe generar un archivo con extensión .docx (ver UI_10).

UI_08. Vista preliminar de las bases.

UI_09. Visualizar otras bases trabajadas.

P á g i n a 6 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

UI_10. Descarga de archivo docx con las bases generadas.
10. DETALLE NO FUNCIONAL
10.1.

SEGURIDAD Y PRIVACIDAD

Se implementarán medidas de seguridad para garantizar que la interacción con el modelo IA
(Chatbot) solo proporcione información relevante para el usuario y que los datos estén
protegidos adecuadamente.
10.2.

INTERFAZ EN ESPAÑOL

La interfaz de la asistencia virtual estará completamente en español para proporcionar una
experiencia óptima a los usuarios objetivo de estos servicios.
11. FUERA DE ALCANCE DE LA SOLUCIÓN
•

El asistente no negocia ni valida legalmente el contenido final de las Bases.

•

No reemplazará la revisión legal final del documento de Bases Integradas por parte del
área legal de Osinergmin.

•

No realizará la publicación ni el registro oficial del documento de Bases en el SEACE o en
el sistema interno.

•

La herramienta solo comparará los datos extraídos del TDR con las plantillas de Bases
Estándar y sus propias bases de conocimiento.

12. CRONOGRAMA
Stage
1
2
3

Descripción
Análisis y diseño técnico
Desarrollo y pruebas unitarias
Pruebas de sistema

Inicio

Fin

Duración
5 semana
14
semanas
3 semanas

P á g i n a 7 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

RF Asoc.

Nombres y
Apellidos

Rol

Gerencia /
División

13. LISTA DE INTERESADOS

RF-1 al RF-5

Miguel Ángel
Goetendia Alarcón

Líder

GAF

mgoetendia@osinergmin.gob.pe

RF-1 al RF-5

Violeta Mercedes
Rodríguez Arce

Líder - apoyo

ULOG

vrodriguez@osinergmin.gob.pe

RF-1 al RF-5

Amparito Gianina
Acevedo Flores

Líder – apoyo

GSTI

RF-1 al RF-5

Julio Lazo Abadie

Líder – apoyo

GPPM

Correo

aacevedo@osinergmin.gob.pe

jlazo@osinergmin.gob.pe

P á g i n a 8 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

14. ACTA DE APROBACIÓN
Se listan los responsables de dar conformidad a los requerimientos.
Requerimien
to Funcional

Rol
Responsable

Nombres y Apellidos

Firma
«ffalcon»

RF-1 al RF-5

Responsable

Freddy Falcón

«jcastaneda»
RF-1 al RF-5

Responsable

Jose Castañeda

«cachirinos»
RF-1 al RF-5

Responsable

Carlos Chirinos

Firmado Digitalmente
por: FALCON
OBREGON Freddy
Felipe FAU
20376082114 hard
Fecha: 18/12/2025
09:36:31

Firmado Digitalmente
por: CASTAÑEDA
ROSSEL Jose Manuel
FAU 20376082114 soft
Fecha: 18/12/2025
09:18:53

Firmado Digitalmente
por: CHIRINOS
AZPILCUETA Carlos
Alberto FAU
20376082114 soft
Fecha: 18/12/2025
10:03:33

P á g i n a 9 | 10

Gerencia de Sistemas y
Tecnologías de la
Información

ESPECIFICACIÓN DE REQUERIMIENTOS

Código: F1-PS4-2-PE-03
Revisión: 02

15. CONTROL DE VERSIONES
Versión
N°
0.1

Fecha

Autor

12/11/2025 Carlos Chirinos

Descripción
Versión Preliminar

P á g i n a 10 | 10

