### ¿Se puede reproducir este proyecto en otra máquina (como Windows)?                                                                                                           
                                                                                                                                                                                   
  Sí, el proyecto es 100% reproducible en Windows, pero no debemos subir las carpetas de base de datos locales, modelos ni binarios al repositorio de GitHub.                      
                                                                                                                                                                                   
  A continuación te detallo qué partes son compatibles, por qué no debemos subirlas a Git y cómo reproducir el proyecto en Windows paso a paso.                                    
  ──────                                                                                                                                                                           
  ### 1. ¿Por qué NO debemos hacer  git add  de esas carpetas?                                                                                                                     
                                                                                                                                                                                   
  1. Límite de tamaño de GitHub (100 MB): La carpeta  .ollama/  contiene el modelo  gemma3:1b  (que pesa más de 1.5 GB). GitHub bloquea de forma estricta cualquier intento de     
  subir archivos mayores a 100 MB, por lo que el comando  git push  fallará de inmediato.                                                                                          
  2. Incompatibilidad de Sistemas Operativos (Binarios): La carpeta  ollama_bin/  contiene ejecutables compilados para Linux (formato ELF). No funcionarán en Windows. Windows     
  requiere su propio ejecutable nativo ( ollama.exe ).                                                                                                                             
  3. Auto-inicialización: La base de datos relacional SQLite ( bases_osinergmin.db ) y la base de datos vectorial Qdrant ( qdrant_db/ ) se crean, estructuran y siembran (seed) de 
  manera automática la primera vez que se inicia la aplicación. Subir estas carpetas locales solo generaría redundancia y posibles conflictos de bloqueo de archivos.              
  4. Portabilidad de datos: El archivo transaccional de SQLite ( .db ) y los archivos de Word ( .docx ) sí son 100% compatibles entre Linux y Windows.                             
  ──────                                                                                                                                                                           
  ### 2. Guía paso a paso para reproducir el proyecto en Windows                                                                                                                   
                                                                                                                                                                                   
  Para levantar el asistente en una máquina con Windows, sigue estos sencillos pasos:                                                                                              
                                                                                                                                                                                   
  #### Paso 1: Instalar y configurar Ollama en Windows                                                                                                                             
                                                                                                                                                                                   
  1. Descarga e instala el instalador nativo de Windows desde: https://ollama.com/download/OllamaSetup.exe.                                                                        
  2. Abre una terminal de Windows ( cmd  o  PowerShell ) y descarga el modelo:                                                                                                     
    ollama pull gemma3:1b                                                                                                                                                          
                                                                                                                                                                                   
                                                                                                                                                                                   
  #### Paso 2: Clonar el Repositorio de GitHub                                                                                                                                     
                                                                                                                                                                                   
  Clona el repositorio en la máquina de Windows:                                                                                                                                   
                                                                                                                                                                                   
    git clone https://github.com/FerPaye01/codigo-bases.git                                                                                                                        
    cd codigo-bases                                                                                                                                                                
                                                                                                                                                                                   
  #### Paso 3: Crear el entorno virtual e instalar dependencias
  
  En Windows, los comandos de entorno virtual cambian ligeramente:
  
  1. Crea el entorno virtual de Python:
    python -m venv venv
  
  2. Activa el entorno virtual:
      • En PowerShell:  .\venv\Scripts\Activate.ps1 
      • En cmd:  .\venv\Scripts\activate.bat 
  3. Instala las dependencias del proyecto:
    pip install fastapi streamlit uvicorn docling qdrant-client fastembed python-docx docxtpl requests
  (Nota: IBM Docling instalará automáticamente los modelos de OCR y PyTorch para CPU en Windows).
  
  #### Paso 4: Ejecutar los Servidores en Windows
  
  Teniendo la consola con el entorno virtual activo:
  
  1. Iniciar el API Backend (FastAPI):
    uvicorn api:app --host 127.0.0.1 --port 8000 --reload
  (SQLite y la base vectorial Qdrant local se inicializarán y sembrarán automáticamente en el primer arranque).
  2. Iniciar la Interfaz Web (Streamlit):
  En otra terminal con el entorno virtual activo, ejecuta:
    streamlit run app.py
  

  Al abrir el navegador en  http://localhost:8501 , el sistema funcionará exactamente igual que en Linux.