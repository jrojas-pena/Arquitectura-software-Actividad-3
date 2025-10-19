from openai_agents.mcp import MCPServer, tool, Schema
from .neo4j_client import run_cypher

class CypherRequest(Schema):
        query: str
            params: dict | None = None

            class MCPGraphServer(MCPServer):
                    @tool(name="cypher_query", description="Ejecuta una consulta Cypher contra Neo4j")
                        def cypher_query(self, req: CypherRequest):
                                    data = run_cypher(req.query, req.params)
                                            return {"rows": data}

                                        mcp_server = MCPGraphServer(name="mcp-graph")

