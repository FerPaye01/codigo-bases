import streamlit as st
import pandas as pd
import datetime
import time

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="Asistente de Bases Estándar - Osinergmin",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS premium empresarial con colores de Osinergmin y diseño de flujo multipaso
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #0c4a6e; /* Azul Osinergmin */
    }

    /* Fondo de la App */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* Sidebar Estilizado */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Slate Oscuro */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-weight: 600;
    }

    /* Tarjetas y Contenedores Premium */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
        transition: all 0.2s ease-in-out;
        margin-bottom: 12px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        border-color: #0284c7;
    }

    /* Alertas */
    .alert-panel {
        background-color: #fffbeb;
        border-left: 4px solid #d97706;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: #78350f;
        font-size: 0.9rem;
    }
    .success-panel {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: #14532d;
        font-size: 0.9rem;
    }
    .error-panel {
        background-color: #fef2f2;
        border-left: 4px solid #dc2626;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: #991b1b;
        font-size: 0.9rem;
    }

    /* Indicador visual de pasos */
    .step-indicator-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 25px;
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.01);
    }
    .step-item {
        text-align: center;
        flex: 1;
        position: relative;
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
    }
    .step-item.active {
        color: #0284c7;
    }
    .step-item.completed {
        color: #16a34a;
    }
    .step-number {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #e2e8f0;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 6px auto;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .step-item.active .step-number {
        background-color: #0284c7;
        color: white;
    }
    .step-item.completed .step-number {
        background-color: #16a34a;
        color: white;
    }

    /* Caja de Vista Preliminar del Documento */
    .doc-preview {
        background-color: #1e293b;
        color: #f8fafc;
        font-family: 'Courier New', Courier, monospace;
        padding: 24px;
        border-radius: 10px;
        border: 1px solid #334155;
        font-size: 0.9rem;
        line-height: 1.5;
        max-height: 500px;
        overflow-y: auto;
    }

    /* Botones */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Indicador de confianza */
    .confidence-badge {
        font-size: 0.75rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .conf-green { background-color: #dcfce7; color: #15803d; }
    .conf-orange { background-color: #fef3c7; color: #b45309; }
    .conf-red { background-color: #fee2e2; color: #b91c1c; }

    /* Visor del TDR */
    .tdr-viewer {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        height: 450px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN (PERSISTENCIA MULTIPASO)
# ==============================================================================
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

# Historial simulado de expedientes
if "historial_expedientes" not in st.session_state:
    st.session_state.historial_expedientes = [
        {
            "expediente": "EXP-SIGED-2026-00982",
            "plantilla": "Servicios - Normal",
            "creacion": "10/06/2026",
            "modificacion": "12/06/2026",
            "responsable": "jortiz@osinergmin.gob.pe",
            "estado": "Borrador generado"
        },
        {
            "expediente": "EXP-SIGED-2026-00411",
            "plantilla": "Bienes - Normal",
            "creacion": "05/06/2026",
            "modificacion": "05/06/2026",
            "responsable": "lrodriguez@osinergmin.gob.pe",
            "estado": "Descargado"
        },
        {
            "expediente": "EXP-SIGED-2026-01053",
            "plantilla": "Consultoría - Abreviado",
            "creacion": "12/06/2026",
            "modificacion": "12/06/2026",
            "responsable": "jortiz@osinergmin.gob.pe",
            "estado": "En progreso"
        }
    ]

# Variables del Expediente Activo
if "expediente_input" not in st.session_state:
    st.session_state.expediente_input = ""
if "expediente_valido" not in st.session_state:
    st.session_state.expediente_valido = False
if "expediente_error" not in st.session_state:
    st.session_state.expediente_error = ""
if "expediente_data" not in st.session_state:
    st.session_state.expediente_data = None

# Plantilla de bases seleccionada
if "plantilla_sugerida" not in st.session_state:
    st.session_state.plantilla_sugerida = ""
if "plantilla_final" not in st.session_state:
    st.session_state.plantilla_final = ""
if "plantilla_confirmada" not in st.session_state:
    st.session_state.plantilla_confirmada = False

# Datos técnicos extraídos y sus estados de confianza
if "datos_tecnicos" not in st.session_state:
    st.session_state.datos_tecnicos = {
        "objeto": "",
        "plazo": "",
        "sistema_contratacion": "",
        "requerimiento_completo": "",
        "requisitos_calificacion": "",
        "factores_evaluacion": ""
    }
if "datos_tecnicos_confianza" not in st.session_state:
    st.session_state.datos_tecnicos_confianza = {
        "objeto": "Verde",
        "plazo": "Verde",
        "sistema_contratacion": "Naranja",
        "requerimiento_completo": "Verde",
        "requisitos_calificacion": "Naranja",
        "factores_evaluacion": "Rojo"
    }
if "datos_tecnicos_confirmados" not in st.session_state:
    st.session_state.datos_tecnicos_confirmados = False

# Datos administrativos ingresados
if "nomenclatura" not in st.session_state:
    st.session_state.nomenclatura = ""
if "tipo_procedimiento" not in st.session_state:
    st.session_state.tipo_procedimiento = "Adjudicación Simplificada"
if "numero_proceso" not in st.session_state:
    st.session_state.numero_proceso = "AS-002-2026-OSINERGMIN"
if "valor_estimado" not in st.session_state:
    st.session_state.valor_estimado = 0.0
if "moneda" not in st.session_state:
    st.session_state.moneda = "Soles (S/.)"
if "fuente_valor" not in st.session_state:
    st.session_state.fuente_valor = "Estudio de Mercado"
if "unidad_solicitante" not in st.session_state:
    st.session_state.unidad_solicitante = "GSTI"
if "responsable" not in st.session_state:
    st.session_state.responsable = "Julio Ortiz"
if "fecha_convocatoria" not in st.session_state:
    st.session_state.fecha_convocatoria = datetime.date.today()
if "fecha_consultas" not in st.session_state:
    st.session_state.fecha_consultas = datetime.date.today() + datetime.timedelta(days=4)
if "fecha_absolucion" not in st.session_state:
    st.session_state.fecha_absolucion = datetime.date.today() + datetime.timedelta(days=6)
if "fecha_presentacion" not in st.session_state:
    st.session_state.fecha_presentacion = datetime.date.today() + datetime.timedelta(days=12)
if "fecha_evaluacion" not in st.session_state:
    st.session_state.fecha_evaluacion = datetime.date.today() + datetime.timedelta(days=15)
if "fecha_buenapro" not in st.session_state:
    st.session_state.fecha_buenapro = datetime.date.today() + datetime.timedelta(days=18)
if "fuente_financiamiento" not in st.session_state:
    st.session_state.fuente_financiamiento = "Recursos Directamente Recaudados (RDR)"
if "observaciones_finan" not in st.session_state:
    st.session_state.observaciones_finan = ""
if "datos_admin_guardados" not in st.session_state:
    st.session_state.datos_admin_guardados = False

# ==============================================================================
# MENU LATERAL - INFORMACIÓN CORPORATIVA
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='color: white; margin-top: 5px;'>Asistente IA</h2>", unsafe_allow_html=True)
    st.caption("Fase 1: Generación de Bases Estándar")
    st.markdown("<hr style='border-color: #334155; margin: 10px 0;'>", unsafe_allow_html=True)
    
    # Barra lateral de accesos directos
    st.markdown("### Navegación Rápida")
    selected_step = st.radio(
        "Saltar a Pantalla:",
        ["1. Inicio / SIGED", "2. Plantilla", "3. Datos Técnicos TDR", "4. Datos Administrativos", "5. Vista Preliminar", "6. Historial & Descargas"],
        index=st.session_state.current_step - 1
    )
    
    # Actualizar paso actual a partir del radio button
    paso_radio = int(selected_step[0])
    if paso_radio != st.session_state.current_step:
        st.session_state.current_step = paso_radio
        st.rerun()

    st.markdown("<hr style='border-color: #334155; margin: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("### Datos del Proceso Activo")
    if st.session_state.expediente_valido:
        st.caption(f"**Expediente:** `{st.session_state.expediente_input}`")
        if st.session_state.plantilla_final:
            st.caption(f"**Plantilla:** {st.session_state.plantilla_final}")
        if st.session_state.nomenclatura:
            st.caption(f"**Nomenclatura:** `{st.session_state.nomenclatura}`")
    else:
        st.caption("Ningún expediente cargado.")


# ==============================================================================
# PANTALLA 1: INICIO / INGRESO DE EXPEDIENTE SIGED
# ==============================================================================
if st.session_state.current_step == 1:
    st.title("Asistente IA para generación de Bases")
    st.markdown("Ingrese el número de expediente SIGED para iniciar la generación de Bases Estándar.")
    
    col_e1, col_e2 = st.columns([1.2, 1])
    
    with col_e1:
        st.markdown("#### Búsqueda en SIGED")
        expediente_input = st.text_input(
            "Número de expediente SIGED:", 
            value=st.session_state.expediente_input, 
            placeholder="Ingrese e.g. EXP-SIGED-2026-00982"
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            btn_validar = st.button("Validar expediente", use_container_width=True)
        with col_btn2:
            btn_limpiar = st.button("Cancelar o Limpiar", use_container_width=True)
            
        if btn_limpiar:
            st.session_state.expediente_input = ""
            st.session_state.expediente_valido = False
            st.session_state.expediente_error = ""
            st.session_state.expediente_data = None
            st.session_state.bases_generadas = False
            st.rerun()

        # Lógica de validación
        if btn_validar:
            if not expediente_input:
                st.markdown('<div class="error-panel">Ingrese un número de expediente válido.</div>', unsafe_allow_html=True)
            else:
                st.session_state.expediente_input = expediente_input
                
                if expediente_input in ["EXP-SIGED-2026-00982", "EXP-SIGED-2026-00411"]:
                    # Simulación interactiva paso a paso del flujo de la imagen
                    log_placeholder = st.empty()
                    with log_placeholder.container():
                        st.markdown('<div class="aws-panel">👤 <b>[Paso 1]</b> Portal recibe N° Expediente: ' + expediente_input + '</div>', unsafe_allow_html=True)
                        time.sleep(0.7)
                        st.markdown('<div class="aws-panel">🔄 <b>[Paso 2]</b> Solicitando documento TDR al Sistema SIGED (API SIGED)...</div>', unsafe_allow_html=True)
                        time.sleep(0.7)
                        st.markdown('<div class="aws-panel">📄 <b>[Paso 3]</b> SIGED proporciona archivo digital del TDR en formato PDF/DOCX</div>', unsafe_allow_html=True)
                        time.sleep(0.7)
                        st.markdown('<div class="aws-panel">🧠 <b>[Paso 4]</b> Enviando archivo al Componente NLP/OCR para extracción técnica automática (RF-3)...</div>', unsafe_allow_html=True)
                        time.sleep(0.9)
                    log_placeholder.empty()

                    st.session_state.expediente_valido = True
                    st.session_state.expediente_error = ""
                    
                    if expediente_input == "EXP-SIGED-2026-00982":
                        st.session_state.expediente_data = {
                            "numero": "EXP-SIGED-2026-00982",
                            "asunto": "Servicio de Consultoría para la Gestión y Mitigación de Riesgos Informáticos en Osinergmin",
                            "tdr": "TDR_Consultoria_Ciberseguridad_2026.pdf",
                            "fecha": "10/06/2026"
                        }
                        st.session_state.plantilla_sugerida = "Servicios - Normal"
                        if not st.session_state.plantilla_final:
                            st.session_state.plantilla_final = "Servicios - Normal"
                        st.session_state.datos_tecnicos = {
                            "objeto": "Contratar un servicio de consultoría especializada para el diagnóstico, gestión y mitigación de riesgos de seguridad de la información e infraestructura de red de Osinergmin.",
                            "plazo": "180 días calendario contados a partir del día siguiente de la firma del contrato.",
                            "sistema_contratacion": "Suma Alzada",
                            "requerimiento_completo": "Se requiere la entrega de 4 informes de diagnóstico situacional, arquitectura sugerida, matriz de riesgos y plan de contingencias corporativo.",
                            "requisitos_calificacion": "1. Facturación acumulada del postor equivalente a 2 veces el valor estimado en consultorías similares.\n2. ISO 27001 activo de la empresa consultora.\n3. Certificaciones de personal clave: Jefe de Proyecto con PMP y CISM.",
                            "factores_evaluacion": "Factores de evaluación sugeridos: Certificación voluntaria ISO 22301 (Plan de Continuidad) de la empresa (20 pts), Mejoras del SLA (10 pts)."
                        }
                        st.session_state.nomenclatura = "AS-002-2026-OSINERGMIN"
                        st.session_state.valor_estimado = 180000.00
                        
                    elif expediente_input == "EXP-SIGED-2026-00411":
                        st.session_state.expediente_data = {
                            "numero": "EXP-SIGED-2026-00411",
                            "asunto": "Adquisición de Servidores de Alta Disponibilidad para el Data Center de Osinergmin",
                            "tdr": "TDR_Adquisicion_Servidores_2026.pdf",
                            "fecha": "05/06/2026"
                        }
                        st.session_state.plantilla_sugerida = "Bienes - Normal"
                        if not st.session_state.plantilla_final:
                            st.session_state.plantilla_final = "Bienes - Normal"
                        st.session_state.datos_tecnicos = {
                            "objeto": "Adquisición de 4 servidores físicos de alta disponibilidad incluyendo licenciamiento y soporte por 3 años.",
                            "plazo": "60 días calendario.",
                            "sistema_contratacion": "Suma Alzada",
                            "requerimiento_completo": "Servidores de 64 núcleos, 512GB RAM y almacenamiento SSD enterprise.",
                            "requisitos_calificacion": "Experiencia en bienes similares y soporte local certificado por fabricante.",
                            "factores_evaluacion": "Mejoras tecnológicas (procesador de mayor capacidad, RAM adicional)."
                        }
                        st.session_state.nomenclatura = "LP-001-2026-OSINERGMIN"
                        st.session_state.valor_estimado = 450000.00
                else:
                    st.session_state.expediente_valido = False
                    st.session_state.expediente_data = None
                    if "error" in expediente_input.lower():
                        st.session_state.expediente_error = "No se encontró expediente"
                    else:
                        st.session_state.expediente_error = "No se identificó TDR asociado"
            st.rerun()

        # Mostrar estado si ya está validado
        if st.session_state.expediente_valido:
            st.markdown('<div class="success-panel">✓ Expediente encontrado y validado en SIGED. Datos técnicos extraídos por NLP/OCR (Paso 4).</div>', unsafe_allow_html=True)
        elif st.session_state.expediente_error:
            if st.session_state.expediente_error == "No se encontró expediente":
                st.markdown('<div class="error-panel">❌ No se encontró expediente. Verifique la nomenclatura e intente nuevamente.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-panel">⚠️ No se identificó un documento de TDR asociado en este expediente del SIGED.</div>', unsafe_allow_html=True)

    with col_e2:
        if st.session_state.expediente_valido and st.session_state.expediente_data is not None:
            data = st.session_state.expediente_data
            st.markdown("#### Resumen del Expediente")
            st.markdown(f"""
            <div class="metric-card">
                <b>Número de expediente:</b> {data['numero']}<br>
                <b>Nombre / Asunto:</b> {data['asunto']}<br>
                <b>Documento TDR identificado:</b> <code style="color:#0284c7;">{data['tdr']}</code><br>
                <b>Fecha de registro:</b> {data['fecha']}
            </div>
            """, unsafe_allow_html=True)
            
            # Botón para ir al paso 2
            if st.button("Continuar a Selección de Plantilla ➡️", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()

# ==============================================================================
# PANTALLA 2: SELECCIÓN O CONFIRMACIÓN DE PLANTILLA
# ==============================================================================
elif st.session_state.current_step == 2:
    st.title("Selección de plantilla de Bases")
    st.markdown("Seleccione la plantilla correspondiente o confirme la sugerida por el sistema.")
    
    col_p1, col_p2 = st.columns([1.2, 1])
    
    with col_p1:
        st.markdown("#### Propuesta del Sistema")
        
        # Simulación de sugerencia basada en el expediente anterior
        contratacion_det = "Servicios en General"
        modalidad_det = "Adjudicación Simplificada / Concurso"
        if "Bienes" in st.session_state.plantilla_sugerida:
            contratacion_det = "Bienes"
            modalidad_det = "Licitación / Adjudicación"
            
        st.markdown(f"""
        <div class="aws-panel">
            <b>Tipo de contratación detectada:</b> {contratacion_det}<br>
            <b>Modalidad detectada:</b> {modalidad_det}<br>
            <b>Plantilla recomendada:</b> <code style="font-weight:bold;">{st.session_state.plantilla_sugerida}</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Selección Manual / Corrección")
        opciones_plantillas = [
            "Bienes - Normal",
            "Bienes - Abreviado",
            "Servicios - Normal",
            "Servicios - Abreviado",
            "Consultoría - Normal",
            "Consultoría - Abreviado"
        ]
        
        # Selector manual de plantillas
        plantilla_manual = st.selectbox(
            "Seleccione plantilla de Base Estándar:",
            opciones_plantillas,
            index=opciones_plantillas.index(st.session_state.plantilla_final) if st.session_state.plantilla_final in opciones_plantillas else 2
        )
        
        # Alerta si cambia la sugerida
        if plantilla_manual != st.session_state.plantilla_sugerida:
            st.markdown("""
            <div class="alert-panel">
                ⚠️ <b>Alerta:</b> La plantilla seleccionada manualmente será usada para la generación del documento.
            </div>
            """, unsafe_allow_html=True)
            
        # Botones de navegación
        col_btn_p1, col_btn_p2 = st.columns(2)
        with col_btn_p1:
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with col_btn_p2:
            if st.button("Confirmar plantilla ➡️", use_container_width=True):
                with st.spinner("Guardando selección de plantilla y datos en Base de Datos (Paso 7)..."):
                    time.sleep(1.0)
                st.session_state.plantilla_final = plantilla_manual
                st.session_state.plantilla_confirmada = True
                st.session_state.current_step = 3
                st.rerun()

    with col_p2:
        st.markdown("#### Detalle Legal de la Plantilla")
        st.markdown("""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; font-size: 0.85rem;">
            <strong>Estructura legal de Bases Estándar:</strong><br>
            Las plantillas son estructuradas en base a las directivas aprobadas por el Organismo Supervisor de las Contrataciones del Estado (OSCE) vigentes para Osinergmin.
            <br><br>
            • <b>Normal:</b> Contempla el desarrollo de factores de evaluación complejos, requisitos de precalificación y cláusulas legales completas.<br>
            • <b>Abreviado:</b> Procedimiento simplificado con plazos de convocatoria reducidos (e.g. 6 a 8 días útiles).
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# PANTALLA 3: REVISIÓN DE DATOS TÉCNICOS EXTRAÍDOS DEL TDR
# ==============================================================================
elif st.session_state.current_step == 3:
    st.title("Revisión de datos técnicos del TDR")
    st.markdown("Revise los datos extraídos automáticamente del TDR. Puede corregirlos antes de continuar.")
    
    col_t1, col_t2 = st.columns([1.2, 1])
    
    with col_t1:
        st.markdown("#### Datos Extraídos")
        
        # Formulario de campos técnicos editables
        objeto_val = st.text_area("Objeto de la contratación (Obligatorio)", value=st.session_state.datos_tecnicos["objeto"], height=70)
        plazo_val = st.text_input("Plazo de ejecución (Obligatorio)", value=st.session_state.datos_tecnicos["plazo"])
        sistema_val = st.text_input("Sistema de contratación", value=st.session_state.datos_tecnicos["sistema_contratacion"])
        req_completo_val = st.text_area("Requerimiento completo", value=st.session_state.datos_tecnicos["requerimiento_completo"], height=100)
        reqs_calif_val = st.text_area("Requisitos de calificación", value=st.session_state.datos_tecnicos["requisitos_calificacion"], height=100)
        factores_val = st.text_area("Factores de evaluación", value=st.session_state.datos_tecnicos["factores_evaluacion"], height=80)
        
        # Mostrar indicadores de confianza
        st.markdown("##### Indicadores de Confianza en Extracción (AWS OCR/NLP)")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("""
            • Objeto: <span class="confidence-badge conf-green">Verde</span><br>
            • Plazo: <span class="confidence-badge conf-green">Verde</span>
            """, unsafe_allow_html=True)
        with col_c2:
            st.markdown("""
            • Sistema: <span class="confidence-badge conf-orange">Naranja</span><br>
            • Requisitos: <span class="confidence-badge conf-orange">Naranja</span>
            """, unsafe_allow_html=True)
        with col_c3:
            st.markdown("""
            • Factores: <span class="confidence-badge conf-red">Rojo</span>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botones de control del paso
        col_btn_t1, col_btn_t2 = st.columns(2)
        with col_btn_t1:
            if st.button("Guardar y salir", use_container_width=True):
                st.session_state.datos_tecnicos = {
                    "objeto": objeto_val,
                    "plazo": plazo_val,
                    "sistema_contratacion": sistema_val,
                    "requerimiento_completo": req_completo_val,
                    "requisitos_calificacion": reqs_calif_val,
                    "factores_evaluacion": factores_val
                }
                st.session_state.current_step = 6 # Volver al historial
                st.rerun()
        with col_btn_t2:
            if st.button("Confirmar datos técnicos ➡️", use_container_width=True):
                if not objeto_val or not plazo_val:
                    st.markdown('<div class="error-panel">Debe completar los campos obligatorios antes de continuar (Objeto y Plazo).</div>', unsafe_allow_html=True)
                else:
                    st.session_state.datos_tecnicos = {
                        "objeto": objeto_val,
                        "plazo": plazo_val,
                        "sistema_contratacion": sistema_val,
                        "requerimiento_completo": req_completo_val,
                        "requisitos_calificacion": reqs_calif_val,
                        "factores_evaluacion": factores_val
                    }
                    st.session_state.datos_tecnicos_confirmados = True
                    st.session_state.current_step = 4
                    st.rerun()

    with col_t2:
        st.markdown("#### Panel visor del TDR")
        
        # Buscador en visor
        search_query = st.text_input("🔍 Buscar texto en el TDR original:", placeholder="Escriba palabra clave (e.g. plazo, jefe)")
        
        # Simulación del documento TDR original en un visor
        tdr_text = f"""TÉRMINOS DE REFERENCIA (TDR)
CONTRATACIÓN DE SERVICIO DE CONSULTORÍA
CÓDIGO INTERNO: TDR-GSTI-2026-004

1. OBJETO DE LA CONTRATACIÓN
Contratar un servicio de consultoría especializada para el diagnóstico, gestión y mitigación de riesgos de seguridad de la información e infraestructura de red de Osinergmin.

2. PLAZO DE EJECUCIÓN
El plazo estimado para la ejecución de las prestaciones del servicio es de 180 días calendario contados a partir del día siguiente de la firma del contrato.

3. SISTEMA DE CONTRATACIÓN
El presente proceso de selección se regirá por el sistema de Suma Alzada.

4. REQUERIMIENTO COMPLETO Y ENTREGABLES
- Entregable 1: Diagnóstico situacional de seguridad de red.
- Entregable 2: Arquitectura de seguridad lógica y física sugerida.
- Entregable 3: Matriz de riesgos informáticos de Osinergmin.
- Entregable 4: Plan de contingencias y recuperación ante desastres corporativo.

5. REQUISITOS DE CALIFICACIÓN
- Facturación acumulada de la empresa consultora equivalente a 2 veces el valor estimado en consultorías similares durante los últimos 5 años.
- Certificación ISO 27001 e ISO 9001 vigente.
- Jefe de Proyecto: Ingeniero con certificación PMP y CISM (Certified Information Security Manager).

6. PENALIDADES
Por retraso en la entrega de informes mensuales se aplicará una penalidad de 0.20% del valor de la orden/entregable por cada día calendario de demora.
"""
        # Resaltado de búsqueda simulado
        if search_query:
            tdr_display = tdr_text.replace(search_query, f"⚡[{search_query.upper()}]⚡")
        else:
            tdr_display = tdr_text
            
        st.markdown(f'<div class="tdr-viewer"><pre style="color:#0f172a; white-space: pre-wrap;">{tdr_display}</pre></div>', unsafe_allow_html=True)

# ==============================================================================
# PANTALLA 4: INGRESO DE DATOS ADMINISTRATIVOS
# ==============================================================================
elif st.session_state.current_step == 4:
    st.title("Datos administrativos del procedimiento")
    st.markdown("Complete la información administrativa necesaria para generar las Bases.")
    
    with st.form("datos_administrativos_form"):
        col_da1, col_da2 = st.columns(2)
        
        with col_da1:
            st.markdown("#### Sección 1: Identificación del procedimiento")
            nomenclatura = st.text_input("Nomenclatura del procedimiento (Obligatorio)", value=st.session_state.nomenclatura, placeholder="Ej. AS-002-2026-OSINERGMIN")
            tipo_proc = st.selectbox("Tipo de procedimiento", ["Adjudicación Simplificada", "Concurso Público", "Licitación Pública", "Contratación Directa"], index=["Adjudicación Simplificada", "Concurso Público", "Licitación Pública", "Contratación Directa"].index(st.session_state.tipo_procedimiento))
            num_proc = st.text_input("Número de proceso", value=st.session_state.numero_proceso)
            
            st.markdown("#### Sección 2: Monto")
            valor = st.number_input("Valor estimado o referencial (Obligatorio)", value=st.session_state.valor_estimado, min_value=0.0, step=1000.0)
            moneda = st.selectbox("Moneda", ["Soles (S/.)", "Dólares ($)"], index=["Soles (S/.)", "Dólares ($)"].index(st.session_state.moneda))
            fuente_val = st.text_input("Fuente del valor (Opcional)", value=st.session_state.fuente_val)
            
            st.markdown("#### Sección 3: Área solicitante")
            unidad = st.text_input("Unidad orgánica solicitante", value=st.session_state.unidad_solicitante)
            responsable = st.text_input("Responsable o contacto (Opcional)", value=st.session_state.responsable)
            
        with col_da2:
            st.markdown("#### Sección 4: Cronograma")
            f_conv = st.date_input("Fecha de convocatoria", value=st.session_state.fecha_convocatoria)
            f_cons = st.date_input("Fecha de consultas u observaciones", value=st.session_state.fecha_consultas)
            f_abs = st.date_input("Fecha de absolución", value=st.session_state.fecha_absolucion)
            f_pres = st.date_input("Fecha de presentación de ofertas", value=st.session_state.fecha_presentacion)
            f_eval = st.date_input("Fecha de evaluación", value=st.session_state.fecha_evaluacion)
            f_buena = st.date_input("Fecha de buena pro", value=st.session_state.fecha_buenapro)
            
            st.markdown("#### Sección 5: Financiamiento")
            fuente_finan = st.selectbox("Fuente de financiamiento", ["Recursos Directamente Recaudados (RDR)", "Recursos Ordinarios (RO)", "Transferencias y Donaciones"], index=["Recursos Directamente Recaudados (RDR)", "Recursos Ordinarios (RO)", "Transferencias y Donaciones"].index(st.session_state.fuente_financiamiento))
            obs_finan = st.text_area("Observaciones de Financiamiento", value=st.session_state.observaciones_finan, height=60)
            
            # Validación de Cronograma en vivo
            st.markdown("##### validación de Cronograma:")
            plazo_consultas = (f_cons - f_conv).days
            plazo_absolucion = (f_abs - f_cons).days
            plazo_ofertas = (f_pres - f_abs).days
            
            error_cronograma = False
            if f_conv > f_cons or f_cons > f_abs or f_abs > f_pres or f_pres > f_eval or f_eval > f_buena:
                st.markdown('<div class="error-panel">❌ Las fechas del cronograma no siguen una secuencia lógica temporal.</div>', unsafe_allow_html=True)
                error_cronograma = True
            elif plazo_ofertas < 3:
                st.markdown('<div class="alert-panel">⚠️ El plazo entre absolución y presentación de ofertas es menor a 3 días útiles.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-panel">✓ Coherencia del cronograma validada.</div>', unsafe_allow_html=True)

        col_form_btn1, col_form_btn2 = st.columns(2)
        with col_form_btn1:
            # Botón de guardar avance
            btn_guardar_avance = st.form_submit_button("Guardar avance")
        with col_form_btn2:
            btn_generar = st.form_submit_button("Generar borrador de Bases ➡️")
            
        if btn_guardar_avance:
            st.session_state.nomenclatura = nomenclatura
            st.session_state.tipo_procedimiento = tipo_proc
            st.session_state.numero_proceso = num_proc
            st.session_state.valor_estimado = valor
            st.session_state.moneda = moneda
            st.session_state.fuente_val = fuente_val
            st.session_state.unidad_solicitante = unidad
            st.session_state.responsable = responsable
            st.session_state.fecha_convocatoria = f_conv
            st.session_state.fecha_consultas = f_cons
            st.session_state.fecha_absolucion = f_abs
            st.session_state.fecha_presentacion = f_pres
            st.session_state.fecha_evaluacion = f_eval
            st.session_state.fecha_buenapro = f_buena
            st.session_state.fuente_financiamiento = fuente_finan
            st.session_state.observaciones_finan = obs_finan
            st.session_state.datos_admin_guardados = True
            st.success("Avance del expediente guardado en caché.")
            
        if btn_generar:
            if not nomenclatura or valor == 0.0:
                st.markdown('<div class="error-panel">Error: Campos obligatorios vacíos (Nomenclatura y Valor Estimado).</div>', unsafe_allow_html=True)
            elif error_cronograma:
                st.markdown('<div class="error-panel">Error: Corrija la coherencia del cronograma antes de generar.</div>', unsafe_allow_html=True)
            else:
                st.session_state.nomenclatura = nomenclatura
                st.session_state.tipo_procedimiento = tipo_proc
                st.session_state.numero_proceso = num_proc
                st.session_state.valor_estimado = valor
                st.session_state.moneda = moneda
                st.session_state.fuente_val = fuente_val
                st.session_state.unidad_solicitante = unidad
                st.session_state.responsable = responsable
                st.session_state.fecha_convocatoria = f_conv
                st.session_state.fecha_consultas = f_cons
                st.session_state.fecha_absolucion = f_abs
                st.session_state.fecha_presentacion = f_pres
                st.session_state.fecha_evaluacion = f_eval
                st.session_state.fecha_buenapro = f_buena
                st.session_state.fuente_financiamiento = fuente_finan
                st.session_state.observaciones_finan = obs_finan
                st.session_state.bases_generadas = True
                st.session_state.current_step = 5
                st.rerun()

    if st.button("⬅️ Volver a datos técnicos", key="back_to_tech"):
        st.session_state.current_step = 3
        st.rerun()

# ==============================================================================
# PANTALLA 5: VISTA PRELIMINAR DE BASES GENERADAS
# ==============================================================================
elif st.session_state.current_step == 5:
    st.title("Vista preliminar de Bases generadas")
    st.markdown("Revise el documento generado antes de descargarlo.")
    
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        st.markdown("#### Resumen del Expediente")
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; font-size: 0.9rem;">
            • <b>Expediente SIGED:</b> {st.session_state.expediente_input}<br>
            • <b>Plantilla utilizada:</b> {st.session_state.plantilla_final}<br>
            • <b>TDR fuente:</b> {st.session_state.tdr_nombre}<br>
            • <b>Valor Estimado:</b> {st.session_state.moneda} {st.session_state.valor_estimado:,.2f}<br>
            • <b>Área Solicitante:</b> {st.session_state.unidad_solicitante}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Estado del Documento:")
        st.markdown('<div class="success-panel"><b>✓ Borrador generado</b> | Listo para descargar</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert-panel">
            ⚠️ <b>Advertencia de revisión humana:</b> Este documento es un borrador y debe ser revisado por el área responsable de Osinergmin antes de su publicación oficial.
        </div>
        """, unsafe_allow_html=True)
        
        # [Paso 10] Checklist de Validación
        st.markdown("#### 📋 Checklist de Validación (Paso 10)")
        st.markdown("Por favor, revise y marque los ítems normativos para confirmar el borrador (Paso 11):")
        
        check_objeto = st.checkbox("El Objeto del TDR coincide con el registrado en SIGED.", key="ch_obj")
        check_plazo = st.checkbox("El Plazo de ejecución ha sido corroborado contra el TDR original.", key="ch_plaz")
        check_cronograma = st.checkbox("El Cronograma de hitos sigue los plazos y la secuencia de ley.", key="ch_cron")
        check_calificacion = st.checkbox("Los Requisitos de calificación han sido validados.", key="ch_calif")
        check_evaluacion = st.checkbox("Los Factores de evaluación están correctamente definidos.", key="ch_eval")
        check_financiamiento = st.checkbox("La Fuente de financiamiento cuenta con código presupuestal.", key="ch_fin")
        
        checklist_completado = check_objeto and check_plazo and check_cronograma and check_calificacion and check_evaluacion and check_financiamiento
        
        if not checklist_completado:
            st.markdown("""
            <div class="error-panel" style="margin-top:10px;">
                🔒 <b>Acceso Bloqueado (Paso 11 - Revisa/Confirma):</b> Debe completar todos los ítems del Checklist de Validación técnica para habilitar la descarga y cierre del expediente.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-panel" style="margin-top:10px;">
                🔓 <b>Validación Exitosa (Paso 11):</b> El borrador ha sido aprobado por el usuario Osinergmin. Se ha habilitado la descarga e integración (Paso 12).
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Acciones Disponibles")
        col_va1, col_va2 = st.columns(2)
        with col_va1:
            if st.button("Editar datos técnicos", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
            if st.button("Editar datos administrativos", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
        with col_va2:
            if st.button("Regenerar documento", use_container_width=True):
                with st.spinner("Regenerando borrador final de bases..."):
                    time.sleep(1.5)
                st.success("Bases regeneradas correctamente.")
            
            # Botón de descarga real del archivo generado [Paso 12]
            moneda_simbolo = "S/." if st.session_state.moneda == "Soles (S/.)" else "$"
            borrador_descarga = f"""BASES ADMINISTRATIVAS OFICIALES - OSINERGMIN
EXPEDIENTE: {st.session_state.expediente_input}
NOMENCLATURA: {st.session_state.nomenclatura}

OBJETO DE LA CONTRATACIÓN:
{st.session_state.datos_tecnicos['objeto']}

PLAZO DE EJECUCIÓN:
{st.session_state.datos_tecnicos['plazo']}

VALOR ESTIMADO:
{moneda_simbolo} {st.session_state.valor_estimado:,.2f}

CRONOGRAMA:
- Convocatoria: {st.session_state.fecha_convocatoria.strftime('%d/%m/%Y')}
- Consultas: {st.session_state.fecha_consultas.strftime('%d/%m/%Y')}
- Absolución: {st.session_state.fecha_absolucion.strftime('%d/%m/%Y')}
- Ofertas: {st.session_state.fecha_presentacion.strftime('%d/%m/%Y')}
- Buena pro: {st.session_state.fecha_buenapro.strftime('%d/%m/%Y')}
"""
            st.download_button(
                "📥 Descargar DOCX",
                borrador_descarga,
                file_name=f"Bases_{st.session_state.nomenclatura}.docx",
                use_container_width=True,
                disabled=not checklist_completado
            )
            
        if st.button("Finalizar y Guardar en Historial ➡️", use_container_width=True, disabled=not checklist_completado):
            with st.spinner("Guardando estado e integrando Base Final .DOC (Paso 12)..."):
                time.sleep(1.2)
            # Agregar al historial si no existe
            en_historial = any(h["expediente"] == st.session_state.expediente_input for h in st.session_state.historial_expedientes)
            if not en_historial:
                st.session_state.historial_expedientes.insert(0, {
                    "expediente": st.session_state.expediente_input,
                    "plantilla": st.session_state.plantilla_final,
                    "creacion": datetime.date.today().strftime('%d/%m/%Y'),
                    "modificacion": datetime.date.today().strftime('%d/%m/%Y'),
                    "responsable": f"{st.session_state.responsable.lower().replace(' ', '')}@osinergmin.gob.pe",
                    "estado": "Descargado" if checklist_completado else "Borrador generado"
                })
            st.session_state.current_step = 6
            st.rerun()

    with col_v2:
        st.markdown("#### Visor de Documento")
        
        # Simulación de la estructura final completa
        preview_text = f"""BASES ESTÁNDAR
PROCESO: {st.session_state.nomenclatura}
ADJUDICACIÓN SIMPLIFICADA N° {st.session_state.numero_proceso}

CAPÍTULO I: DE LA CONVOCATORIA
El Organismo Supervisor de la Inversión en Energía y Minería (OSINERGMIN) convoca al proceso de selección respectivo.
Cronograma:
1. Convocatoria: {st.session_state.fecha_convocatoria.strftime('%d/%m/%Y')}
2. Registro de participantes: {st.session_state.fecha_convocatoria.strftime('%d/%m/%Y')} en adelante.
3. Formulación de Consultas y Observaciones: {st.session_state.fecha_consultas.strftime('%d/%m/%Y')}
4. Absolución e Integración: {st.session_state.fecha_absolucion.strftime('%d/%m/%Y')}
5. Presentación de Ofertas: {st.session_state.fecha_presentacion.strftime('%d/%m/%Y')}
6. Otorgamiento de Buena Pro: {st.session_state.fecha_buenapro.strftime('%d/%m/%Y')}

CAPÍTULO II: OBJETO DE CONTRATACIÓN
Objeto: "{st.session_state.datos_tecnicos['objeto']}"
Valor Estimado: {st.session_state.moneda} {st.session_state.valor_estimado:,.2f}
Financiamiento: {st.session_state.fuente_financiamiento}

CAPÍTULO III: REQUERIMIENTOS TÉCNICOS MÍNIMOS
Plazo: {st.session_state.datos_tecnicos['plazo']}
Requisitos de Calificación:
{st.session_state.datos_tecnicos['requisitos_calificacion']}

CAPÍTULO IV: CRITERIOS DE EVALUACIÓN
{st.session_state.datos_tecnicos['factores_evaluacion']}
"""
        st.markdown(f'<div class="doc-preview"><pre style="color: #cbd5e1; white-space: pre-wrap;">{preview_text}</pre></div>', unsafe_allow_html=True)

# ==============================================================================
# PANTALLA 6: HISTORIAL Y DESCARGA
# ==============================================================================
elif st.session_state.current_step == 6:
    st.title("Historial de Bases generadas")
    st.markdown("Consulte procesos anteriores, retome avances y descargue documentos generados.")
    
    # Buscadores / Filtros
    col_fi1, col_fi2, col_fi3 = st.columns(3)
    with col_fi1:
        search_exp = st.text_input("Buscar por número de expediente:", placeholder="EXP-SIGED-...")
    with col_fi2:
        search_date = st.text_input("Buscar por fecha (DD/MM/AAAA):", placeholder="e.g. 12/06/2026")
    with col_fi3:
        search_user = st.text_input("Buscar por usuario / responsable:", placeholder="e.g. jortiz")
        
    # Lógica de filtrado
    df_historial = pd.DataFrame(st.session_state.historial_expedientes)
    
    if search_exp:
        df_historial = df_historial[df_historial["expediente"].str.contains(search_exp, case=False)]
    if search_date:
        df_historial = df_historial[df_historial["creacion"].str.contains(search_date, case=False)]
    if search_user:
        df_historial = df_historial[df_historial["responsable"].str.contains(search_user, case=False)]
        
    # Renderizar tabla
    st.markdown("#### Expedientes Registrados")
    
    for idx, row in df_historial.iterrows():
        col_row1, col_row2, col_row3 = st.columns([3, 1, 1.5])
        with col_row1:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <b>Expediente:</b> <code>{row['expediente']}</code> | <b>Plantilla:</b> {row['plantilla']}<br>
                <span style="font-size: 0.8rem; color:#64748b;"><b>Creación:</b> {row['creacion']} | <b>Modificación:</b> {row['modificacion']} | <b>Responsable:</b> {row['responsable']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_row2:
            badge_color = "#e0f2fe" if row['estado'] == "Borrador generado" else ("#fef3c7" if row['estado'] == "En progreso" else "#dcfce7")
            text_color = "#0369a1" if row['estado'] == "Borrador generado" else ("#b45309" if row['estado'] == "En progreso" else "#15803d")
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <span style="background-color: {badge_color}; color: {text_color}; font-weight: bold; font-size: 0.8rem; padding: 5px 10px; border-radius: 12px;">{row['estado']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_row3:
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                # Botón Retomar
                if st.button("Retomar", key=f"retomar_{idx}"):
                    st.session_state.expediente_input = row["expediente"]
                    st.session_state.expediente_valido = True
                    st.session_state.plantilla_final = row["plantilla"]
                    st.session_state.current_step = 3 # Ir a revisión de datos técnicos
                    st.rerun()
            with col_act2:
                # Descargar DOCX
                st.download_button(
                    "DOCX",
                    f"Bases de prueba del expediente {row['expediente']}",
                    file_name=f"Bases_{row['expediente']}.docx",
                    key=f"dl_{idx}"
                )
                
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Iniciar Nuevo Proceso", type="primary"):
        st.session_state.expediente_input = ""
        st.session_state.expediente_valido = False
        st.session_state.expediente_data = None
        st.session_state.bases_generadas = False
        st.session_state.current_step = 1
        st.rerun()
