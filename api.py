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
class SIGEDAdapter:
    """
    Adaptador para la integración del Asistente de Bases con el Sistema de Gestión Documentaria (SIGED) de Osinergmin.
    
    ESTRATEGIAS DE INTEGRACIÓN POR ESCENARIO:
    
    1. ESCENARIO MVP / PRUEBAS (Implementado Actual):
       - Se simula la existencia de expedientes utilizando un diccionario estático de TDRs en memoria 
         indexado por claves de 11 dígitos (AAAAXXXXXXX) en el frontend.
       - Permite el desarrollo del asistente de forma desacoplada y offline.
       
    2. ESCENARIO DE PRODUCCIÓN A (API REST / SOAP Oficial de Osinergmin):
       - Si la Gerencia de Sistemas (GSTI) habilita servicios de interoperabilidad, este adaptador 
         utilizará un cliente HTTP asíncrono (ej. httpx) o cliente SOAP (ej. zeep) con reintentos para:
         a) Validar la existencia de un expediente mediante HTTP GET /api/v1/expedientes/{numero}.
         b) Consultar la lista de documentos asociados al expediente.
         c) Descargar el TDR digital (PDF o DOCX) desde el gestor documental a un almacenamiento temporal.
         
    3. ESCENARIO DE PRODUCCIÓN B (RPA - Robotic Process Automation con Playwright/Selenium):
       - Si no existe API y se requiere integración automática, el adaptador instanciará un navegador 
         headless con Playwright para emular las acciones del operador humano:
         a) Login automatizado en la intranet de SIGED de Osinergmin.
         b) Navegación y búsqueda del expediente usando el número de 11 dígitos.
         c) Detección del enlace del archivo de TDR por palabra clave o tipo documental.
         d) Descarga automática del archivo al disco del servidor para procesarlo con el OCR/NLP.
    """
    def __init__(self):
        # Inicialización de clientes HTTP o controladores de navegador según configuración
        pass

    def consultar_expediente(self, numero: str) -> Optional[dict]:
        # Simulación de respuesta mock
        if numero == "20260000982":
            return {
                "numero": "20260000982",
                "asunto": "Servicio de Consultoría para la Gestión y Mitigación de Riesgos Informáticos en Osinergmin",
                "tdr": "TDR_Consultoria_Ciberseguridad_2026.pdf",
                "fecha": "10/06/2026"
            }
        elif numero == "20260000411":
            return {
                "numero": "20260000411",
                "asunto": "Adquisición de Servidores de Alta Disponibilidad para el Data Center de Osinergmin",
                "tdr": "TDR_Adquisicion_Servidores_2026.pdf",
                "fecha": "05/06/2026"
            }
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
        template_path = "plantilla_base.docx"
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=404, 
                detail="No se encontró la plantilla 'plantilla_base.docx' en el directorio de trabajo."
            )
            
        doc = DocxTemplate(template_path)
        
        context = {
            "nomenclatura": request.nomenclatura,
            "numero_expediente": request.numero_expediente,
            "objeto": request.objeto,
            "plazo": request.plazo,
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
