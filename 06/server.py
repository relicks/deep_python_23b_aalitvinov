import asyncio
from asyncio import StreamReader, StreamWriter
from queue import Queue

que: Queue[str] = Queue()


async def handle_url(reader: StreamReader, writer: StreamWriter) -> None:
    data = await reader.read(5000)
    url = data.decode()
    que.put(url)
    addr = writer.get_extra_info("peername")
    print(f"Received {url!r} from {addr!r}")
    print(f"{que.queue = }")

    writer.write(b"\x06")
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def handle_echo(reader: StreamReader, writer: StreamWriter) -> None:
    data = await reader.read(5000)
    message = data.decode()
    addr = writer.get_extra_info("peername")

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_url, "127.0.0.1", 8888)

    address = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {address}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
