import sqlite3
import json
import uuid
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

# Configuración SQLite
DATABASE_FILE = os.getenv("SQLITE_DB_FILE", "bases_osinergmin.db")

# Configuración Oracle
ORACLE_USER = os.getenv("ORACLE_DB_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
ORACLE_HOST = os.getenv("ORACLE_DB_HOST")
ORACLE_PORT = os.getenv("ORACLE_DB_PORT", "1521")
ORACLE_SERVICE = os.getenv("ORACLE_DB_SERVICE")
ORACLE_DSN = os.getenv("ORACLE_DB_DSN")

def adapt_query(query):
    """Adapta los placeholders y funciones de SQL para compatibilidad con Oracle."""
    if DB_TYPE == "oracle":
        # 1. Reemplazar '?' por ':1', ':2', etc.
        parts = query.split('?')
        new_query = ""
        for i, part in enumerate(parts[:-1]):
            new_query += part + f":{i+1}"
        new_query += parts[-1]
        query = new_query
        
        # 2. Reemplazar 'LIMIT <N>' por 'FETCH FIRST <N> ROWS ONLY'
        query = re.sub(r'(?i)\bLIMIT\s+(\d+)\b', r'FETCH FIRST \1 ROWS ONLY', query)
    return query

def get_now_value():
    """Retorna la fecha/hora actual en el formato adecuado para el motor de DB."""
    if DB_TYPE == "oracle":
        return datetime.now()
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class OracleCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, query, params=None):
        adapted = adapt_query(query)
        if params is not None:
            res = self.cursor.execute(adapted, params)
        else:
            res = self.cursor.execute(adapted)
            
        # Re-configurar rowfactory después de cada execute() ya que oracledb lo limpia
        if self.cursor.description is not None:
            self.cursor.rowfactory = lambda *row: dict(zip([col[0].lower() for col in self.cursor.description], row))
            
        return res
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def close(self):
        self.cursor.close()
        
    def __getattr__(self, name):
        return getattr(self.cursor, name)

class ConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        
    def cursor(self):
        cursor = self.conn.cursor()
        if DB_TYPE == "oracle":
            return OracleCursorWrapper(cursor)
        return cursor
        
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()
        
    def close(self):
        self.conn.close()
        
    def __getattr__(self, name):
        return getattr(self.conn, name)

def get_connection():
    """Retorna una conexión a la base de datos configurada (SQLite u Oracle)."""
    if DB_TYPE == "oracle":
        import oracledb
        oracledb.defaults.fetch_lobs = False
        if ORACLE_DSN:
            conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
        else:
            dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
            conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
        return ConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return ConnectionWrapper(conn)

