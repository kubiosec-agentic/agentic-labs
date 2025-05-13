from fastmcp import FastMCP, Client

# Create a client configured to talk to the backend server
# This could be any MCP server - remote, local, or using any transport
backend_client = Client("http://127.0.0.1:8001/mcp")  # Could be "http://remote.server/sse", etc.

# Create the proxy server with from_client()
proxy_server = FastMCP.from_client(
    backend_client,
    name="MyProxyServer",
    port=8002  # Optional settings for the proxy
)

# That's it! You now have a proxy FastMCP server that can be used
# with any transport (SSE, stdio, etc.) just like any other FastMCP server

if __name__ == "__main__":
    proxy_server.run(transport="sse")

