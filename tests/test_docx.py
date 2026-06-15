import requests
import sys

def test_docx():
    url = "http://127.0.0.1:8000/generate_docx"
    payload = {
        "nomenclatura": "AS-002-2026-OSINERGMIN",
        "numero_expediente": "20260000982",
        "objeto": "Servicio de consultoría especializada en seguridad de la información.",
        "plazo": "180 días calendario",
        "valor_estimado": 180000.0,
        "moneda": "Soles (S/.)",
        "unidad_solicitante": "GSTI",
        "responsable": "Julio Ortiz",
        "fecha_convocatoria": "10/06/2026",
        "fecha_consultas": "14/06/2026",
        "fecha_absolucion": "16/06/2026",
        "fecha_presentacion": "22/06/2026",
        "fecha_buenapro": "28/06/2026",
        "fuente_financiamiento": "Recursos Directamente Recaudados (RDR)",
        "requisitos_calificacion": "Certificación ISO 27001 e ISO 9001 vigente.",
        "factores_evaluacion": "Penalidad de 0.20% por retraso."
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response Content Size: {len(resp.content)} bytes")
            with open("/data/proyectos/proyecto-bases/test_output.docx", "wb") as f:
                f.write(resp.content)
            print("Successfully wrote test_output.docx")
        else:
            print(f"Error output: {resp.text}")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_docx()
