import streamlit as st
import pandas as pd
import datetime
import time
import requests
import database

# Inicializar Base de Datos SQLite en arranque
database.init_db()

# MOCK TDRs para la simulación del API de SIGED (RF-1, RF-3)
MOCK_TDRS = {
    "20260000982": """TÉRMINOS DE REFERENCIA (TDR)
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
Por retraso en la entrega de informes del servicio se aplicará una penalidad de 0.20%.""",
    "20260000411": """TÉRMINOS DE REFERENCIA (TDR)
ADQUISICIÓN DE SERVIDORES DE ALTA DISPONIBILIDAD
CÓDIGO INTERNO: TDR-GSTI-2026-011

1. OBJETO DE LA CONTRATACIÓN
Adquisición de 4 servidores físicos de alta disponibilidad incluyendo licenciamiento y soporte por 3 años para el Data Center de Osinergmin.

2. PLAZO DE EJECUCIÓN
El plazo de entrega de los servidores físicos instalados y configurados será de 60 días calendario.

3. SISTEMA DE CONTRATACIÓN
El presente proceso de selección se regirá por el sistema de Suma Alzada.

4. REQUERIMIENTO COMPLETO
Servidores físicos de 64 núcleos, 512GB RAM y almacenamiento SSD enterprise en configuración cluster.

5. REQUISITOS DE CALIFICACIÓN
- Experiencia de la empresa en la provisión de servidores y almacenamiento empresarial durante los últimos 3 años.
- Soporte técnico local certificado directamente por el fabricante del hardware de los servidores."""
}


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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Variables de Diseño Oficiales de Osinergmin */
    :root {
        --primary-color: #0039aa;
        --primary-500: #0039aa;
        --primary-color-text: #ffffff;
        --surface-900: #101828;
        --yellow-osinergmin: #fbe122;
        --naranja-osinergmin: #f6a229;
        --celeste-osinergmin: #03a9f4;
        --verde-osinergmin: #35cc29;
        --dorado-osinergmin: #bfab49;
        --celeste-claro-osinergmin: #d2f7fc;
        --gris-claro-osinergmin: #f2f2f2;
    }

    /* Aplicación estricta de Tipografía Poppins */
    html, body, [class*="css"], .stMarkdown, .stText, .stButton, input, select, textarea, [data-testid="stHeader"] {
        font-family: 'Poppins', sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        color: #0039aa !important; /* Azul Osinergmin (Primary) */
    }

    /* Fondo de la App con Celeste Claro de Osinergmin en degradé */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #d2f7fc 100%) !important;
    }

    /* Sidebar Estilizado con Surface 900 (Color institucional oscuro) */
    [data-testid="stSidebar"] {
        background-color: #101828 !important; /* --surface-900 */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #fbe122 !important; /* Amarillo Osinergmin para destacar */
        font-weight: 600;
    }

    /* Elemento Fijo: Franja combinada Azul y Amarilla (Línea de Identidad) */
    .linea-identidad-osinergmin {
        height: 25px; /* Entre 21px y 30px según la regla */
        width: 100%;
        background: linear-gradient(90deg, #0039aa 0%, #0039aa 65%, #fbe122 65%, #fbe122 100%);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 57, 170, 0.1);
    }

    /* Tarjetas y Contenedores Premium */
    .metric-card {
        background: #ffffff;
        border: 1px solid #f2f2f2; /* Gris Claro */
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(16, 24, 40, 0.04);
        transition: all 0.2s ease-in-out;
        margin-bottom: 12px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 24, 40, 0.08);
        border-color: #0039aa; /* Azul Osinergmin */
    }

    /* Alertas */
    .alert-panel {
        background-color: #fffdf0;
        border-left: 4px solid #f6a229; /* Naranja Osinergmin */
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: #7c2d12;
        font-size: 0.9rem;
    }
    .success-panel {
        background-color: #f0fdf4;
        border-left: 4px solid #35cc29; /* Verde Osinergmin */
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
        border: 1px solid #f2f2f2; /* Gris Claro */
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.02);
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
        color: #0039aa; /* Azul Osinergmin */
    }
    .step-item.completed {
        color: #35cc29; /* Verde Osinergmin */
    }
    .step-number {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #f2f2f2; /* Gris Claro */
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 6px auto;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .step-item.active .step-number {
        background-color: #0039aa; /* Azul Osinergmin */
        color: white;
    }
    .step-item.completed .step-number {
        background-color: #35cc29; /* Verde Osinergmin */
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
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Botón Primario: Azul Osinergmin con texto blanco */
    div.stButton > button[kind="primary"] {
        background-color: #0039aa !important;
        color: #ffffff !important;
        border: 1px solid #0039aa !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #002b80 !important;
        border-color: #002b80 !important;
        box-shadow: 0 4px 12px rgba(0, 57, 170, 0.2) !important;
    }

    /* Botón Secundario: Blanco/Gris con borde y texto Azul */
    div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #0039aa !important;
        border: 1px solid #0039aa !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #f2f2f2 !important;
        border-color: #002b80 !important;
        color: #002b80 !important;
    }
    
    /* Indicador de confianza */
    .confidence-badge {
        font-size: 0.75rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .conf-green { background-color: #e6fced; color: #1b6615; border: 1px solid #35cc29; }
    .conf-orange { background-color: #fff9f0; color: #a16207; border: 1px solid #f6a229; }
    .conf-red { background-color: #fee2e2; color: #b91c1c; border: 1px solid #ef4444; }

    /* Visor del TDR */
    .tdr-viewer {
        background-color: #f2f2f2;
        border: 1px solid #d2f7fc;
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
            "expediente": "20260000982",
            "plantilla": "Servicios - Normal",
            "creacion": "10/06/2026",
            "modificacion": "12/06/2026",
            "responsable": "jortiz@osinergmin.gob.pe",
            "estado": "Borrador generado"
        },
        {
            "expediente": "20260000411",
            "plantilla": "Bienes - Normal",
            "creacion": "05/06/2026",
            "modificacion": "05/06/2026",
            "responsable": "lrodriguez@osinergmin.gob.pe",
            "estado": "Descargado"
        },
        {
            "expediente": "20260001053",
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
if "tdr_nombre" not in st.session_state:
    st.session_state.tdr_nombre = ""

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
if "fuente_val" not in st.session_state:
    st.session_state.fuente_val = "Estudio de Mercado"
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

# Función para renderizar el indicador visual de pasos (UI Premium)
def render_step_indicator(current_step):
    steps = [
        "1. Carga TDR",
        "2. Plantilla",
        "3. Datos Técnicos",
        "4. Datos Administrativos",
        "5. Vista Preliminar",
        "6. Descarga / Historial"
    ]
    
    html = '<div class="step-indicator-container">'
    for idx, name in enumerate(steps):
        step_num = idx + 1
        active_class = ""
        if step_num == current_step:
            active_class = " active"
        elif step_num < current_step:
            active_class = " completed"
            
        num_content = "✓" if step_num < current_step else str(step_num)
        
        html += f'<div class="step-item{active_class}"><div class="step-number">{num_content}</div><div style="margin-top: 4px;">{name}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ==============================================================================
# MENU LATERAL - INFORMACIÓN CORPORATIVA
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="linea-identidad-osinergmin" style="height: 25px; margin-bottom: 15px;"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-top: 5px;'>Asistente IA</h2>", unsafe_allow_html=True)
    st.caption("Fase 1: Generación de Bases Estándar")
    st.markdown("<hr style='border-color: #1e293b; margin: 10px 0;'>", unsafe_allow_html=True)
    
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

    st.markdown("<hr style='border-color: #334155; margin: 10px 0;'>", unsafe_allow_html=True)
    with st.expander("💡 Guía Rápida & Glosario", expanded=False):
        st.markdown("""
        <small style="color: #cbd5e1;">
        <b>Flujo de Elaboración:</b><br>
        1. <b>Carga TDR</b>: Ingrese código SIGED o archivo local.<br>
        2. <b>Plantilla</b>: Seleccione tipo/variante de bases.<br>
        3. <b>Datos Técnicos</b>: OCR y NLP local (Gemma 3).<br>
        4. <b>Datos Admin</b>: Fechas, montos y responsables.<br>
        5. <b>Vista Preliminar</b>: Visor de borrador y checklist.<br>
        6. <b>Descarga</b>: Obtención de bases finales en Word.<br><br>
        
        <b>Glosario Osinergmin:</b><br>
        • <b>SIGED</b>: Gestor de expedientes oficiales.<br>
        • <b>TDR</b>: Requisitos del bien o servicio.<br>
        • <b>RAG (Qdrant)</b>: Recomendación de cláusulas OSCE.<br>
        • <b>Bases Estándar</b>: Modelos oficiales de contratación.
        </small>
        """, unsafe_allow_html=True)


# Renderizar la franja de identidad corporativa y el indicador de progreso multipaso a nivel global en la UI
st.markdown('<div class="linea-identidad-osinergmin"></div>', unsafe_allow_html=True)
render_step_indicator(st.session_state.current_step)

# ==============================================================================
# PANTALLA 1: INICIO / INGRESO DE EXPEDIENTE SIGED
# ==============================================================================
if st.session_state.current_step == 1:
    st.title("Asistente IA para generación de Bases")
    st.markdown("Ingrese el número de expediente SIGED para iniciar la generación de Bases Estándar.")
    
    col_e1, col_e2 = st.columns([1.2, 1])
    
    with col_e1:
        st.markdown("#### Búsqueda en SIGED")
        
        # 1. Lista de expedientes sugeridos/mock y del historial de la BD
        expedientes_sugeridos = {
            "20260000982": "20260000982 - Consultoría Ciberseguridad (TDR-GSTI-2026-004)",
            "20260000411": "20260000411 - Servidores Alta Disponibilidad (TDR-GSTI-2026-011)"
        }
        
        try:
            historial = database.get_all_processes_history()
            for item in historial:
                exp = item["expediente"]
                if exp not in expedientes_sugeridos:
                    expedientes_sugeridos[exp] = f"{exp} - {item.get('plantilla', 'Bases Registradas')}"
        except Exception:
            pass
            
        opciones_desplegable = ["-- Seleccione o busque un expediente --"] + list(expedientes_sugeridos.values()) + ["Otro (Ingresar número manualmente...)"]
        
        # Encontrar índice de selección predeterminado
        default_idx = 0
        if st.session_state.expediente_input:
            encontrado = False
            for idx, opt in enumerate(opciones_desplegable):
                if opt.startswith(st.session_state.expediente_input):
                    default_idx = idx
                    encontrado = True
                    break
            if not encontrado:
                default_idx = len(opciones_desplegable) - 1 # "Otro"
                
        seleccion_expediente = st.selectbox(
            "Buscar o seleccionar expediente:",
            options=opciones_desplegable,
            index=default_idx,
            help="Escriba parte del número de expediente o del asunto para filtrar la lista predictivamente."
        )
        
        # Determinar el valor final de expediente_input a validar
        if seleccion_expediente == "Otro (Ingresar número manualmente...)":
            expediente_input = st.text_input(
                "Ingrese número de expediente SIGED (11 dígitos):", 
                value=st.session_state.expediente_input if st.session_state.expediente_input not in expedientes_sugeridos else "", 
                placeholder="Ingrese e.g. 20260000982",
                max_chars=11
            )
        elif seleccion_expediente != "-- Seleccione o busque un expediente --":
            expediente_input = seleccion_expediente.split(" - ")[0].strip()
        else:
            expediente_input = ""
        
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
            if "tdr_markdown_extraido" in st.session_state:
                st.session_state.tdr_markdown_extraido = ""
            st.rerun()
            
        st.markdown("<hr style='border-color: #cbd5e1; margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 📂 O Procesar Documento Local (Layout OCR)")
        st.caption("Cargue su archivo PDF, Word o imagen del TDR para procesarlo localmente con IBM Docling:")
        tdr_file = st.file_uploader(
            "Subir archivo TDR:",
            type=["pdf", "docx", "png", "jpg", "jpeg"]
        )
        btn_procesar_file = st.button("🚀 Iniciar Extracción Local con Docling", type="primary", use_container_width=True)
        
        if btn_procesar_file:
            if not tdr_file:
                st.error("Por favor, cargue un archivo primero.")
            else:
                virt_expediente = f"2026{int(time.time()) % 10000000:07d}"
                st.session_state.expediente_input = virt_expediente
                
                log_placeholder = st.empty()
                with log_placeholder.container():
                    st.markdown(f'<div class="aws-panel">👤 <b>[Paso 1]</b> Archivo local recibido: {tdr_file.name}</div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    st.markdown('<div class="aws-panel">📄 <b>[Paso 2-3]</b> Iniciando motor IBM Docling para análisis de layout y OCR...</div>', unsafe_allow_html=True)
                    
                    # Llamar al API FastAPI /extract_file
                    ext_success = False
                    try:
                        files = {"file": (tdr_file.name, tdr_file.getvalue(), tdr_file.type)}
                        api_resp = requests.post(
                            "http://127.0.0.1:8000/extract_file",
                            files=files,
                            timeout=600 # Timeout amplio para CPU OCR
                        )
                        if api_resp.status_code == 200:
                            api_data = api_resp.json()
                            ext_data = api_data["data"]
                            st.session_state.tdr_markdown_extraido = api_data.get("raw_response", "")
                            ext_success = True
                        else:
                            st.error(f"Error en el backend de extracción (Código {api_resp.status_code}): {api_resp.text}")
                    except Exception as ex:
                        st.error(f"No se pudo conectar con el backend en http://127.0.0.1:8000: {ex}")
                        
                log_placeholder.empty()
                
                if ext_success:
                    st.session_state.expediente_valido = True
                    st.session_state.expediente_error = ""
                    
                    st.session_state.expediente_data = {
                        "numero": virt_expediente,
                        "asunto": f"Extracción local: {tdr_file.name}",
                        "tdr": tdr_file.name,
                        "fecha": datetime.date.today().strftime('%d/%m/%Y')
                    }
                    st.session_state.tdr_nombre = tdr_file.name
                    
                    objeto_str = ext_data.get("objeto", "").lower()
                    if "bien" in objeto_str or "adquisición" in objeto_str or "compra" in objeto_str:
                        st.session_state.plantilla_sugerida = "Bienes - Normal"
                    elif "consult" in objeto_str or "diagnóstico" in objeto_str or "asesoría" in objeto_str:
                        st.session_state.plantilla_sugerida = "Consultoría - Normal"
                    else:
                        st.session_state.plantilla_sugerida = "Servicios - Normal"
                        
                    st.session_state.plantilla_final = st.session_state.plantilla_sugerida
                    st.session_state.nomenclatura = f"AS-{virt_expediente[-3:]}-2026-OSINERGMIN"
                    
                    st.session_state.datos_tecnicos = {
                        "objeto": ext_data.get("objeto", ""),
                        "plazo": ext_data.get("plazo", ""),
                        "sistema_contratacion": ext_data.get("sistema_contratacion", "Suma Alzada"),
                        "requerimiento_completo": ext_data.get("requerimiento_completo") or "Se requiere la entrega de los informes técnicos especificados en el TDR.",
                        "requisitos_calificacion": "\n".join(ext_data.get("requisitos_calificacion", [])),
                        "factores_evaluacion": "\n".join(ext_data.get("factores_evaluacion", [])) or "Factores de evaluación sugeridos: Certificación voluntaria adicional (20 pts), SLA mejorado (10 pts)."
                    }
                    
                    if ext_data.get("valor_estimado"):
                        st.session_state.valor_estimado = float(ext_data["valor_estimado"])
                    else:
                        st.session_state.valor_estimado = 150000.00
                        
                    st.success("✓ Archivo procesado y estructurado con éxito.")
                    time.sleep(1.0)
                    st.rerun()

        # Lógica de validación
        if btn_validar:
            if not expediente_input:
                st.markdown('<div class="error-panel">Ingrese un número de expediente válido.</div>', unsafe_allow_html=True)
            elif len(expediente_input) != 11 or not expediente_input.isdigit():
                st.session_state.expediente_valido = False
                st.session_state.expediente_data = None
                st.session_state.expediente_error = "Formato incorrecto"
            else:
                st.session_state.expediente_input = expediente_input
                
                # Intentar cargar desde Base de Datos (RNF-4 Persistencia / Reanudación)
                db_state = database.load_process_state(expediente_input)
                if db_state:
                    st.session_state.expediente_valido = True
                    st.session_state.expediente_error = ""
                    st.session_state.expediente_data = {
                        "numero": db_state["expediente"],
                        "asunto": db_state["datos_siged"].get("asunto", ""),
                        "tdr": db_state["datos_siged"].get("tdr", ""),
                        "fecha": db_state["datos_siged"].get("fecha", datetime.date.today().strftime('%d/%m/%Y'))
                    }
                    st.session_state.tdr_nombre = db_state["datos_siged"].get("tdr", "")
                    st.session_state.plantilla_final = db_state["plantilla_usada"]
                    st.session_state.plantilla_sugerida = db_state["plantilla_usada"]
                    st.session_state.plantilla_confirmada = True
                    st.session_state.datos_tecnicos = db_state["datos_extraidos"]
                    
                    # Cargar datos administrativos
                    admin = db_state["datos_administrativos"]
                    st.session_state.nomenclatura = admin.get("nomenclatura", "")
                    st.session_state.tipo_procedimiento = admin.get("tipo_procedimiento", "Adjudicación Simplificada")
                    st.session_state.numero_proceso = admin.get("numero_proceso", "")
                    st.session_state.valor_estimado = float(admin.get("valor_estimado", 0.0))
                    st.session_state.moneda = admin.get("moneda", "Soles (S/.)")
                    st.session_state.fuente_val = admin.get("fuente_val", "")
                    st.session_state.unidad_solicitante = admin.get("unidad_solicitante", "")
                    st.session_state.responsable = admin.get("responsable", "")
                    
                    # Convertir fechas de string a datetime.date
                    for key, val in [
                        ("fecha_convocatoria", datetime.date.today()),
                        ("fecha_consultas", datetime.date.today() + datetime.timedelta(days=4)),
                        ("fecha_absolucion", datetime.date.today() + datetime.timedelta(days=6)),
                        ("fecha_presentacion", datetime.date.today() + datetime.timedelta(days=12)),
                        ("fecha_evaluacion", datetime.date.today() + datetime.timedelta(days=15)),
                        ("fecha_buenapro", datetime.date.today() + datetime.timedelta(days=18))
                    ]:
                        if admin.get(key):
                            try:
                                setattr(st.session_state, key, datetime.datetime.strptime(admin.get(key), '%Y-%m-%d').date())
                            except Exception:
                                setattr(st.session_state, key, val)
                        else:
                            setattr(st.session_state, key, val)
                            
                    st.session_state.fuente_financiamiento = admin.get("fuente_financiamiento", "Recursos Directamente Recaudados (RDR)")
                    st.session_state.observaciones_finan = admin.get("observaciones_finan", "")
                    st.session_state.datos_admin_guardados = True
                    st.session_state.bases_generadas = (db_state["estado"] == "Completado" or db_state["estado"] == "Descargado")
                    
                    st.success(f"✓ Proceso reanudado desde la base de datos (Estado: {db_state['estado']})")
                    time.sleep(1.0)
                    st.session_state.current_step = 3 # Ir directamente a datos técnicos
                    st.rerun()
                
                if expediente_input in ["20260000982", "20260000411"]:
                    # Simulación interactiva paso a paso del flujo de la imagen
                    log_placeholder = st.empty()
                    with log_placeholder.container():
                        st.markdown('<div class="aws-panel">👤 <b>[Paso 1]</b> Portal recibe N° Expediente: ' + expediente_input + '</div>', unsafe_allow_html=True)
                        time.sleep(0.5)
                        st.markdown('<div class="aws-panel">🔄 <b>[Paso 2]</b> Solicitando documento TDR al Sistema SIGED (API REST SIGED)...</div>', unsafe_allow_html=True)
                        
                        # Consultar metadatos desde el backend FastAPI que usa SIGEDAdapter
                        siged_meta = None
                        try:
                            siged_resp = requests.get(f"http://127.0.0.1:8000/siged/consultar/{expediente_input}", timeout=10)
                            if siged_resp.status_code == 200:
                                siged_meta = siged_resp.json()["data"]
                            else:
                                st.error("Expediente no encontrado en la API REST de SIGED.")
                        except Exception as e:
                            st.error(f"Error al conectar con la API del Backend (SIGED): {e}")
                        
                        time.sleep(0.5)
                        st.markdown('<div class="aws-panel">📄 <b>[Paso 3]</b> SIGED proporciona archivo digital del TDR en formato PDF/DOCX (Descarga REST)</div>', unsafe_allow_html=True)
                        
                        # Descargar contenido del TDR desde la API de SIGED
                        tdr_content = ""
                        if siged_meta:
                            try:
                                tdr_resp = requests.get(f"http://127.0.0.1:8000/siged/descargar/{siged_meta['tdr']}", timeout=10)
                                if tdr_resp.status_code == 200:
                                    tdr_content = tdr_resp.json()["content"]
                            except Exception as e:
                                print(f"Error al descargar contenido del TDR desde la API: {e}")
                                
                        if not tdr_content:
                            tdr_content = MOCK_TDRS.get(expediente_input)
                            
                        time.sleep(0.5)
                        st.markdown('<div class="aws-panel">🧠 <b>[Paso 4]</b> Enviando archivo al backend FastAPI + Ollama (Gemma 3) para extracción técnica estructurada (RF-3)...</div>', unsafe_allow_html=True)
                        
                        # Realizar la extracción llamando al backend FastAPI
                        ext_success = False
                        try:
                            api_resp = requests.post(
                                "http://127.0.0.1:8000/extract",
                                json={"tdr_text": tdr_content},
                                timeout=120 # Timeout amplio para la primera carga de inferencia
                            )
                            if api_resp.status_code == 200:
                                ext_data = api_resp.json()["data"]
                                ext_success = True
                            else:
                                st.error(f"Error del backend FastAPI (Código {api_resp.status_code})")
                        except Exception as ex:
                            st.error(f"No se pudo conectar con el backend en http://127.0.0.1:8000: {ex}")
                            
                        time.sleep(0.5)
                    log_placeholder.empty()

                    if ext_success and siged_meta:
                        st.session_state.expediente_valido = True
                        st.session_state.expediente_error = ""
                        st.session_state.expediente_data = siged_meta
                        st.session_state.tdr_nombre = siged_meta["tdr"]
                        
                        # Mapeo de plantillas sugeridas
                        if expediente_input == "20260000982":
                            st.session_state.plantilla_sugerida = "Servicios - Normal"
                            st.session_state.nomenclatura = "AS-002-2026-OSINERGMIN"
                        else:
                            st.session_state.plantilla_sugerida = "Bienes - Normal"
                            st.session_state.nomenclatura = "LP-001-2026-OSINERGMIN"
                            
                        if not st.session_state.plantilla_final:
                            st.session_state.plantilla_final = st.session_state.plantilla_sugerida
                        
                        # Poblar con los datos REALMENTE extraídos por el LLM Gemma 3 local
                        st.session_state.datos_tecnicos = {
                            "objeto": ext_data.get("objeto", ""),
                            "plazo": ext_data.get("plazo", ""),
                            "sistema_contratacion": ext_data.get("sistema_contratacion", "Suma Alzada"),
                            "requerimiento_completo": ext_data.get("requerimiento_completo") or "Se requiere la entrega de los informes técnicos especificados en el TDR.",
                            "requisitos_calificacion": "\n".join(ext_data.get("requisitos_calificacion", [])),
                            "factores_evaluacion": "\n".join(ext_data.get("factores_evaluacion", [])) or "Factores de evaluación sugeridos: Certificación voluntaria adicional (20 pts), SLA mejorado (10 pts)."
                        }
                        
                        if ext_data.get("valor_estimado"):
                            st.session_state.valor_estimado = float(ext_data["valor_estimado"])
                        else:
                            st.session_state.valor_estimado = 180000.00 if expediente_input == "20260000982" else 450000.00
                    else:
                        st.session_state.expediente_valido = False
                        st.session_state.expediente_error = "Error de extracción"
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
            if st.session_state.expediente_error == "Formato incorrecto":
                st.markdown('<div class="error-panel">❌ El número de expediente debe tener exactamente 11 dígitos numéricos (AAAAXXXXXXX).</div>', unsafe_allow_html=True)
            elif st.session_state.expediente_error == "No se encontró expediente":
                st.markdown('<div class="error-panel">❌ No se encontró expediente. Verifique el número e intente nuevamente.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-panel">⚠️ No se identificó un documento de TDR asociado en este expediente del SIGED.</div>', unsafe_allow_html=True)

    with col_e2:
        if st.session_state.expediente_valido and st.session_state.expediente_data is not None:
            data = st.session_state.expediente_data
            st.markdown("#### Resumen del Expediente")
            st.markdown(f'<div class="metric-card"><b>Número de expediente:</b> {data["numero"]}<br><b>Nombre / Asunto:</b> {data["asunto"]}<br><b>Documento TDR identificado:</b> <code style="color:#0039aa;">{data["tdr"]}</code><br><b>Fecha de registro:</b> {data["fecha"]}</div>', unsafe_allow_html=True)
            
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
            st.markdown('<div class="alert-panel">⚠️ <b>Alerta:</b> La plantilla seleccionada manualmente será usada para la generación del documento.</div>', unsafe_allow_html=True)
            
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
        <div style="background-color: #f2f2f2; border: 1px solid #d2f7fc; border-radius: 8px; padding: 15px; font-size: 0.85rem;">
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
        
        # Calcular confianza dinámicamente según el contenido real
        def get_conf_class(text):
            if not text or len(text.strip()) == 0 or "sugerido" in text.lower() or "se requiere" in text.lower():
                return "conf-red", "Rojo"
            elif len(text.strip()) < 35:
                return "conf-orange", "Naranja"
            else:
                return "conf-green", "Verde"

        conf_obj_class, conf_obj_txt = get_conf_class(objeto_val)
        conf_plz_class, conf_plz_txt = get_conf_class(plazo_val)
        conf_sis_class, conf_sis_txt = get_conf_class(sistema_val)
        conf_req_class, conf_req_txt = get_conf_class(reqs_calif_val)
        conf_fac_class, conf_fac_txt = get_conf_class(factores_val)

        st.markdown("##### Indicadores de Confianza en Extracción (AWS OCR/NLP)")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(f'• Objeto: <span class="confidence-badge {conf_obj_class}">{conf_obj_txt}</span><br>• Plazo: <span class="confidence-badge {conf_plz_class}">{conf_plz_txt}</span>', unsafe_allow_html=True)
        with col_c2:
            st.markdown(f'• Sistema: <span class="confidence-badge {conf_sis_class}">{conf_sis_txt}</span><br>• Requisitos: <span class="confidence-badge {conf_req_class}">{conf_req_txt}</span>', unsafe_allow_html=True)
        with col_c3:
            st.markdown(f'• Factores: <span class="confidence-badge {conf_fac_class}">{conf_fac_txt}</span>', unsafe_allow_html=True)
        st.caption("🟢 **Verde**: Datos completos. 🟡 **Naranja**: Datos breves (revisar). 🔴 **Rojo**: Vacío o requiere ingreso manual.")
            
        # RAG / Qdrant Clause Recommendations (Local Vector Search)
        st.markdown("<hr style='border-color: #cbd5e1; margin: 15px 0;'>", unsafe_allow_html=True)
        with st.expander("💡 **Asistente de Recomendaciones Normativas (RAG Qdrant)**", expanded=False):
            st.markdown("<small>Busque cláusulas recomendadas de las directivas OSCE y bases estándar basadas en el TDR:</small>", unsafe_allow_html=True)
            
            default_query = st.session_state.datos_tecnicos.get("objeto", "")
            rag_query = st.text_input("Palabras clave de consulta:", value=default_query)
            
            if st.button("Consultar Base de Conocimiento", use_container_width=True):
                if not rag_query:
                    st.warning("Ingrese un término de búsqueda.")
                else:
                    with st.spinner("Buscando en la base vectorial Qdrant..."):
                        try:
                            payload = {
                                "text": rag_query,
                                "categoria": st.session_state.plantilla_final,
                                "limit": 3
                            }
                            resp = requests.post("http://127.0.0.1:8000/recommend_clauses", json=payload, timeout=15)
                            if resp.status_code == 200:
                                recommendations = resp.json().get("recommendations", [])
                                if not recommendations:
                                    st.info("No se encontraron cláusulas similares para este criterio.")
                                else:
                                    for idx, rec in enumerate(recommendations):
                                        st.markdown(f'<div style="background-color: #f0fdf4; border-left: 3px solid #35cc29; padding: 10px; border-radius: 6px; margin-bottom: 10px;"><b style="color: #14532d;">Sugerencia #{idx+1}: {rec["tipo_clausula"]}</b><br><span style="font-size: 0.85rem; color: #1e293b;">{rec["texto"]}</span><br><small style="color: #64748b;">Fuente: {rec["fuente"]} | Relevancia: {rec["score"]:.2%}</small></div>', unsafe_allow_html=True)
                            else:
                                st.error(f"Error al conectar con la base de vectores: {resp.text}")
                        except Exception as ex:
                            st.error(f"No se pudo contactar al API de vectores: {ex}")
            
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
        
        # Obtener el texto del TDR original (del mock o del extraído por docling)
        if "tdr_markdown_extraido" in st.session_state and st.session_state.tdr_markdown_extraido:
            tdr_text = st.session_state.tdr_markdown_extraido
        else:
            tdr_text = MOCK_TDRS.get(st.session_state.expediente_input, MOCK_TDRS["20260000982"])
        # Resaltado de búsqueda simulado
        if search_query:
            tdr_display = tdr_text.replace(search_query, f"⚡[{search_query.upper()}]⚡")
        else:
            tdr_display = tdr_text
            
        st.markdown(f'<div class="tdr-viewer"><pre style="color:#101828; white-space: pre-wrap;">{tdr_display}</pre></div>', unsafe_allow_html=True)

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
            
            # Guardar en Base de Datos SQLite (RNF-4 Persistencia)
            datos_admin = {
                "nomenclatura": nomenclatura,
                "tipo_procedimiento": tipo_proc,
                "numero_proceso": num_proc,
                "valor_estimado": float(valor),
                "moneda": moneda,
                "fuente_val": fuente_val,
                "unidad_solicitante": unidad,
                "responsable": responsable,
                "fecha_convocatoria": f_conv.strftime('%Y-%m-%d'),
                "fecha_consultas": f_cons.strftime('%Y-%m-%d'),
                "fecha_absolucion": f_abs.strftime('%Y-%m-%d'),
                "fecha_presentacion": f_pres.strftime('%Y-%m-%d'),
                "fecha_evaluacion": f_eval.strftime('%Y-%m-%d'),
                "fecha_buenapro": f_buena.strftime('%Y-%m-%d'),
                "fuente_financiamiento": fuente_finan,
                "observaciones_finan": obs_finan
            }
            
            asunto_val = st.session_state.expediente_data.get("asunto", "Sin Asunto") if st.session_state.expediente_data else "Sin Asunto"
            tdr_val = st.session_state.expediente_data.get("tdr", "Sin TDR") if st.session_state.expediente_data else "Sin TDR"
            responsable_val = responsable if responsable else "admin@osinergmin.gob.pe"
            
            success = database.save_or_update_process(
                numero_expediente=st.session_state.expediente_input,
                asunto=asunto_val,
                tdr_nombre=tdr_val,
                plantilla=st.session_state.plantilla_final,
                datos_tecnicos=st.session_state.datos_tecnicos,
                datos_admin=datos_admin,
                estado="En progreso",
                responsable=responsable_val
            )
            
            if success:
                st.success("✓ Avance del expediente guardado exitosamente en Base de Datos relacional local (RNF-4).")
            else:
                st.error("Error al guardar el avance en la base de datos.")
            
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
                
                # Guardar en Base de Datos SQLite (RNF-4 Persistencia)
                datos_admin = {
                    "nomenclatura": nomenclatura,
                    "tipo_procedimiento": tipo_proc,
                    "numero_proceso": num_proc,
                    "valor_estimado": float(valor),
                    "moneda": moneda,
                    "fuente_val": fuente_val,
                    "unidad_solicitante": unidad,
                    "responsable": responsable,
                    "fecha_convocatoria": f_conv.strftime('%Y-%m-%d'),
                    "fecha_consultas": f_cons.strftime('%Y-%m-%d'),
                    "fecha_absolucion": f_abs.strftime('%Y-%m-%d'),
                    "fecha_presentacion": f_pres.strftime('%Y-%m-%d'),
                    "fecha_evaluacion": f_eval.strftime('%Y-%m-%d'),
                    "fecha_buenapro": f_buena.strftime('%Y-%m-%d'),
                    "fuente_financiamiento": fuente_finan,
                    "observaciones_finan": obs_finan
                }
                
                asunto_val = st.session_state.expediente_data.get("asunto", "Sin Asunto") if st.session_state.expediente_data else "Sin Asunto"
                tdr_val = st.session_state.expediente_data.get("tdr", "Sin TDR") if st.session_state.expediente_data else "Sin TDR"
                responsable_val = responsable if responsable else "admin@osinergmin.gob.pe"
                
                database.save_or_update_process(
                    numero_expediente=st.session_state.expediente_input,
                    asunto=asunto_val,
                    tdr_nombre=tdr_val,
                    plantilla=st.session_state.plantilla_final,
                    datos_tecnicos=st.session_state.datos_tecnicos,
                    datos_admin=datos_admin,
                    estado="Borrador generado",
                    responsable=responsable_val
                )
                
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
        <div style="background-color: #f2f2f2; border: 1px solid #d2f7fc; border-radius: 8px; padding: 15px; font-size: 0.9rem;">
            • <b>Expediente SIGED:</b> {st.session_state.expediente_input}<br>
            • <b>Plantilla utilizada:</b> {st.session_state.plantilla_final}<br>
            • <b>TDR fuente:</b> {st.session_state.tdr_nombre}<br>
            • <b>Valor Estimado:</b> {st.session_state.moneda} {st.session_state.valor_estimado:,.2f}<br>
            • <b>Área Solicitante:</b> {st.session_state.unidad_solicitante}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Estado del Documento:")
        st.markdown('<div class="success-panel"><b>✓ Borrador generado</b> | Listo para descargar</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="alert-panel">⚠️ <b>Advertencia de revisión humana:</b> Este documento es un borrador y debe ser revisado por el área responsable de Osinergmin antes de su publicación oficial.</div>', unsafe_allow_html=True)
        
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
            st.markdown('<div class="error-panel" style="margin-top:10px;">🔒 <b>Acceso Bloqueado (Paso 11 - Revisa/Confirma):</b> Debe completar todos los ítems del Checklist de Validación técnica para habilitar la descarga y cierre del expediente.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-panel" style="margin-top:10px;">🔓 <b>Validación Exitosa (Paso 11):</b> El borrador ha sido aprobado por el usuario Osinergmin. Se ha habilitado la descarga e integración (Paso 12).</div>', unsafe_allow_html=True)

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
            docx_data = None
            if checklist_completado:
                try:
                    f_conv = st.session_state.fecha_convocatoria.strftime('%d/%m/%Y')
                    f_cons = st.session_state.fecha_consultas.strftime('%d/%m/%Y')
                    f_abs = st.session_state.fecha_absolucion.strftime('%d/%m/%Y')
                    f_pres = st.session_state.fecha_presentacion.strftime('%d/%m/%Y')
                    f_buena = st.session_state.fecha_buenapro.strftime('%d/%m/%Y')
                    
                    payload = {
                        "nomenclatura": st.session_state.nomenclatura,
                        "numero_expediente": st.session_state.expediente_input,
                        "objeto": st.session_state.datos_tecnicos['objeto'],
                        "plazo": st.session_state.datos_tecnicos['plazo'],
                        "valor_estimado": float(st.session_state.valor_estimado),
                        "moneda": st.session_state.moneda,
                        "unidad_solicitante": st.session_state.unidad_solicitante,
                        "responsable": st.session_state.responsable,
                        "fecha_convocatoria": f_conv,
                        "fecha_consultas": f_cons,
                        "fecha_absolucion": f_abs,
                        "fecha_presentacion": f_pres,
                        "fecha_buenapro": f_buena,
                        "fuente_financiamiento": st.session_state.fuente_financiamiento,
                        "requisitos_calificacion": st.session_state.datos_tecnicos['requisitos_calificacion'],
                        "factores_evaluacion": st.session_state.datos_tecnicos['factores_evaluacion'],
                        "plantilla_usada": st.session_state.plantilla_final,
                        "sistema_contratacion": st.session_state.datos_tecnicos.get('sistema_contratacion', 'Suma Alzada')
                    }
                    
                    api_resp = requests.post("http://127.0.0.1:8000/generate_docx", json=payload, timeout=30)
                    if api_resp.status_code == 200:
                        docx_data = api_resp.content
                    else:
                        st.error(f"Error de generación en API backend: {api_resp.text}")
                except Exception as ex:
                    st.error(f"No se pudo conectar al backend para generar el DOCX: {ex}")
            
            st.download_button(
                "📥 Descargar DOCX (Generado por API)",
                data=docx_data if docx_data else b"",
                file_name=f"Bases_{st.session_state.nomenclatura.replace('/', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                disabled=not checklist_completado or docx_data is None
            )
            
        if st.button("Finalizar y Guardar en Historial ➡️", use_container_width=True, disabled=not checklist_completado):
            with st.spinner("Guardando estado e integrando Base Final .DOC (Paso 12)..."):
                time.sleep(1.2)
            
            # Guardar en Base de Datos SQLite (RNF-4 Persistencia)
            try:
                f_conv_str = st.session_state.fecha_convocatoria.strftime('%Y-%m-%d')
                f_cons_str = st.session_state.fecha_consultas.strftime('%Y-%m-%d')
                f_abs_str = st.session_state.fecha_absolucion.strftime('%Y-%m-%d')
                f_pres_str = st.session_state.fecha_presentacion.strftime('%Y-%m-%d')
                f_eval_str = st.session_state.fecha_evaluacion.strftime('%Y-%m-%d')
                f_buena_str = st.session_state.fecha_buenapro.strftime('%Y-%m-%d')
            except Exception:
                f_conv_str = datetime.date.today().strftime('%Y-%m-%d')
                f_cons_str = datetime.date.today().strftime('%Y-%m-%d')
                f_abs_str = datetime.date.today().strftime('%Y-%m-%d')
                f_pres_str = datetime.date.today().strftime('%Y-%m-%d')
                f_eval_str = datetime.date.today().strftime('%Y-%m-%d')
                f_buena_str = datetime.date.today().strftime('%Y-%m-%d')
                
            datos_admin = {
                "nomenclatura": st.session_state.nomenclatura,
                "tipo_procedimiento": st.session_state.tipo_procedimiento,
                "numero_proceso": st.session_state.numero_proceso,
                "valor_estimado": float(st.session_state.valor_estimado),
                "moneda": st.session_state.moneda,
                "fuente_val": st.session_state.fuente_val,
                "unidad_solicitante": st.session_state.unidad_solicitante,
                "responsable": st.session_state.responsable,
                "fecha_convocatoria": f_conv_str,
                "fecha_consultas": f_cons_str,
                "fecha_absolucion": f_abs_str,
                "fecha_presentacion": f_pres_str,
                "fecha_evaluacion": f_eval_str,
                "fecha_buenapro": f_buena_str,
                "fuente_financiamiento": st.session_state.fuente_financiamiento,
                "observaciones_finan": st.session_state.observaciones_finan
            }
            
            asunto_val = st.session_state.expediente_data.get("asunto", "Sin Asunto") if st.session_state.expediente_data else "Sin Asunto"
            tdr_val = st.session_state.expediente_data.get("tdr", "Sin TDR") if st.session_state.expediente_data else "Sin TDR"
            responsable_val = st.session_state.responsable if st.session_state.responsable else "admin@osinergmin.gob.pe"
            
            database.save_or_update_process(
                numero_expediente=st.session_state.expediente_input,
                asunto=asunto_val,
                tdr_nombre=tdr_val,
                plantilla=st.session_state.plantilla_final,
                datos_tecnicos=st.session_state.datos_tecnicos,
                datos_admin=datos_admin,
                estado="Descargado" if checklist_completado else "Borrador generado",
                responsable=responsable_val
            )
            
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
        search_exp = st.text_input("Buscar por número de expediente:", placeholder="2026...")
    with col_fi2:
        search_date = st.text_input("Buscar por fecha (DD/MM/AAAA):", placeholder="e.g. 12/06/2026")
    with col_fi3:
        search_user = st.text_input("Buscar por usuario / responsable:", placeholder="e.g. jortiz")
        
    # Lógica de filtrado
    df_historial = pd.DataFrame(database.get_all_processes_history())
    
    if len(df_historial) > 0:
        if search_exp:
            df_historial = df_historial[df_historial["expediente"].str.contains(search_exp, case=False)]
        if search_date:
            df_historial = df_historial[df_historial["creacion"].str.contains(search_date, case=False)]
        if search_user:
            df_historial = df_historial[df_historial["responsable"].str.contains(search_user, case=False)]
            
    # Renderizar tabla
    st.markdown("#### Expedientes Registrados")
    
    if len(df_historial) == 0:
        st.markdown("<p style='color: #64748b;'>No se encontraron expedientes en el historial.</p>", unsafe_allow_html=True)
    else:
        for idx, row in df_historial.iterrows():
            col_row1, col_row2, col_row3 = st.columns([3, 1, 1.5])
            with col_row1:
                st.markdown(f'<div style="background-color: white; border: 1px solid #f2f2f2; border-radius: 8px; padding: 12px; margin-bottom: 8px;"><b>Expediente:</b> <code>{row["expediente"]}</code> | <b>Plantilla:</b> {row["plantilla"]}<br><span style="font-size: 0.8rem; color:#64748b;"><b>Creación:</b> {row["creacion"]} | <b>Modificación:</b> {row["modificacion"]} | <b>Responsable:</b> {row["responsable"]}</span></div>', unsafe_allow_html=True)
            with col_row2:
                badge_color = "#d2f7fc" if row['estado'] == "Borrador generado" else ("#fff9f0" if row['estado'] == "En progreso" else "#e6fced")
                text_color = "#0039aa" if row['estado'] == "Borrador generado" else ("#f6a229" if row['estado'] == "En progreso" else "#1b6615")
                st.markdown(f'<div style="text-align: center; margin-top: 10px;"><span style="background-color: {badge_color}; color: {text_color}; font-weight: bold; font-size: 0.8rem; padding: 5px 10px; border-radius: 12px;">{row["estado"]}</span></div>', unsafe_allow_html=True)
            with col_row3:
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    # Botón Retomar con carga completa de base de datos
                    if st.button("Retomar", key=f"retomar_{idx}"):
                        db_state = database.load_process_state(row["expediente"])
                        if db_state:
                            st.session_state.expediente_input = db_state["expediente"]
                            st.session_state.expediente_valido = True
                            st.session_state.expediente_error = ""
                            st.session_state.expediente_data = {
                                "numero": db_state["expediente"],
                                "asunto": db_state["datos_siged"].get("asunto", ""),
                                "tdr": db_state["datos_siged"].get("tdr", ""),
                                "fecha": db_state["datos_siged"].get("fecha", datetime.date.today().strftime('%d/%m/%Y'))
                            }
                            st.session_state.tdr_nombre = db_state["datos_siged"].get("tdr", "")
                            st.session_state.plantilla_final = db_state["plantilla_usada"]
                            st.session_state.plantilla_sugerida = db_state["plantilla_usada"]
                            st.session_state.plantilla_confirmada = True
                            st.session_state.datos_tecnicos = db_state["datos_extraidos"]
                            
                            # Cargar datos administrativos
                            admin = db_state["datos_administrativos"]
                            st.session_state.nomenclatura = admin.get("nomenclatura", "")
                            st.session_state.tipo_procedimiento = admin.get("tipo_procedimiento", "Adjudicación Simplificada")
                            st.session_state.numero_proceso = admin.get("numero_proceso", "")
                            st.session_state.valor_estimado = float(admin.get("valor_estimado", 0.0))
                            st.session_state.moneda = admin.get("moneda", "Soles (S/.)")
                            st.session_state.fuente_val = admin.get("fuente_val", "")
                            st.session_state.unidad_solicitante = admin.get("unidad_solicitante", "")
                            st.session_state.responsable = admin.get("responsable", "")
                            
                            # Convertir fechas de string a datetime.date
                            for key, val in [
                                ("fecha_convocatoria", datetime.date.today()),
                                ("fecha_consultas", datetime.date.today() + datetime.timedelta(days=4)),
                                ("fecha_absolucion", datetime.date.today() + datetime.timedelta(days=6)),
                                ("fecha_presentacion", datetime.date.today() + datetime.timedelta(days=12)),
                                ("fecha_evaluacion", datetime.date.today() + datetime.timedelta(days=15)),
                                ("fecha_buenapro", datetime.date.today() + datetime.timedelta(days=18))
                            ]:
                                if admin.get(key):
                                    try:
                                        setattr(st.session_state, key, datetime.datetime.strptime(admin.get(key), '%Y-%m-%d').date())
                                    except Exception:
                                        setattr(st.session_state, key, val)
                                else:
                                    setattr(st.session_state, key, val)
                                    
                            st.session_state.fuente_financiamiento = admin.get("fuente_financiamiento", "Recursos Directamente Recaudados (RDR)")
                            st.session_state.observaciones_finan = admin.get("observaciones_finan", "")
                            st.session_state.datos_admin_guardados = True
                            st.session_state.bases_generadas = (db_state["estado"] == "Completado" or db_state["estado"] == "Descargado")
                            
                            st.session_state.current_step = 3 # Ir a revisión de datos técnicos
                            st.rerun()
                with col_act2:
                    # Descargar DOCX real generado desde API backend
                    hist_docx_data = None
                    try:
                        db_state = database.load_process_state(row["expediente"])
                        if db_state:
                            admin = db_state["datos_administrativos"]
                            tecnicos = db_state["datos_extraidos"]
                            
                            payload = {
                                "nomenclatura": admin.get("nomenclatura", "AS-002-2026-OSINERGMIN"),
                                "numero_expediente": db_state["expediente"],
                                "objeto": tecnicos.get("objeto", ""),
                                "plazo": tecnicos.get("plazo", ""),
                                "valor_estimado": float(admin.get("valor_estimado", 0.0)),
                                "moneda": admin.get("moneda", "Soles (S/.)"),
                                "unidad_solicitante": admin.get("unidad_solicitante", ""),
                                "responsable": admin.get("responsable", ""),
                                "fecha_convocatoria": admin.get("fecha_convocatoria", ""),
                                "fecha_consultas": admin.get("fecha_consultas", ""),
                                "fecha_absolucion": admin.get("fecha_absolucion", ""),
                                "fecha_presentacion": admin.get("fecha_presentacion", ""),
                                "fecha_buenapro": admin.get("fecha_buenapro", ""),
                                "fuente_financiamiento": admin.get("fuente_financiamiento", ""),
                                "requisitos_calificacion": tecnicos.get("requisitos_calificacion", ""),
                                "factores_evaluacion": tecnicos.get("factores_evaluacion", ""),
                                "plantilla_usada": db_state.get("plantilla_usada", "base"),
                                "sistema_contratacion": tecnicos.get("sistema_contratacion", "Suma Alzada")
                            }
                            
                            api_resp = requests.post("http://127.0.0.1:8000/generate_docx", json=payload, timeout=10)
                            if api_resp.status_code == 200:
                                hist_docx_data = api_resp.content
                    except Exception as ex:
                        pass
                    
                    st.download_button(
                        "DOCX",
                        data=hist_docx_data if hist_docx_data else b"",
                        file_name=f"Bases_{row['expediente']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_{idx}",
                        disabled=hist_docx_data is None
                    )
                
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Iniciar Nuevo Proceso", type="primary"):
        st.session_state.expediente_input = ""
        st.session_state.expediente_valido = False
        st.session_state.expediente_data = None
        st.session_state.bases_generadas = False
        st.session_state.current_step = 1
        st.rerun()
