from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Protocolo-Estandar-Server")


@mcp.tool()
def calculator(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get weather for a city."""
    # This would normally call a weather API
    return f"Weather in {city}: 22degrees{unit[0].upper()}"


if __name__ == "__main__":
    import sys
    # Reconfigure stdout to use UTF-8 to prevent any encoding issues on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("Iniciando MCP Server en modo SSE (Server-Sent Events)...")
    mcp.run(transport="sse")
