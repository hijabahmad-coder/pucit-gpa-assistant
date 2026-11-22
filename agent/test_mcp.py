import asyncio, os
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv()
url = os.getenv("MCP_URL")
print("URL:", repr(url))

async def main():
    async with Client(url) as c:
        tools = await c.list_tools()
        print(len(tools), [t.name for t in tools])

asyncio.run(main())