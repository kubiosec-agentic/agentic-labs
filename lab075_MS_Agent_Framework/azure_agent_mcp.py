import asyncio
from agent_framework import ChatAgent, MCPStreamableHTTPTool, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def http_mcp_example():
    """Example using an HTTP-based MCP server."""
    async with (
        AzureCliCredential() as credential,
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
           # headers={"Authorization": "Bearer your-token"},
        ) as mcp_server,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            name="DocsAgent",
            instructions="You help with Microsoft documentation questions.",
            # tools=[
            #     HostedWebSearchTool(
            #         additional_properties={
            #             "user_location": {
            #                 "city": "Seattle",
            #                 "country": "US"
            #             }
            #         }
            #     )
            # ]
        ) as agent,
    ):
        result = await agent.run(
            "How to run the dev ui in the microsoft agent framework for a python app?",
            tools=mcp_server
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(http_mcp_example())