def init_db():
    """Inicializa la base de datos creando las tablas del stack de Osinergmin si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if DB_TYPE == "oracle":
        import oracledb
        
        # Tabla de expedientes
        try:
            cursor.execute("""
            CREATE TABLE expedientes (
                id VARCHAR2(36) PRIMARY KEY,
                numero_expediente VARCHAR2(50) UNIQUE NOT NULL,
                datos_siged CLOB, -- JSON con metadatos de SIGED
                fecha_consulta TIMESTAMP,
                usuario_id VARCHAR2(36)
            )
            """)
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code != 955: # ORA-00955: name is already used by an existing object
                raise
                
        # Tabla de procesos
        try:
            cursor.execute("""
            CREATE TABLE procesos (
                id VARCHAR2(36) PRIMARY KEY,
                expediente_id VARCHAR2(36) REFERENCES expedientes(id),
                tipo_proceso VARCHAR2(30),
                estado VARCHAR2(20),
                datos_extraidos CLOB, -- JSON con datos técnicos del TDR (objeto, plazo, etc)
                datos_administrativos CLOB, -- JSON con nomenclatura, cronograma, valor estimado, etc
                plantilla_usada VARCHAR2(100),
                documento_generado_url VARCHAR2(1000),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code != 955:
                raise
                
        # Tabla de auditoría para trazabilidad de usuario (RNF-1)
        try:
            cursor.execute("""
            CREATE TABLE auditoria (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                usuario_id VARCHAR2(100),
                accion VARCHAR2(100),
                numero_expediente VARCHAR2(50),
                detalles CLOB,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code != 955:
                raise
    else:
        # Tabla de expedientes (conforme a stack.md)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expedientes (
            id VARCHAR(36) PRIMARY KEY,
            numero_expediente VARCHAR(50) UNIQUE NOT NULL,
            datos_siged TEXT, -- JSON con metadatos de SIGED
            fecha_consulta TIMESTAMP,
            usuario_id VARCHAR(36)
        )
        """)
        
        # Tabla de procesos (conforme a stack.md)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS procesos (
            id VARCHAR(36) PRIMARY KEY,
            expediente_id VARCHAR(36) REFERENCES expedientes(id),
            tipo_proceso VARCHAR(30),
            estado VARCHAR(20),
            datos_extraidos TEXT, -- JSON con datos técnicos del TDR (objeto, plazo, etc)
            datos_administrativos TEXT, -- JSON con nomenclatura, cronograma, valor estimado, etc
            plantilla_usada VARCHAR(100),
            documento_generado_url TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de auditoría para trazabilidad de usuario (RNF-1)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id VARCHAR(100),
            accion VARCHAR(100),
            numero_expediente VARCHAR(50),
            detalles TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
    conn.commit()
    
    # Pre-poblar con datos mock de Osinergmin si está vacío (RNF-4)
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM expedientes")
        count = cursor.fetchone()["cnt"]
        if count == 0:
            mock_data = [
                (
                    "20260000982",
                    "Servicio de Consultoría para la Gestión y Mitigación de Riesgos Informáticos en Osinergmin",
                    "TDR_Consultoria_Ciberseguridad_2026.pdf",
                    "Servicios - Normal",
                    {
                        "objeto": "Servicio de consultoría especializada para el diagnóstico, gestión y mitigación de riesgos de seguridad de la información e infraestructura de red de Osinergmin.",
                        "plazo": "180 días calendario",
                        "sistema_contratacion": "Suma Alzada",
                        "requerimiento_completo": "- Entregable 1: Diagnóstico situacional de seguridad de red.\n- Entregable 2: Arquitectura de seguridad lógica y física sugerida.\n- Entregable 3: Matriz de riesgos informáticos de Osinergmin.\n- Entregable 4: Plan de contingencias y recuperación ante desastres corporativo.",
                        "requisitos_calificacion": "- Facturación acumulada de la empresa consultora equivalente a 2 veces el valor estimado en consultorías similares durante los últimos 5 años.\n- Certificación ISO 27001 e ISO 9001 vigente.\n- Jefe de Proyecto: Ingeniero con certificación PMP y CISM (Certified Information Security Manager).",
                        "factores_evaluacion": "Por retraso en la entrega de informes del servicio se aplicará una penalidad de 0.20%."
                    },
                    {
                        "nomenclatura": "AS-002-2026-OSINERGMIN",
                        "tipo_procedimiento": "Adjudicación Simplificada",
                        "numero_proceso": "AS-002-2026-OSINERGMIN",
                        "valor_estimado": 180000.0,
                        "moneda": "Soles (S/.)",
                        "fuente_val": "Estudio de Mercado",
                        "unidad_solicitante": "GSTI",
                        "responsable": "Julio Ortiz",
                        "fecha_convocatoria": "2026-06-10",
                        "fecha_consultas": "2026-06-14",
                        "fecha_absolucion": "2026-06-16",
                        "fecha_presentacion": "2026-06-22",
                        "fecha_evaluacion": "2026-06-25",
                        "fecha_buenapro": "2026-06-28",
                        "fuente_financiamiento": "Recursos Directamente Recaudados (RDR)",
                        "observaciones_finan": ""
                    },
                    "Borrador generado",
                    "jortiz@osinergmin.gob.pe"
                ),
                (
                    "20260000411",
                    "Adquisición de Servidores de Alta Disponibilidad para el Data Center de Osinergmin",
                    "TDR_Adquisicion_Servidores_2026.pdf",
                    "Bienes - Normal",
                    {
                        "objeto": "Adquisición de 4 servidores físicos de alta disponibilidad incluyendo licenciamiento y soporte por 3 años para el Data Center de Osinergmin.",
                        "plazo": "60 días calendario",
                        "sistema_contratacion": "Suma Alzada",
                        "requerimiento_completo": "Servidores físicos de 64 núcleos, 512GB RAM y almacenamiento SSD enterprise en configuración cluster.",
                        "requisitos_calificacion": "- Experiencia de la empresa en la provisión de servidores y almacenamiento empresarial durante los últimos 3 años.\n- Soporte técnico local certificado directamente por el fabricante del hardware de los servidores.",
                        "factores_evaluacion": "Soporte técnico local certificado directamente por el fabricante."
                    },
                    {
                        "nomenclatura": "LP-001-2026-OSINERGMIN",
                        "tipo_procedimiento": "Licitación Pública",
                        "numero_proceso": "LP-001-2026-OSINERGMIN",
                        "valor_estimado": 450000.0,
                        "moneda": "Soles (S/.)",
                        "fuente_val": "Cotización de Proveedores",
                        "unidad_solicitante": "GSTI",
                        "responsable": "Luis Rodríguez",
                        "fecha_convocatoria": "2026-06-05",
                        "fecha_consultas": "2026-06-09",
                        "fecha_absolucion": "2026-06-11",
                        "fecha_presentacion": "2026-06-17",
                        "fecha_evaluacion": "2026-06-20",
                        "fecha_buenapro": "2026-06-23",
                        "fuente_financiamiento": "Recursos Ordinarios (RO)",
                        "observaciones_finan": ""
                    },
                    "Descargado",
                    "lrodriguez@osinergmin.gob.pe"
                ),
                (
                    "20260001053",
                    "Servicio de Consultoría de Procesos GAF",
                    "TDR_Procesos_GAF_2026.pdf",
                    "Consultoría - Abreviado",
                    {
                        "objeto": "Servicio de consultoría para el rediseño de procesos administrativos de la GAF.",
                        "plazo": "90 días calendario",
                        "sistema_contratacion": "Suma Alzada",
                        "requerimiento_completo": "Entregable 1: Mapeo AS-IS de procesos.\nEntregable 2: Diseño TO-BE de procesos administrativos.",
                        "requisitos_calificacion": "- Experiencia en consultoría de procesos en sector público.\n- Consultor Senior: Administrador o Ingeniero Industrial.",
                        "factores_evaluacion": "Evaluación curricular del equipo técnico propuesto."
                    },
                    {
                        "nomenclatura": "AS-005-2026-OSINERGMIN",
                        "tipo_procedimiento": "Adjudicación Simplificada",
                        "numero_proceso": "AS-005-2026-OSINERGMIN",
                        "valor_estimado": 90000.0,
                        "moneda": "Soles (S/.)",
                        "fuente_val": "Estudio de Mercado",
                        "unidad_solicitante": "GAF",
                        "responsable": "Julio Ortiz",
                        "fecha_convocatoria": "2026-06-12",
                        "fecha_consultas": "2026-06-16",
                        "fecha_absolucion": "2026-06-18",
                        "fecha_presentacion": "2026-06-24",
                        "fecha_evaluacion": "2026-06-26",
                        "fecha_buenapro": "2026-06-29",
                        "fuente_financiamiento": "Recursos Directamente Recaudados (RDR)",
                        "observaciones_finan": ""
                    },
                    "En progreso",
                    "jortiz@osinergmin.gob.pe"
                )
            ]
            
            for num_exp, asunto, tdr_nom, plant, t_data, a_data, est, resp in mock_data:
                exp_id = str(uuid.uuid4())
                datos_siged = json.dumps({"asunto": asunto, "tdr": tdr_nom, "responsable": resp})
                cursor.execute(
                    "INSERT INTO expedientes (id, numero_expediente, datos_siged, fecha_consulta, usuario_id) VALUES (?, ?, ?, ?, ?)",
                    (exp_id, num_exp, datos_siged, get_now_value(), resp)
                )
                
                proc_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO procesos (id, expediente_id, tipo_proceso, estado, datos_extraidos, datos_administrativos, plantilla_usada, creado_en, actualizado_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        proc_id,
                        exp_id,
                        a_data.get("tipo_procedimiento"),
                        est,
                        json.dumps(t_data),
                        json.dumps(a_data),
                        plant,
                        get_now_value(),
                        get_now_value()
                    )
                )
            conn.commit()
    except Exception as e:
        print(f"Error seeding DB: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_or_update_process(numero_expediente, asunto, tdr_nombre, plantilla, datos_tecnicos, datos_admin, estado, responsable):
    """Guarda o actualiza un expediente y su proceso correspondiente en la base de datos persistente."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar si el expediente ya existe en la DB
        cursor.execute("SELECT id FROM expedientes WHERE numero_expediente = ?", (numero_expediente,))
        exp_row = cursor.fetchone()
        
        if exp_row:
            expediente_id = exp_row['id']
            # Actualizar datos del expediente
            datos_siged = json.dumps({
                "asunto": asunto,
                "tdr": tdr_nombre,
                "responsable": responsable
            })
            cursor.execute("""
                UPDATE expedientes 
                SET datos_siged = ?, fecha_consulta = ? 
                WHERE id = ?
            """, (datos_siged, get_now_value(), expediente_id))
        else:
            expediente_id = str(uuid.uuid4())
            datos_siged = json.dumps({
                "asunto": asunto,
                "tdr": tdr_nombre,
                "responsable": responsable
            })
            cursor.execute("""
                INSERT INTO expedientes (id, numero_expediente, datos_siged, fecha_consulta, usuario_id)
                VALUES (?, ?, ?, ?, ?)
            """, (expediente_id, numero_expediente, datos_siged, get_now_value(), responsable))
            
        # 2. Verificar si ya existe un proceso asociado a este expediente
        cursor.execute("SELECT id FROM procesos WHERE expediente_id = ?", (expediente_id,))
        proc_row = cursor.fetchone()
        
        datos_extraidos_json = json.dumps(datos_tecnicos)
        datos_admin_json = json.dumps(datos_admin)
        
        if proc_row:
            proceso_id = proc_row['id']
            cursor.execute("""
                UPDATE procesos 
                SET tipo_proceso = ?, estado = ?, datos_extraidos = ?, datos_administrativos = ?, plantilla_usada = ?, actualizado_en = ?
                WHERE id = ?
            """, (
                datos_admin.get("tipo_procedimiento"), 
                estado, 
                datos_extraidos_json, 
                datos_admin_json, 
                plantilla, 
                get_now_value(),
                proceso_id
            ))
        else:
            proceso_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO procesos (id, expediente_id, tipo_proceso, estado, datos_extraidos, datos_administrativos, plantilla_usada, creado_en, actualizado_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proceso_id,
                expediente_id,
                datos_admin.get("tipo_procedimiento"),
                estado,
                datos_extraidos_json,
                datos_admin_json,
                plantilla,
                get_now_value(),
                get_now_value()
            ))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar en DB: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def load_process_state(numero_expediente):
    """Carga el estado persistente de un proceso a partir de su número de expediente."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.numero_expediente, e.datos_siged, p.tipo_proceso, p.estado, p.datos_extraidos, p.datos_administrativos, p.plantilla_usada
        FROM expedientes e
        JOIN procesos p ON e.id = p.expediente_id
        WHERE e.numero_expediente = ?
    """, (numero_expediente,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "expediente": row["numero_expediente"],
            "datos_siged": json.loads(row["datos_siged"]),
            "tipo_proceso": row["tipo_proceso"],
            "estado": row["estado"],
            "datos_extraidos": json.loads(row["datos_extraidos"]),
            "datos_administrativos": json.loads(row["datos_administrativos"]),
            "plantilla_usada": row["plantilla_usada"]
        }
    return None

def get_all_processes_history():
    """Retorna el historial completo de procesos registrados en la base de datos relacional (para el historial)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.numero_expediente as expediente, e.datos_siged, p.plantilla_usada as plantilla, 
               p.creado_en, p.actualizado_en, p.estado, p.datos_administrativos
        FROM expedientes e
        JOIN procesos p ON e.id = p.expediente_id
        ORDER BY p.actualizado_en DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        datos_siged = json.loads(r["datos_siged"])
        datos_admin = json.loads(r["datos_administrativos"]) if r["datos_administrativos"] else {}
        
        # Formatear fechas para la UI
        # SQLite timestamps suelen ser YYYY-MM-DD HH:MM:SS, Oracle son objetos datetime
        try:
            if isinstance(r["creado_en"], datetime):
                creacion_str = r["creado_en"].strftime('%d/%m/%Y')
            else:
                creacion_dt = datetime.strptime(r["creado_en"], '%Y-%m-%d %H:%M:%S')
                creacion_str = creacion_dt.strftime('%d/%m/%Y')
        except:
            creacion_str = str(r["creado_en"]) if r["creado_en"] else ""
            
        try:
            if isinstance(r["actualizado_en"], datetime):
                modif_str = r["actualizado_en"].strftime('%d/%m/%Y')
            else:
                modif_dt = datetime.strptime(r["actualizado_en"], '%Y-%m-%d %H:%M:%S')
                modif_str = modif_dt.strftime('%d/%m/%Y')
        except:
            modif_str = str(r["actualizado_en"]) if r["actualizado_en"] else ""
            
        history.append({
            "expediente": r["expediente"],
            "plantilla": r["plantilla"],
            "creacion": creacion_str,
            "modificacion": modif_str,
            "responsable": datos_siged.get("responsable", "admin@osinergmin.gob.pe"),
            "estado": r["estado"],
            "datos_admin": datos_admin
        })
    return history

def log_audit_action(usuario_id, accion, numero_expediente, detalles):
    """Registra una acción del usuario en la tabla de auditoría para trazabilidad (RNF-1)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO auditoria (usuario_id, accion, numero_expediente, detalles)
            VALUES (?, ?, ?, ?)
        """, (usuario_id, accion, numero_expediente, detalles))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
