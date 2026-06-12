import json
import time
import sys
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import ollama

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError in Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


MODEL_NAME = 'gemma3:1b'

# ---------------------------------------------------------
# Define Pydantic Models for Structured Output Examples
# ---------------------------------------------------------
class UserProfile(BaseModel):
    name: str = Field(description="Nombre del usuario")
    occupation: str = Field(description="Ocupación o profesión")
    skills: List[str] = Field(description="Lista de habilidades técnicas mencionadas")
    years_experience: int = Field(description="Años de experiencia, o -1 si no se especifica")


class SimulatedToolCall(BaseModel):
    tool_name: str = Field(
        description="El nombre de la función a llamar: 'calculator', 'get_weather' o 'none'"
    )
    arguments: Dict[str, Any] = Field(
        description="Argumentos clave-valor para la función (ej. {'a': 5, 'b': 3} o {'city': 'Madrid'})"
    )


# ---------------------------------------------------------
# Real Python Functions to simulate Tool Calling
# ---------------------------------------------------------
def calculator(a: float, b: float, op: str) -> str:
    if op == '+': return f"{a} + {b} = {a + b}"
    elif op == '-': return f"{a} - {b} = {a - b}"
    elif op == '*': return f"{a} * {b} = {a * b}"
    elif op == '/': return f"{a} / {b} = {a / b}" if b != 0 else "Error: División por cero"
    return f"Operación '{op}' no soportada."


def get_weather(city: str) -> str:
    city_lower = city.lower()
    if "madrid" in city_lower: return "Clima en Madrid: 22°C, Soleado"
    elif "paris" in city_lower or "parís" in city_lower: return "Clima en París: 15°C, Llovizna"
    elif "buenos aires" in city_lower: return "Clima en Buenos Aires: 18°C, Despejado"
    else: return f"Clima en {city}: 20°C, Parcialmente Nublado"


def main():
    print("=" * 60)
    print(f" Gemma 3 1B + Ollama Python Library Demo ".center(60, "="))
    print("=" * 60)
    
    # 1. Stateless Text Generation
    print("\n--- 1. Generación de Texto Simple (Stateless) ---")
    prompt = "Explica qué es una API REST en una sola frase simple."
    print(f"Prompt: {prompt}")
    start = time.time()
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    print(f"Respuesta: {response['response'].strip()}")
    print(f"Tiempo: {time.time() - start:.2f}s")
    
    # 2. Streaming Responses
    print("\n--- 2. Streaming de Respuesta ---")
    prompt = "Escribe un poema de 3 líneas sobre el café."
    print(f"Prompt: {prompt}")
    print("Respuesta (Streaming): ", end="", flush=True)
    for chunk in ollama.generate(model=MODEL_NAME, prompt=prompt, stream=True):
        print(chunk['response'], end="", flush=True)
    print()
    
    # 3. Multi-turn Chat
    print("\n--- 3. Chat Multi-turno (Manteniendo el Contexto) ---")
    messages = [
        {"role": "user", "content": "Hola Gemma, recuerda que mi color favorito es el verde."}
    ]
    print(f"Turno 1 (Usuario): {messages[0]['content']}")
    resp1 = ollama.chat(model=MODEL_NAME, messages=messages)
    print(f"Turno 1 (Gemma): {resp1['message']['content'].strip()}")
    messages.append(resp1['message'])
    
    messages.append({"role": "user", "content": "¿Cuál es mi color favorito?"})
    print(f"Turno 2 (Usuario): {messages[-1]['content']}")
    resp2 = ollama.chat(model=MODEL_NAME, messages=messages)
    print(f"Turno 2 (Gemma): {resp2['message']['content'].strip()}")
    
    # 4. Structured JSON Output
    print("\n--- 4. Salida JSON Estructurada ---")
    text_to_parse = "Hola, mi nombre es Juan Pérez. Trabajo como Analista de Datos y tengo 4 años de experiencia. Sé usar SQL, Python y Tableau."
    print(f"Texto a estructurar: '{text_to_parse}'")
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            'role': 'user',
            'content': f"Extrae la información del texto y ponla en el formato del esquema JSON:\n{text_to_parse}"
        }],
        format=UserProfile.model_json_schema()
    )
    json_str = response['message']['content']
    print(f"JSON recibido:\n{json_str}")
    try:
        profile = UserProfile(**json.loads(json_str))
        print("Objeto Pydantic instanciado con éxito:")
        print(f" - Nombre: {profile.name}")
        print(f" - Ocupación: {profile.occupation}")
        print(f" - Habilidades: {', '.join(profile.skills)}")
        print(f" - Experiencia: {profile.years_experience} años")
    except Exception as e:
        print(f"Error al validar JSON: {e}")
        
    # 5. Simulated Tool Calling
    print("\n--- 5. Simulación de Tool Calling (Agente Autónomo) ---")
    queries = [
        "¿Cuánto es 45 multiplicado por 12?",
        "¿Cómo está el clima en París hoy?",
        "Dime un chiste sobre robots."
    ]
    
    system_instruction = (
        "Eres un despachador de herramientas. Tu única tarea es decidir qué herramienta llamar basándote en la solicitud del usuario.\n"
        "Herramientas disponibles:\n"
        "1. name: 'calculator', arguments: {a: float, b: float, op: str} (donde op es '+', '-', '*', o '/')\n"
        "2. name: 'get_weather', arguments: {city: str}\n"
        "Si no necesitas ninguna herramienta, responde con tool_name 'none'.\n"
        "Responde exclusivamente con el esquema JSON provisto."
    )
    
    for q in queries:
        print(f"\nConsulta: '{q}'")
        res = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': q}
            ],
            format=SimulatedToolCall.model_json_schema()
        )
        call_info = json.loads(res['message']['content'])
        tool_name = call_info.get('tool_name', 'none')
        args = call_info.get('arguments', {})
        
        print(f"Decisión del modelo: tool_name='{tool_name}', arguments={args}")
        
        if tool_name == 'calculator':
            result = calculator(args.get('a', 0), args.get('b', 0), args.get('op', '+'))
            print(f"Resultado de la función local: {result}")
        elif tool_name == 'get_weather':
            result = get_weather(args.get('city', ''))
            print(f"Resultado de la función local: {result}")
        else:
            print("El modelo respondió directamente sin herramientas.")
            
    print("\n" + "=" * 60)
    print(" Demostración Finalizada con Éxito ".center(60, "="))
    print("=" * 60)


if __name__ == '__main__':
    main()
