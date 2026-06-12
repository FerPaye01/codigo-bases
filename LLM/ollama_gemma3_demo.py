import os
import json
import time
import sys
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import ollama

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError in Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Import rich elements for premium terminal user interface
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

console = Console()
MODEL_NAME = 'gemma3:1b'

# Check if model exists
try:
    ollama.show(MODEL_NAME)
except Exception:
    console.print(Panel(
        f"[bold red]Error:[/] El modelo [bold yellow]{MODEL_NAME}[/] no está disponible en Ollama.\n"
        f"Por favor ejecuta [cyan]ollama pull {MODEL_NAME}[/] en tu terminal antes de correr este script.",
        title="Modelo No Encontrado",
        border_style="red"
    ))
    exit(1)


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
    """Suma, resta, multiplica o divide dos números."""
    if op == '+':
        return f"{a} + {b} = {a + b}"
    elif op == '-':
        return f"{a} - {b} = {a - b}"
    elif op == '*':
        return f"{a} * {b} = {a * b}"
    elif op == '/':
        if b == 0:
            return "Error: División por cero"
        return f"{a} / {b} = {a / b}"
    else:
        return f"Operación '{op}' no soportada."


def get_weather(city: str) -> str:
    """Simula el clima actual de una ciudad."""
    city_lower = city.lower()
    if "madrid" in city_lower:
        return "Clima en Madrid: 22°C, Soleado"
    elif "paris" in city_lower or "parís" in city_lower:
        return "Clima en París: 15°C, Llovizna"
    elif "buenos aires" in city_lower:
        return "Clima en Buenos Aires: 18°C, Despejado"
    elif "tokyo" in city_lower or "tokio" in city_lower:
        return "Clima en Tokio: 26°C, Nublado"
    else:
        return f"Clima en {city}: 20°C, Parcialmente Nublado"


# ---------------------------------------------------------
# DEMO FUNCTIONS
# ---------------------------------------------------------

def demo_basic_generate():
    console.print(Panel("Opción 1: Generación Básica de Texto (Stateless)", style="bold cyan"))
    prompt = Prompt.ask("Escribe una pregunta corta para Gemma 3", default="Explica la recursividad en una oración simple")
    
    console.print("\n[bold green]Código Ejecutado:[/]")
    code_text = (
        "import ollama\n"
        "response = ollama.generate(\n"
        f"    model='{MODEL_NAME}',\n"
        f"    prompt='{prompt}'\n"
        ")\n"
        "print(response['response'])"
    )
    console.print(Panel(code_text, style="dim", border_style="green"))
    
    with console.status("[bold yellow]Generando respuesta de Gemma 3..."):
        start_time = time.time()
        response = ollama.generate(model=MODEL_NAME, prompt=prompt)
        elapsed = time.time() - start_time
        
    console.print("\n[bold green]Respuesta Recibida:[/]")
    console.print(Panel(response['response'], title="Gemma 3 Output", border_style="blue"))
    
    # Show metadata
    table = Table(title="Metadatos de la Respuesta", show_header=True, header_style="bold magenta")
    table.add_column("Propiedad", style="cyan")
    table.add_column("Valor", style="green")
    table.add_row("Tiempo de respuesta", f"{elapsed:.2f} segundos")
    table.add_row("Tokens leídos (Prompt)", str(response.get('prompt_eval_count', 'N/A')))
    table.add_row("Tokens generados", str(response.get('eval_count', 'N/A')))
    console.print(table)


def demo_streaming():
    console.print(Panel("Opción 2: Streaming de Respuestas en Tiempo Real", style="bold cyan"))
    prompt = Prompt.ask("Escribe algo para que Gemma 3 redacte (ej. un poema corto)", default="Escribe un poema de 4 líneas sobre la Luna")
    
    console.print("\n[bold green]Código Ejecutado:[/]")
    code_text = (
        "import ollama\n"
        "for chunk in ollama.generate(\n"
        f"    model='{MODEL_NAME}',\n"
        f"    prompt='{prompt}',\n"
        "    stream=True\n"
        "):\n"
        "    print(chunk['response'], end='', flush=True)"
    )
    console.print(Panel(code_text, style="dim", border_style="green"))
    
    console.print("\n[bold green]Streaming de Respuesta:[/]")
    console.print("[blue]Gemma 3: [/]", end="")
    
    # Custom loop to display streaming output
    for chunk in ollama.generate(model=MODEL_NAME, prompt=prompt, stream=True):
        console.print(chunk['response'], end='', flush=True)
    console.print("\n")


