import os
import sys
import requests

# Forzar codificación UTF-8 en salida
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener URL final de redirección
url = "https://github.com/ollama/ollama/releases/download/v0.30.8/ollama-linux-amd64.tar.zst"
dest = "/data/proyectos/proyecto-bases/ollama_bin/ollama-linux-amd64.tar.zst"

os.makedirs(os.path.dirname(dest), exist_ok=True)

temp_size = 0
mode = 'wb'
headers = {}

if os.path.exists(dest):
    temp_size = os.path.getsize(dest)
    # Si ya se descargó algo, reanudar
    if temp_size > 0:
        headers['Range'] = f'bytes={temp_size}-'
        mode = 'ab'
        print(f"Reanudando descarga desde byte {temp_size}...")

try:
    # Seguir redirecciones y usar timeout largo
    r = requests.get(url, headers=headers, stream=True, timeout=30)
    
    # 206 Partial Content significa reanudación exitosa, 200 significa inicio desde cero
    if r.status_code in [200, 206]:
        content_len = int(r.headers.get('content-length', 0))
        total_size = content_len + (temp_size if r.status_code == 206 else 0)
        
        if r.status_code == 200:
            temp_size = 0
            mode = 'wb'
            
        print(f"Descargando {total_size} bytes totales ({content_len} bytes restantes)...")
        
        last_print = 0
        with open(dest, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024): # bloques de 1MB
                if chunk:
                    f.write(chunk)
                    temp_size += len(chunk)
                    # Mostrar progreso cada 5MB para no saturar los logs
                    if temp_size - last_print > 5 * 1024 * 1024 or temp_size == total_size:
                        print(f"Progreso: {temp_size / (1024*1024):.2f}MB / {total_size / (1024*1024):.2f}MB ({temp_size / total_size * 100:.2f}%)")
                        last_print = temp_size
        print("Descarga completada con éxito.")
        sys.exit(0)
    elif r.status_code == 416:
        print("El rango solicitado ya está completo o fuera de los límites del archivo. (Descarga posiblemente terminada).")
        sys.exit(0)
    else:
        print(f"Error HTTP de descarga: {r.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Error durante la descarga: {e}", file=sys.stderr)
    sys.exit(1)
