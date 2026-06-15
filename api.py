from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import ollama
import os
import io
import tempfile
import shutil
import database
from docxtpl import DocxTemplate
from docling.document_converter import DocumentConverter

# ==============================================================================
# INTEGRACIÓN SIGED - PATRÓN ADAPTER (Sección 3.10 de stack.md)
# ==============================================================================
MOCK_SIGED_DATA = {
    "20260000982": {
        "numero": "20260000982",
        "asunto": "Servicio de Consultoría para la Gestión y Mitigación de Riesgos Informáticos en Osinergmin",
        "tdr": "TDR_Consultoria_Ciberseguridad_2026.pdf",
        "fecha": "10/06/2026",
        "tdr_text": """TÉRMINOS DE REFERENCIA (TDR)
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
Por retraso en la entrega de informes del servicio se aplicará una penalidad de 0.20%."""
    },
    "20260000411": {
        "numero": "20260000411",
        "asunto": "Adquisición de Servidores de Alta Disponibilidad para el Data Center de Osinergmin",
        "tdr": "TDR_Adquisicion_Servidores_2026.pdf",
        "fecha": "05/06/2026",
        "tdr_text": """TÉRMINOS DE REFERENCIA (TDR)
ADQUISICIÓN DE SERVIDORES DE ALTA DISPONIBILIDAD
CÓDIGO INTERNO: TDR-GSTI-2026-011

1. OBJETO DE LA CONTRATACIÓN
Adquisición de 4 servidores físicos de alta disponibilidad incluyendo licenciamiento y soporte por 3 años para el Data Center de Osinergmin.

2. PLAZO DE EJECUCIÓN
El plazo de entrega de los servidores físicos instalados y configurados será de 60 días calendario.

3. SISTEMA DE CONTRATACIÓN
El presente proceso de selección se regirá por el sistema de Suma Alzada.

4. REQUERIMIENTO COMPLETO Y ESPECIFICACIONES
- Servidores físicos de 64 núcleos, 512GB RAM y almacenamiento SSD enterprise en configuración cluster.
- Soporte técnico local certificado directamente por el fabricante del hardware de los servidores.

5. REQUISITOS DE CALIFICACIÓN
- Experiencia de la empresa en la provisión de servidores y almacenamiento empresarial durante los últimos 3 años.
- Soporte técnico local certificado directamente por el fabricante del hardware de los servidores.

6. PENALIDADES
Se aplicará la penalidad por mora establecida en el Artículo 161 del Reglamento de la Ley de Contrataciones del Estado."""
    }
}

import requests

class SIGEDAdapter:
    """
    Adaptador para la integración del Asistente de Bases con el Sistema de Gestión Documentaria (SIGED) de Osinergmin.
    Utiliza llamadas reales de API REST dirigidas al simulador del SIGED.
    """
    def __init__(self, base_url="http://127.0.0.1:8000/api/v1/siged"):
        self.base_url = base_url

    def consultar_expediente(self, numero: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/expedientes/{numero}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error al conectar con la API REST de SIGED (GET /expedientes): {e}")
            return None

    def descargar_tdr(self, filename: str) -> Optional[str]:
        try:
            url = f"{self.base_url}/documentos/{filename}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("content")
            return None
        except Exception as e:
            print(f"Error al conectar con la API REST de SIGED (GET /documentos): {e}")
            return None

# ==============================================================================
# LIFECYCLE / LIFESPAN DE FASTAPI
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar la base de datos relacional local en el arranque (RNF-4)
    database.init_db()
    # Inicializar la base de datos vectorial Qdrant local
    try:
        import qdrant_service
        qdrant_service.init_qdrant()
    except Exception as e:
        print(f"Error al inicializar Qdrant en lifespan: {e}")
    yield

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Asistente de Bases Estándar - Osinergmin",
    description="Servicio backend para la extracción de información de TDRs y generación de texto utilizando Gemma 3 via Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# Definir la URL de Ollama (por defecto localhost:11434)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_HOST

MODEL_NAME = "gemma3:1b"

# ==============================================================================
# MODELOS DE DATOS (PYDANTIC)
# ==============================================================================

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="El prompt o pregunta para el modelo LLM")
    system_prompt: Optional[str] = Field(
        "Eres un asistente experto en contrataciones del sector público peruano y Osinergmin.",
        description="Prompt del sistema para establecer el rol y las reglas del modelo"
    )
    temperature: Optional[float] = Field(0.2, description="Temperatura de muestreo (creatividad)")

