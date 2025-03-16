import socket
import asyncio
from typing import List

class Server:
    tasks = []

    def __init__(self):
        pass

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while True:
            msg = await reader.read(4096)
            print(msg)

async def main():
    IP = "26.181.96.20"
    PORT = 55557

    server = await asyncio.start_server(
        lambda r, w: Server().handle(r, w),
        IP, PORT
    )

    async with server:
        await server.serve_forever()

asyncio.run(main())
