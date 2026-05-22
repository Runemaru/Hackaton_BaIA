import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from Hackaton_BaIA.api.websocket_manager import WebSocketManager
from Hackaton_BaIA.api.prediction_worker import consume_prediction_events

manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(
        consume_prediction_events(manager.broadcast)
    )

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "API online",
        "websocket": "/ws/predictions"
    }


@app.websocket("/ws/predictions")
async def websocket_predictions(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
