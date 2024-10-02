import asyncio
import websockets
import console
import colorama

# initialize
colorama.init(autoreset=True)
console_ = console.CommandLine()
websocket_ = []


async def command_send(user_input: str):
    """ send message to server"""
    arg: str = " ".join(user_input.split(' ')[1:])
    await websocket_.send(arg)
    console_.log(arg)


console_.add_command("send", command_send)


async def monitor_ws():
    global websocket_
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websocket:
        websocket_ = websocket
        # async for message in websocket:
        while True:
            response = await websocket.recv()
            console_.log(f"Server response: {response}")


async def main():
    spammer_task = asyncio.create_task(monitor_ws())
    input_task = asyncio.create_task(console_.input_loop())
    _done, pending = await asyncio.wait([spammer_task, input_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


asyncio.run(main())
