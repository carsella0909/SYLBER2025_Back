from json import loads

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio import AsyncServer, ASGIApp

from routers.user import router as user_router
from routers.room import router as room_router
from sio.game import GameNamespace


CONFIG = loads(open("config.json").read())
HOST = CONFIG["host"]
PORT = CONFIG["port"]

app = FastAPI()

# Allow CORS for all origins
origins = [
    "http://192.168.175.18:8000",
    "http://192.168.175.162:5173",
    "http://192.168.175.213",
    "http://localhost:5173",
    "http://192.168.175.162",
    "http://0.0.0.0:8000",
    "http://0.0.0.0"
]

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)

sio = AsyncServer(async_mode='asgi', cors_allowed_origins=origins, ping_timeout=60)
game_namespace = GameNamespace('/game')
sio.register_namespace(game_namespace)
sio_app = ASGIApp(sio, app)
app.mount('/socket.io', sio_app)

# Include the user router
app.include_router(user_router)
# Include the room router
app.include_router(room_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
