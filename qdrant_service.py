from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
import time

QDRANT_DB_PATH = "/data/proyectos/proyecto-bases/qdrant_db"

def get_qdrant_client():
    """Retorna el cliente local de Qdrant persistido en disco."""
    os.makedirs(QDRANT_DB_PATH, exist_ok=True)
    return QdrantClient(path=QDRANT_DB_PATH)

def init_qdrant():
    """Inicializa la colección de Qdrant y la puebla si está vacía."""
    client = get_qdrant_client()
    collection_name = "plantillas_osinergmin"
    
    # En Qdrant local, las colecciones se crean automáticamente al agregar documentos,
    # pero podemos asegurarnos de que la colección esté lista y poblada.
    try:
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
    except Exception:
        exists = False
        
    if not exists:
        print(f"Creando colección '{collection_name}' en Qdrant...")
        
        # Cláusulas legales estándar de Osinergmin / OSCE para RAG
        mock_clauses = [
            # BIENES
            {
                "documento": "La entrega de los bienes se realizará en el almacén central de Osinergmin dentro del plazo establecido. La conformidad será otorgada por la Oficina de Administración dentro de los 8 días de recibido el informe de conformidad técnica.",
                "metadata": {"categoria": "Bienes", "tipo_clausula": "Plazo y Conformidad", "fuente": "Directiva OSCE N° 001-2025"}
            },
            {
                "documento": "Requisito de Calificación - Experiencia del Postor: El postor debe acreditar una facturación acumulada por un monto equivalente a dos (2) veces el valor estimado de la contratación por la venta de bienes iguales o similares al objeto de la convocatoria, durante los últimos ocho (8) años.",
                "metadata": {"categoria": "Bienes", "tipo_clausula": "Requisito Calificación", "fuente": "Bases Estándar Bienes - OSCE"}
            },
            {
                "documento": "Criterios de Evaluación Técnica para Bienes: Se otorgará un máximo de 20 puntos por mejoras al hardware propuesto (ej. mayor capacidad de almacenamiento o procesadores de generación reciente) y 10 puntos por ampliación del plazo de garantía técnica por encima del mínimo requerido.",
                "metadata": {"categoria": "Bienes", "tipo_clausula": "Factor Evaluación", "fuente": "Manual de Compras GAF"}
            },
            # SERVICIOS
            {
                "documento": "El plazo de prestación del servicio se computa en días calendario. Los entregables mensuales deberán presentarse dentro de los primeros dos (2) días hábiles del mes siguiente. La conformidad de los informes estará a cargo del Administrador del Contrato (GSTI o GAF).",
                "metadata": {"categoria": "Servicios", "tipo_clausula": "Plazo y Conformidad", "fuente": "Bases Estándar Servicios"}
            },
            {
                "documento": "Requisito de Calificación - Experiencia en Servicios: Se requiere experiencia en la prestación de servicios similares al objeto de la convocatoria por un monto acumulado de hasta tres veces el valor estimado, acreditado mediante contratos y conformidad de los mismos en los últimos cinco (5) años.",
                "metadata": {"categoria": "Servicios", "tipo_clausula": "Requisito Calificación", "fuente": "Directivas Internas de Osinergmin"}
            },
            {
                "documento": "Penalidades aplicables por retraso: De acuerdo al Artículo 161 del Reglamento de la Ley de Contrataciones del Estado, por cada día de retraso injustificado en la ejecución de las prestaciones, se aplicará al contratista una penalidad por mora de hasta un máximo del diez por ciento (10%) del monto del contrato.",
                "metadata": {"categoria": "Servicios", "tipo_clausula": "Penalidades", "fuente": "Ley de Contrataciones del Estado"}
            },
            # CONSULTORIAS
            {
                "documento": "Requisito de Calificación - Personal Clave: El Jefe de Proyecto deberá acreditar el título profesional de Ingeniero de Sistemas, Telecomunicaciones o afines, con certificación PMP vigente y experiencia mínima de tres (3) años en proyectos de consultoría de seguridad informática.",
                "metadata": {"categoria": "Consultoría", "tipo_clausula": "Requisito Calificación", "fuente": "Bases Estándar Consultoría"}
            },
            {
                "documento": "Criterios de Evaluación para Consultorías: Experiencia del personal clave propuesto (hasta 30 puntos), metodología de trabajo y plan de contingencia (hasta 20 puntos), y certificaciones internacionales de la empresa en ISO/IEC 27001 o ISO 9001 (hasta 10 puntos).",
                "metadata": {"categoria": "Consultoría", "tipo_clausula": "Factor Evaluación", "fuente": "Guía de Adjudicaciones Osinergmin"}
            },
            {
                "documento": "Entregables de Consultoría: La entrega de informes se estructurará en tres etapas: 1. Plan de Trabajo detallado, 2. Diagnóstico de arquitectura y riesgos informáticos, 3. Informe Final y plan de remediación ante desastres corporativos.",
                "metadata": {"categoria": "Consultoría", "tipo_clausula": "Entregables", "fuente": "TDR Tipo de la GSTI"}
            }
        ]
        
        # Desglosar para inserción automática en Qdrant
        documents = [c["documento"] for c in mock_clauses]
        metadata = [c["metadata"] for c in mock_clauses]
        ids = list(range(len(mock_clauses)))
        
        # Agregar los documentos calculando vectores en disco automáticamente
        client.add(
            collection_name=collection_name,
            documents=documents,
            metadata=metadata,
            ids=ids
        )
        print(f"Colección poblada con {len(mock_clauses)} cláusulas estándar con embeddings locales.")
    else:
        print(f"La colección '{collection_name}' ya existe y está lista.")

def query_similar_clauses(query_text, category_filter=None, limit=3):
    """Busca cláusulas similares en Qdrant utilizando filtrado opcional por categoría (payload)."""
    client = get_qdrant_client()
    collection_name = "plantillas_osinergmin"
    
    # Construir filtro por categoría si se proporciona
    query_filter = None
    if category_filter:
        # Mapear categorías si vienen de Streamlit (ej. 'Bienes - Normal' -> 'Bienes')
        category_clean = category_filter.split(" - ")[0]
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="categoria",
                    match=MatchValue(value=category_clean)
                )
            ]
        )
        
    try:
        results = client.query(
            collection_name=collection_name,
            query_text=query_text,
            query_filter=query_filter,
            limit=limit
        )
        
        output = []
        for r in results:
            output.append({
                "texto": r.document,
                "categoria": r.metadata.get("categoria"),
                "tipo_clausula": r.metadata.get("tipo_clausula"),
                "fuente": r.metadata.get("fuente"),
                "score": r.score
            })
        return output
    except Exception as e:
        print(f"Error al consultar Qdrant: {e}")
        return []

if __name__ == "__main__":
    print("Iniciando inicialización de Qdrant...")
    init_qdrant()
    print("Buscando 'penalidad' en Servicios:")
    res = query_similar_clauses("penalidad por mora", category_filter="Servicios")
    for r in res:
        print(f"[{r['fuente']}] ({r['score']:.3f}): {r['texto']}")
