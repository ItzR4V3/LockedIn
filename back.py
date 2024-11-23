from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect

app = FastAPI()
connections = {}

@app.websocket("/ws/{client_type}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str):
    await websocket.accept()
    connections[client_id] = {"type": client_type, "socket": websocket}
    print(f"{client_type} connected: {client_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from {client_id}: {data}")
    except WebSocketDisconnect:
        del connections[client_id]
        print(f"{client_id} disconnected")

async def send_message(client_id: str, message: str):
    if client_id in connections:
        await connections[client_id]["socket"].send_text(message)

# Test endpoint for sending commands
@app.post("/send/{client_id}/{message}")
async def send_to_client(client_id: str, message: str):
    await send_message(client_id, message)
    return {"status": "Message sent"}
