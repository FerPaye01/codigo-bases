import requests
import sys
import time

def test_extract_file():
    url = "http://127.0.0.1:8000/extract_file"
    pdf_path = "LLM-NESTED LEARNING/nested-learning-kmccleary3301/google_papers/Nested_Learning.pdf"
    
    print(f"Testing /extract_file with document: {pdf_path}")
    print("This will run local IBM Docling parsing + local Ollama Gemma 3 inference. Please wait...")
    
    start_time = time.time()
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            resp = requests.post(url, files=files, timeout=600)
            
        print(f"Status Code: {resp.status_code}")
        print(f"Total processing time: {time.time() - start_time:.2f} seconds.")
        
        if resp.status_code == 200:
            res_json = resp.json()
            print("\n--- Successful Extraction! ---")
            data = res_json["data"]
            print(f"Objeto: {data['objeto']}")
            print(f"Plazo: {data['plazo']}")
            print(f"Valor Estimado: {data['valor_estimado']}")
            print(f"Requisitos de Calificación: {data['requisitos_calificacion']}")
            print(f"Factores de Evaluación: {data['factores_evaluacion']}")
            print(f"Markdown Content Length: {len(res_json.get('raw_response', ''))} characters")
        else:
            print(f"Error output: {resp.text}")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_extract_file()