def demo_multiturn_chat():
    console.print(Panel("Opción 3: Chat Multi-turno (Manteniendo el Contexto)", style="bold cyan"))
    console.print("En este modo, las respuestas previas se almacenan y reenvían para mantener el contexto.\n")
    
    messages = [
        {"role": "system", "content": "Eres un asistente virtual amigable y experto en programación."}
    ]
    
    console.print("[dim italic]Escribe 'salir' para terminar el chat.[/]\n")
    
    while True:
        user_input = Prompt.ask("[bold green]Tú[/]")
        if user_input.lower() == 'salir':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        console.print("[bold blue]Gemma 3: [/]", end="")
        
        response_content = ""
        # We can stream inside the chat context too
        for chunk in ollama.chat(model=MODEL_NAME, messages=messages, stream=True):
            content = chunk['message']['content']
            console.print(content, end='', flush=True)
            response_content += content
        console.print()
        
        messages.append({"role": "assistant", "content": response_content})
        console.print()


def demo_structured_output():
    console.print(Panel("Opción 4: Respuestas Estructuradas en JSON (Pydantic)", style="bold cyan"))
    text_to_parse = Prompt.ask(
        "Ingresa un texto para extraer información estructurada",
        default="Hola, soy Sofía. Trabajo como ingeniera de software y tengo 7 años de experiencia desarrollando en Python y React."
    )
    
    console.print("\n[bold green]Código Ejecutado:[/]")
    code_text = (
        "from pydantic import BaseModel, Field\n"
        "import ollama\n\n"
        "class UserProfile(BaseModel):\n"
        "    name: str\n"
        "    occupation: str\n"
        "    skills: list[str]\n"
        "    years_experience: int\n\n"
        "response = ollama.chat(\n"
        f"    model='{MODEL_NAME}',\n"
        "    messages=[{'role': 'user', 'content': 'Extrae la información de: ...'}],\n"
        "    format=UserProfile.model_json_schema()\n"
        ")\n"
        "print(response['message']['content'])"
    )
    console.print(Panel(code_text, style="dim", border_style="green"))
    
    with console.status("[bold yellow]Analizando texto y estructurando JSON con Gemma 3..."):
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{
                'role': 'user', 
                'content': f"Analiza el siguiente texto y extrae la información requerida en el esquema JSON:\n\n{text_to_parse}"
            }],
            format=UserProfile.model_json_schema()
        )
        json_content = response['message']['content']
        
    console.print("\n[bold green]JSON Crudo de Gemma 3:[/]")
    console.print(Panel(json_content, border_style="blue"))
    
    try:
        data = json.loads(json_content)
        profile = UserProfile(**data)
        
        # Display as a pretty table
        table = Table(title="Información Extraída (Objeto Pydantic)", show_header=True, header_style="bold magenta")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="green")
        table.add_row("Nombre", profile.name)
        table.add_row("Ocupación", profile.occupation)
        table.add_row("Habilidades", ", ".join(profile.skills))
        table.add_row("Años de Experiencia", str(profile.years_experience) if profile.years_experience != -1 else "No especificado")
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error al parsear el JSON estructurado: {e}[/]")