class GenerateResponse(BaseModel):
    response: str = Field(..., description="La respuesta textual generada por el modelo")

# Esquemas para Recomendaciones Vectoriales con Qdrant (RAG)
class RecommendRequest(BaseModel):
    text: str = Field(..., description="Texto de consulta para buscar similitudes en Qdrant")
    categoria: Optional[str] = Field(None, description="Categoría opcional (Bienes, Servicios, Consultoría) para filtrar")
    limit: Optional[int] = Field(3, description="Límite máximo de sugerencias a retornar")

class ClauseRecommendation(BaseModel):
    texto: str
    categoria: str
    tipo_clausula: str
    fuente: str
    score: float

class RecommendResponse(BaseModel):
    success: bool
    recommendations: List[ClauseRecommendation]

# Esquema enriquecido para estructurar la extracción del TDR conforme a los requisitos (RF-3)
class TDRExtractedData(BaseModel):
    objeto: str = Field(..., description="Objeto de la contratación (Bienes, Servicios o Consultoría) y una breve descripción")
    plazo: str = Field(..., description="Plazo de ejecución detallado (ej. 180 días calendario, 12 meses)")
    valor_estimado: Optional[float] = Field(None, description="Valor estimado de la contratación en soles (S/.), o null si no se menciona")
    moneda: Optional[str] = Field("PEN", description="Moneda del valor estimado (habitualmente PEN)")
    sistema_contratacion: Optional[str] = Field("Suma Alzada", description="Sistema de contratación (e.g. Suma Alzada, Precios Unitarios, Esquema Mixto)")
    requerimiento_completo: Optional[str] = Field(None, description="Resumen o lista de los entregables principales y el alcance técnico")
    requisitos_calificacion: List[str] = Field(
        default=[], 
        description="Lista de requisitos de calificación mínimos exigidos para el postor (experiencia, certificaciones, personal)"
    )
    factores_evaluacion: List[str] = Field(
        default=[],
        description="Lista de factores de evaluación técnica o mejoras propuestas sugeridas en el documento"
    )

class ExtractRequest(BaseModel):
    tdr_text: str = Field(..., description="Contenido de texto completo o parcial extraído del TDR")

class ExtractResponse(BaseModel):
    success: bool
    data: TDRExtractedData
    raw_response: Optional[str] = None

# Esquema para generación de archivo .docx
class DocxGenerationRequest(BaseModel):
    nomenclatura: str
    numero_expediente: str
    objeto: str
    plazo: str
    valor_estimado: float
    moneda: str
    unidad_solicitante: str
    responsable: str
    fecha_convocatoria: str
    fecha_consultas: str
    fecha_absolucion: str
    fecha_presentacion: str
    fecha_buenapro: str
    fuente_financiamiento: str
    requisitos_calificacion: str
    factores_evaluacion: str
    plantilla_usada: Optional[str] = "base"
    sistema_contratacion: Optional[str] = "Suma Alzada"

# ==============================================================================
# ENDPOINTS DE LA API
# ==============================================================================

@app.get("/")
def read_root():
    """
    Ruta raíz para verificar la disponibilidad de la API y el estado de la conexión a Ollama.
    """
    try:
        # Verificar conexión rápida con Ollama listando modelos
        models = ollama.list()
        ollama_status = "Conectado"
        available_models = [m.model for m in models.models]
    except Exception as e:
        ollama_status = f"Error de conexión: {str(e)}"
        available_models = []

    return {
        "message": "Servicio de API del Asistente de Bases Estándar - Osinergmin",
        "ollama_status": ollama_status,
        "model_configured": MODEL_NAME,
        "available_models_in_ollama": available_models,
        "api_docs_url": "/docs"
    }

# --- Endpoint de simulación de API REST de SIGED (Simula el servidor externo) ---
@app.get("/api/v1/siged/expedientes/{numero}")
def external_siged_get_expediente(numero: str):
    if numero in MOCK_SIGED_DATA:
        data = MOCK_SIGED_DATA[numero]
        return {
            "numero": data["numero"],
            "asunto": data["asunto"],
            "tdr": data["tdr"],
            "fecha": data["fecha"]
        }
    raise HTTPException(status_code=404, detail="Expediente no encontrado en el sistema SIGED")

@app.get("/api/v1/siged/documentos/{filename}")
def external_siged_get_documento(filename: str):
    for key, data in MOCK_SIGED_DATA.items():
        if data["tdr"] == filename:
            return {
                "filename": filename,
                "content": data["tdr_text"]
            }
    raise HTTPException(status_code=404, detail="Documento de TDR no encontrado en el servidor de archivos de SIGED")

