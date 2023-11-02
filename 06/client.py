import asyncio
import json
import threading


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection("localhost", 8888)

    print(f"Send: {message!r}")
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1000)

    # print(f"Received: {data.decode()!r}")
    print("Received:")

    print("Close the connection")
    writer.close()
    await writer.wait_closed()
    print(json.loads(data.decode()))
    return json.loads(data.decode())


# for _ in range(10):
#     th = threading.Thread(
#         target=asyncio.run,
#         args=(tcp_echo_client("https://ru.wikipedia.org/wiki/Python"),),
#     )
#     th.start()

with open("./urls.txt") as fs:
    urls_list = fs.read().split("\n")