def demo_simulated_tool_calling():
    console.print(Panel("Opción 5: Simulación de Tool Calling via JSON estructurado", style="bold cyan"))
    console.print(
        "Como la integración nativa de `gemma3:1b` en Ollama no soporta el parámetro `tools` en la API actual,\n"
        "podemos lograr exactamente el mismo comportamiento pidiéndole al modelo que responda con un JSON\n"
        "que represente la llamada a una función cuando corresponda, o 'none' si no necesita herramientas.\n"
    )
    
    prompt = Prompt.ask(
        "Haz una consulta que requiera una herramienta (clima o matemática)", 
        default="¿Cuál es el clima en París hoy?"
    )
    
    console.print(f"\n[bold green]Consulta del Usuario:[/] {prompt}")
    
    system_instruction = (
        "Eres un asistente que decide qué herramienta llamar basándote en la solicitud del usuario.\n"
        "Las herramientas disponibles son:\n"
        "1. name: 'calculator', arguments: {a: float, b: float, op: str} (donde op es '+', '-', '*', o '/')\n"
        "2. name: 'get_weather', arguments: {city: str}\n"
        "Si no se necesita ninguna herramienta, establece tool_name a 'none'.\n"
        "Responde EXCLUSIVAMENTE con el esquema JSON provisto."
    )
    
    with console.status("[bold yellow]Gemma 3 decidiendo qué herramienta usar..."):
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': prompt}
            ],
            format=SimulatedToolCall.model_json_schema()
        )
        json_content = response['message']['content']
        
    console.print("\n[bold green]Decisión de Gemma 3 (JSON):[/]")
    console.print(Panel(json_content, border_style="blue"))
    
    try:
        call_info = json.loads(json_content)
        tool_name = call_info.get('tool_name', 'none')
        args = call_info.get('arguments', {})
        
        if tool_name == 'calculator':
            a = float(args.get('a', 0))
            b = float(args.get('b', 0))
            op = args.get('op', '+')
            console.print(f"[bold yellow]Ejecutando Función Local:[/] [cyan]calculator(a={a}, b={b}, op='{op}')[/]")
            result = calculator(a, b, op)
            console.print(Panel(result, title="Resultado del Cálculo", border_style="green"))
            
        elif tool_name == 'get_weather':
            city = args.get('city', 'Madrid')
            console.print(f"[bold yellow]Ejecutando Función Local:[/] [cyan]get_weather(city='{city}')[/]")
            result = get_weather(city)
            console.print(Panel(result, title="Resultado del Clima", border_style="green"))
            
        else:
            console.print("[bold green]Gemma 3 decidió que no se requiere ninguna herramienta local.[/]")
            
    except Exception as e:
        console.print(f"[bold red]Error al procesar la herramienta: {e}[/]")


# ---------------------------------------------------------
# MAIN EVENT LOOP
# ---------------------------------------------------------
def main():
    while True:
        console.clear()
        console.print(Panel(
            Text.assemble(
                ("Gemma 3 1B", "bold yellow"),
                (" + ", "white"),
                ("Ollama Python SDK Demo", "bold green")
            ),
            subtitle="Interactúa de forma local y segura con LLMs",
            border_style="magenta"
        ))
        
        console.print("[bold]Selecciona una demostración para ejecutar:[/]")
        console.print("1. [bold cyan]Generación Básica (Stateless)[/] - ollama.generate()")
        console.print("2. [bold cyan]Streaming en Tiempo Real[/] - Stream=True")
        console.print("3. [bold cyan]Chat Multi-turno[/] - ollama.chat() con historial")
        console.print("4. [bold cyan]Respuestas Estructuradas (JSON)[/] - format=Pydantic.json_schema()")
        console.print("5. [bold cyan]Simulación de Tool Calling[/] - Agente funcional autónomo")
        console.print("6. [bold red]Salir[/]")
        
        choice = IntPrompt.ask("\nOpción (1-6)", choices=[1, 2, 3, 4, 5, 6], default=1)
        
        console.clear()
        if choice == 1:
            demo_basic_generate()
        elif choice == 2:
            demo_streaming()
        elif choice == 3:
            demo_multiturn_chat()
        elif choice == 4:
            demo_structured_output()
        elif choice == 5:
            demo_simulated_tool_calling()
        elif choice == 6:
            console.print("[bold green]¡Hasta luego![/]")
            break
            
        Prompt.ask("\nPresiona [bold enter]Enter[/] para regresar al menú principal")


if __name__ == '__main__':
    main()