# --- Endpoints que la UI consume para consultar SIGED a través de nuestro Adapter ---
@app.get("/siged/consultar/{numero}")
def siged_consultar_expediente(numero: str):
    adapter = SIGEDAdapter()
    res = adapter.consultar_expediente(numero)
    if res:
        return {"success": True, "data": res}
    raise HTTPException(status_code=404, detail="Expediente no encontrado en SIGED")

@app.get("/siged/descargar/{filename}")
def siged_descargar_tdr(filename: str):
    adapter = SIGEDAdapter()
    content = adapter.descargar_tdr(filename)
    if content:
        return {"success": True, "content": content}
    raise HTTPException(status_code=404, detail="No se pudo descargar el TDR desde SIGED")

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """
    Endpoint de generación de texto general utilizando Gemma 3.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            options={
                "temperature": request.temperature
            }
        )
        return GenerateResponse(response=response.message.content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al invocar el modelo en Ollama: {str(e)}. "
                   f"Asegúrese de que el servicio de Ollama está corriendo y el modelo '{MODEL_NAME}' está descargado."
        )

@app.post("/extract", response_model=ExtractResponse)
async def extract_tdr_data(request: ExtractRequest):
    """
    Endpoint específico para el procesamiento de TDRs.
    Toma el texto crudo del TDR y extrae la información estructurada bajo el formato TDRExtractedData.
    """
    system_prompt = (
        "Eres un analista experto en contrataciones del estado peruano (Osinergmin). "
        "Tu tarea es analizar el texto de un Término de Referencia (TDR) provisto por el usuario "
        "y extraer la información técnica de relevancia de forma estructurada según el esquema JSON solicitado. "
        "Sé preciso y no inventes datos. Si el valor estimado no se menciona, déjalo como null. "
        "Extrae en 'factores_evaluacion' las certificaciones opcionales o SLA adicionales si existen."
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analiza este TDR y extrae los datos correspondientes:\n\n{request.tdr_text}"}
            ],
            format=TDRExtractedData.model_json_schema(),
            options={
                "temperature": 0.1
            }
        )
        
        raw_content = response.message.content
        extracted_data = TDRExtractedData.model_validate_json(raw_content)
        
        # Registrar auditoría (RNF-1)
        try:
            database.log_audit_action(
                usuario_id="sistema",
                accion="EXTRACT_TDR_TEXT",
                numero_expediente=None,
                detalles=f"Extracción estructurada exitosa sobre texto de TDR ({len(request.tdr_text)} caracteres)."
            )
        except Exception as db_err:
            print(f"Error al registrar auditoría: {db_err}")
            
        return ExtractResponse(
            success=True,
            data=extracted_data,
            raw_response=raw_content
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el procesamiento de extracción estructurada: {str(e)}. "
                   f"Asegúrese de tener el modelo '{MODEL_NAME}' instalado y corriendo en Ollama."
        )

@app.post("/extract_file", response_model=ExtractResponse)
async def extract_from_file(file: UploadFile = File(...)):
    """
    Endpoint específico para el procesamiento de TDRs cargados en archivos físicos (PDF, DOCX, imagen).
    Usa IBM Docling para extraer el texto y layout en Markdown y Ollama + Gemma 3 para estructurarlo.
    """
    temp_dir = "/data/proyectos/proyecto-bases/scratch"
    os.makedirs(temp_dir, exist_ok=True)
    
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=temp_dir) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_file_path = tmp.name
        
    try:
        # Convertir con Docling
        converter = DocumentConverter()
        result = converter.convert(temp_file_path)
        markdown_text = result.document.export_to_markdown()
        
        # Analizar con LLM Gemma 3 local
        system_prompt = (
            "Eres un analista experto en contrataciones del estado peruano (Osinergmin). "
            "Tu tarea es analizar el texto de un Término de Referencia (TDR) provisto por el usuario "
            "y extraer la información técnica de relevancia de forma estructurada según el esquema JSON solicitado. "
            "Sé preciso y no inventes datos. Si el valor estimado no se menciona, déjalo como null. "
            "Extrae en 'factores_evaluacion' las certificaciones opcionales o SLA adicionales si existen."
        )
        
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analiza este TDR y extrae los datos correspondientes:\n\n{markdown_text}"}
            ],
            format=TDRExtractedData.model_json_schema(),
            options={
                "temperature": 0.1
            }
        )
        
        raw_content = response.message.content
        extracted_data = TDRExtractedData.model_validate_json(raw_content)
        
        # Registrar auditoría (RNF-1)
        try:
            database.log_audit_action(
                usuario_id="sistema",
                accion="EXTRACT_TDR_FILE",
                numero_expediente=None,
                detalles=f"Extracción y OCR local con Docling exitosa sobre archivo: {file.filename}."
            )
        except Exception as db_err:
            print(f"Error al registrar auditoría: {db_err}")
            
        return ExtractResponse(
            success=True,
            data=extracted_data,
            raw_response=markdown_text
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el procesamiento de OCR/Extracción con Docling y LLM: {str(e)}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/generate_docx")
async def generate_docx(request: DocxGenerationRequest):
    """
    Endpoint para la generación de Bases formateadas en Word (.docx) utilizando docxtpl.
    """
    try:
        # Mapeo de nombres de plantilla a archivos físicos
        template_map = {
            "Bienes - Normal": "plantilla_bienes_normal.docx",
            "Bienes - Abreviado": "plantilla_bienes_abreviado.docx",
            "Servicios - Normal": "plantilla_servicios_normal.docx",
            "Servicios - Abreviado": "plantilla_servicios_abreviado.docx",
            "Consultoría - Normal": "plantilla_consultoria_normal.docx",
            "Consultoría - Abreviado": "plantilla_consultoria_abreviado.docx",
        }
        
        template_name = request.plantilla_usada or "base"
        template_file = template_map.get(template_name, "plantilla_base.docx")
        
        template_path = template_file
        if not os.path.exists(template_path):
            template_path = "plantilla_base.docx"
            
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró la plantilla '{template_path}' en el directorio de trabajo."
            )
            
        doc = DocxTemplate(template_path)
        
        # Registrar auditoría (RNF-1)
        try:
            database.log_audit_action(
                usuario_id=request.responsable or "sistema",
                accion="GENERATE_DOCX",
                numero_expediente=request.numero_expediente,
                detalles=f"Generación de borrador de bases en Word. Nomenclatura: {request.nomenclatura}. Plantilla: {template_name}."
            )
        except Exception as db_err:
            print(f"Error al registrar auditoría: {db_err}")
            
        context = {
            "nomenclatura": request.nomenclatura,
            "numero_expediente": request.numero_expediente,
            "objeto": request.objeto,
            "plazo": request.plazo,
            "sistema_contratacion": request.sistema_contratacion or "Suma Alzada",
            "valor_estimado": f"{request.valor_estimado:,.2f}",
            "moneda": request.moneda,
            "unidad_solicitante": request.unidad_solicitante,
            "responsable": request.responsable,
            "fecha_convocatoria": request.fecha_convocatoria,
            "fecha_consultas": request.fecha_consultas,
            "fecha_absolucion": request.fecha_absolucion,
            "fecha_presentacion": request.fecha_presentacion,
            "fecha_buenapro": request.fecha_buenapro,
            "fuente_financiamiento": request.fuente_financiamiento,
            "requisitos_calificacion": request.requisitos_calificacion,
            "factores_evaluacion": request.factores_evaluacion
        }
        
        doc.render(context)
        
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        filename = f"Bases_{request.nomenclatura.replace('/', '_')}.docx"
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el documento de Bases Word: {str(e)}"
        )

@app.post("/recommend_clauses", response_model=RecommendResponse)
def recommend_clauses(request: RecommendRequest):
    """
    Endpoint para buscar cláusulas y normas estándar similares en Qdrant (RAG).
    Permite filtrar por categoría del procedimiento (Bienes, Servicios, Consultoría).
    """
    try:
        import qdrant_service
        results = qdrant_service.query_similar_clauses(
            query_text=request.text,
            category_filter=request.categoria,
            limit=request.limit
        )
        
        # Registrar auditoría (RNF-1)
        try:
            database.log_audit_action(
                usuario_id="sistema",
                accion="RECOMMEND_CLAUSES",
                numero_expediente=None,
                detalles=f"Consulta semántica en Qdrant: '{request.text[:80]}' (filtro: {request.categoria})."
            )
        except Exception as db_err:
            print(f"Error al registrar auditoría: {db_err}")
            
        recommendations = [
            ClauseRecommendation(
                texto=r["texto"],
                categoria=r["categoria"],
                tipo_clausula=r["tipo_clausula"],
                fuente=r["fuente"],
                score=r["score"]
            )
            for r in results
        ]
        return RecommendResponse(success=True, recommendations=recommendations)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar recomendaciones en la Vector DB Qdrant: {str(e)}"
        )
