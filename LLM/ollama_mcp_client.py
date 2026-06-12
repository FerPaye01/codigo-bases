import asyncio
import json
import sys
from pydantic import BaseModel, Field
import ollama
from mcp import ClientSession
from mcp.client.sse import sse_client

# Configure stdout to use UTF-8 to prevent any encoding issues on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MODEL_NAME = 'gemma3:1b'
SERVER_URL = "http://127.0.0.1:8000/sse"


# Pydantic model to ask Gemma 3 which tool to execute
class ToolCallDecision(BaseModel):
    tool_name: str = Field(
        description="El nombre exacto de la herramienta a llamar de la lista de herramientas, o 'none' si no se necesita ninguna herramienta."
    )
    arguments: dict = Field(
        default_factory=dict,
        description="Los argumentos clave-valor para la herramienta (por ejemplo: {'a': 5, 'b': 10} para 'sum', o {'city': 'Madrid'} para 'get_weather')"
    )


async def run_client():
    print("=" * 60)
    print(" Iniciando Cliente MCP SSE + Ollama Gemma 3 ".center(60, "="))
    print("=" * 60)
    
    print(f"\n1. Conectando al Servidor MCP SSE en {SERVER_URL}...")
    try:
        async with sse_client(SERVER_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize connection with MCP server
                print("2. Inicializando sesión de protocolo...")
                await session.initialize()
                print("   ¡Conexión establecida con éxito!")
                
                # Fetch available tools
                print("\n3. Obteniendo herramientas disponibles del servidor MCP...")
                tools_response = await session.list_tools()
                available_tools = tools_response.tools
                
                print(f"   Herramientas encontradas ({len(available_tools)}):")
                tools_info = []
                for tool in available_tools:
                    print(f"    - [Tool] {tool.name}: {tool.description}")
                    tools_info.append({
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    })
                
                # Ask user for prompt
                print("\n" + "-" * 50)
                user_prompt = input("¿Qué le deseas pedir a Gemma? (ej. ¿cuánto es 142 + 258? o clima en París): ")
                if not user_prompt.strip():
                    user_prompt = "¿Cuánto es 123 + 456?"
                    print(f"Usando prompt por defecto: '{user_prompt}'")
                print("-" * 50)
                
                # System prompt to guide Gemma 3 to select the correct tool
                system_instruction = (
                    "Eres un agente inteligente que coordina llamadas a herramientas del protocolo MCP.\n"
                    f"Las herramientas disponibles registradas en el servidor son:\n"
                    f"{json.dumps(tools_info, indent=2, ensure_ascii=False)}\n\n"
                    "Debes decidir si la solicitud del usuario requiere de alguna herramienta disponible.\n"
                    "Si requiere una herramienta, responde con el nombre exacto de la herramienta y sus argumentos.\n"
                    "Si no requiere ninguna herramienta, responde con tool_name = 'none'.\n"
                    "Responde exclusivamente en el formato del esquema JSON provisto."
                )
                
                print("\n4. Consultando a Gemma 3 1B para decidir la herramienta...")
                decision_response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    format=ToolCallDecision.model_json_schema()
                )
                
                decision_json = decision_response['message']['content']
                decision = ToolCallDecision(**json.loads(decision_json))
                
                print(f"   Decisión de Gemma 3: tool_name='{decision.tool_name}', arguments={decision.arguments}")
                
                # If a tool needs to be called
                if decision.tool_name != 'none' and any(t.name == decision.tool_name for t in available_tools):
                    print(f"\n5. Ejecutando la herramienta '{decision.tool_name}' en el Servidor MCP via SSE...")
                    
                    try:
                        tool_result = await session.call_tool(decision.tool_name, decision.arguments)
                        print(f"   Resultado crudo del Servidor MCP: {tool_result.content}")
                        
                        # Extract text content from the tool output
                        result_text = ""
                        for content_item in tool_result.content:
                            if content_item.type == 'text':
                                result_text += content_item.text
                                
                        print(f"   Resultado procesado: '{result_text}'")
                        
                        # Send result back to Gemma for final natural language formulation
                        print("\n6. Enviando el resultado a Gemma 3 para formular la respuesta final...")
                        final_response = ollama.chat(
                            model=MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "Eres un asistente amable. Responde la duda del usuario usando la información de la herramienta ejecutada."},
                                {"role": "user", "content": user_prompt},
                                {"role": "assistant", "content": f"Ejecuté la herramienta {decision.tool_name} y obtuve el siguiente resultado: {result_text}. Por lo tanto:"}
                            ]
                        )
                        print("\n" + "=" * 60)
                        print("Respuesta Final de Gemma 3:")
                        print(final_response['message']['content'].strip())
                        print("=" * 60)
                        
                    except Exception as e:
                        print(f"Error al llamar a la herramienta en el servidor MCP: {e}")
                else:
                    # No tool called, let Gemma respond directly
                    print("\n5. No se requiere herramienta. Gemma responderá directamente...")
                    direct_response = ollama.chat(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    print("\n" + "=" * 60)
                    print("Respuesta Final de Gemma 3:")
                    print(direct_response['message']['content'].strip())
                    print("=" * 60)
                    
    except ConnectionRefusedError:
        print("\n[bold red]Error: No se pudo conectar al servidor MCP.[/] Asegúrate de que el servidor esté corriendo en otra consola con:")
        print("   python MCP/server.py")
    except Exception as e:
        print(f"\nError en la ejecución del cliente: {e}")


if __name__ == "__main__":
    asyncio.run(run_client())
