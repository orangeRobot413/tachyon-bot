import socket
from rcon.source import Client


async def rcon(port: int, password: str, cmd: str) -> str | None:
    try:
        with Client('127.0.0.1', int(port), passwd=password) as client:
            response = client.run(cmd)
            return response
    except socket.timeout:
        return
