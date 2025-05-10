from json import loads

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.user import router as user_router


CONFIG = loads(open("config.json").read())
HOST = CONFIG["host"]
PORT = CONFIG["port"]

app = FastAPI()

# Allow CORS for all origins
origins = [
    "http://localhost:3000",
]

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the user router
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
