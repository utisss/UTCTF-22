import asyncio
import websockets

from battleship_pb2 import *

ADDRESS = "misc1.utctf.live"
PORT = 9998
ORIGIN = ["Origin","http://" + ADDRESS + ":" + str(PORT)]

HEIGHT=20
WIDTH=20

def initialize():
    t = input('Captcha token: ')
    i = Initialize()
    i.g_captcha_response = t
    assert i.IsInitialized()
    return i

def ship(r,c,l,o):
    s = Ship(orientation=o,start=Point(row=r,col=c),length=l)
    assert s.IsInitialized()
    return s

def board():
    b = Board(ships = [ship(0,c,l,0) for c,l in zip(range(10), [5,4,3,3,2]*2)])
    b.width = WIDTH
    b.height = HEIGHT
    assert b.IsInitialized()
    return b

async def solve():
    async with websockets.connect("ws://" + ADDRESS + ":" + str(PORT) + "/websocket", extra_headers=[ORIGIN], ping_timeout=None) as websocket:
        await websocket.send(initialize().SerializeToString())
        await websocket.send(board().SerializeToString())
        for r in range(HEIGHT):
            for c in range(WIDTH):
                await websocket.send(Missile(target=Point(row=r,col=c)).SerializeToString())
        while True:
            print(await websocket.recv())

asyncio.run(solve())
