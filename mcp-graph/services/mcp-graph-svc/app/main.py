from fastapi import FastAPI
from .mcp_server import mcp_server
from .neo4j_client import run_cypher

app = FastAPI(title="MCP Graph Service")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
 
# Opcional: endpoint REST de prueba (sin MCP)
@app.post("/chat")
def chat(q: str):
    """
    Ejemplo minimalista: si el usuario pregunta "¿cuántos nodos Person?"
    resolvemos a Cypher fijo. En producción, usarías LLM para traducir NL→Cypher.
    """
    # PoC: detección naive
    if "cuántos" in q and "Person" in q:
        rows = run_cypher("MATCH (p:Person) RETURN count(p) AS total")
        return {"answer": rows[0]["total"] if rows else 0}
    return {"answer": "No sé aún. Usa MCP tool 'cypher_query' con tu prompt."}

# Exponer el servidor MCP por el mismo proceso
# (el SDK típicamente ofrece una forma de registrar/servir el MCP server;
#  aquí asumimos que el framework lo expone en un socket/JSON-RPC conforme doc del SDK)
mcp_app = mcp_server.asgi_app()  # si el SDK lo soporta
app.mount("/mcp", mcp_app)

