import asyncio
import websockets
import colorama
from datetime import datetime
from colorama import Fore
import console
import json

# all Init
colorama.init(autoreset=True)
clients = set()  # client list
server_cycle = False
# open config with text
with open('config.json', 'r', encoding="utf-8") as file:
    config = json.load(file)
websocket_server = None


async def on_close(websocket):  # client disconnection...
    """
    Function for safely removing client from client set
    Also with this func. you will not have any errors X)
    """
    # remove client from websocket set
    clients.remove(websocket)

    # get action time
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    # print "safe" message
    client_leave_msgs: list[str, str] = config["client_leave"]
    console_.log(client_leave_msgs[0].format(color1=Fore.BLACK, color2=Fore.CYAN))
    console_.log(client_leave_msgs[1].format(color1=Fore.CYAN, color2=Fore.LIGHTWHITE_EX,
                                             client_adres=websocket.remote_address,
                                             left_time=formatted_now))


def on_close_callback(websocket):
    """sync wrap for call-back async func"""
    asyncio.create_task(on_close(websocket))


async def send_message_to_clients(message):
    """Sends the message to all clients in clients set"""
    for client in clients:
        await client.send(message)


async def receive_messages(websocket):
    """"Receive messages from all clients in clients set"""
    # get action time
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    # print "safe" message about client joining
    client_connection_msgs: list[str, str] = config["client_connection"]
    text1 = client_connection_msgs[0].format(color1=Fore.BLACK, color2=Fore.CYAN)
    text2 = client_connection_msgs[1].format(color1=Fore.CYAN, color2=Fore.LIGHTWHITE_EX,
                                             client_adres=websocket.remote_address,
                                             join_time=formatted_now)

    console_.log(text1)
    console_.log(text2)
    # send this to all clients
    await send_message_to_clients(text1)
    await send_message_to_clients(text2)

    while len(clients) != 0:
        # some things with received message
        await asyncio.sleep(1)
        client_response = await websocket.recv()
        client_message_msg: list[str, str] = config["client_message"]
        text = client_message_msg[0].format(color1=Fore.CYAN, color2=Fore.LIGHTWHITE_EX,
                                            response=client_response,
                                            client_adres=websocket.remote_address)

        console_.log(text)
        await send_message_to_clients(text)


async def handler(websocket, path):
    """Add client to client list"""
    clients.add(websocket)
    # add asynch tasks
    wait_closed_task = asyncio.create_task(websocket.wait_closed())
    receive_task = asyncio.create_task(receive_messages(websocket))
    # msg receive is working until wait closed task stops (to prevent error)
    done, pending = await asyncio.wait(
        [wait_closed_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    # finally closing all tasks
    for task in pending:
        task.cancel()
    # close socket
    on_close_callback(websocket)


async def close_server(input_command: str):
    websocket_server.close()
    return True


async def run_server(input_command: str):
    """Run web-server"""
    global server_cycle, websocket_server
    server_cycle = True
    # get event time
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    # server start log
    client_leave_msgs: list[str, str] = config["server_launch"]
    console_.log(f"{client_leave_msgs[0].format(color1=Fore.BLACK, color2=Fore.CYAN)}")
    console_.log(f"{client_leave_msgs[1].format(color1=Fore.CYAN, color2=Fore.LIGHTWHITE_EX, start_time=formatted_now)}")
    # starting server
    server_settings: dict = config["server_settings"]
    websocket_server = await websockets.serve(handler, server_settings["host"], server_settings["port"])


async def main():
    """Main function"""
    input_task = asyncio.create_task(console_.input_loop())
    _done, pending = await asyncio.wait([input_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


if __name__ == "__main__":
    starter_msg: str = config["starter_message"]
    print(starter_msg.format(color1=Fore.CYAN, color2=Fore.BLACK, author="TosiX"))

    console_ = console.CommandLine(f"{Fore.CYAN}$ ", {
        "broadcast-server start": run_server,
        "broadcast-server stop": [console.break_console, close_server]
    })

    asyncio.run(main())
