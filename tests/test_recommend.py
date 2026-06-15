import requests
import sys

def test_recommend():
    url = "http://127.0.0.1:8000/recommend_clauses"
    payload = {
        "text": "experiencia del postor o facturación anual",
        "categoria": "Bienes - Normal",
        "limit": 3
    }
    
    print("Testing /recommend_clauses endpoint...")
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            res_json = resp.json()
            print("\n--- Recommendations received ---")
            for idx, r in enumerate(res_json.get("recommendations", [])):
                print(f"Sugerencia #{idx+1}:")
                print(f"  Texto: {r['texto']}")
                print(f"  Fuente: {r['fuente']}")
                print(f"  Score: {r['score']:.3f}")
                print(f"  Categoría: {r['categoria']}")
        else:
            print(f"Error response: {resp.text}")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_recommend()
