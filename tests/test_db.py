import sys
sys.path.append("/data/proyectos/proyecto-bases")
import database
import json

def run_test():
    print("--- 1. Initializing DB ---")
    database.init_db()
    
    print("\n--- 2. Checking initial history length ---")
    history = database.get_all_processes_history()
    print(f"Total processes in history: {len(history)}")
    for h in history:
        print(f"Expediente: {h['expediente']}, Plantilla: {h['plantilla']}, Estado: {h['estado']}")

    print("\n--- 3. Saving a new process (20260000982) in progress ---")
    datos_tecnicos = {
        "objeto": "Servicio de Consultoría de Ciberseguridad Modificado",
        "plazo": "180 días calendario",
        "sistema_contratacion": "Suma Alzada",
        "requerimiento_completo": "Entregables técnicos de ciberseguridad.",
        "requisitos_calificacion": "- ISO 27001",
        "factores_evaluacion": "Penalidad de 0.20%"
    }
    datos_admin = {
        "nomenclatura": "AS-002-2026-OSINERGMIN",
        "tipo_procedimiento": "Adjudicación Simplificada",
        "numero_proceso": "AS-002-2026-OSINERGMIN",
        "valor_estimado": 190000.0,
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
    }
    
    success = database.save_or_update_process(
        numero_expediente="20260000982",
        asunto="Servicio de Consultoría para la Gestión y Mitigación de Riesgos Informáticos en Osinergmin",
        tdr_nombre="TDR_Consultoria_Ciberseguridad_2026.pdf",
        plantilla="Servicios - Normal",
        datos_tecnicos=datos_tecnicos,
        datos_admin=datos_admin,
        estado="En progreso",
        responsable="jortiz@osinergmin.gob.pe"
    )
    print(f"Save success: {success}")

    print("\n--- 4. Loading the saved process (20260000982) ---")
    state = database.load_process_state("20260000982")
    if state:
        print(f"Loaded Expediente: {state['expediente']}")
        print(f"Loaded Estado: {state['estado']}")
        print(f"Loaded Objeto (datos_tecnicos): {state['datos_extraidos']['objeto']}")
        print(f"Loaded Valor Estimado (datos_admin): {state['datos_administrativos']['valor_estimado']}")
    else:
        print("Failed to load process state!")

    print("\n--- 5. Checking history again ---")
    history2 = database.get_all_processes_history()
    print(f"Total processes in history: {len(history2)}")
    for h in history2:
        if h['expediente'] == "20260000982":
            print(f"Expediente: {h['expediente']}, Plantilla: {h['plantilla']}, Estado: {h['estado']} (VERIFIED!)")

if __name__ == "__main__":
    run_test()
