import json
import importlib
import os
import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
import uvicorn

agent = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

def load_agent(config):
    agent_config = config["agent"]['name']
    agent_module, agent_class = agent_config.split(".")
    agent_module = importlib.import_module(f"src.agent.{agent_module}")
    agent_class = getattr(agent_module, agent_class)
    return  agent_class(config['agent'])

def parse_config(config):
    with open(config) as f:
        config = json.load(f)

    log_file = os.path.join(config['logging']['output'], 'api.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger.remove()
    logger.add(log_file, format="{time} {level} {message}", rotation="10 MB", compression="zip")

    global agent
    agent = load_agent(config)

@asynccontextmanager
async def lifespan(app):
    try:
        parser = argparse.ArgumentParser(description='Research Assistant API')
        parser.add_argument('--config', type=str, default='config/config.json', help='Path to the config.json file')
        args = parser.parse_args()
        parse_config(config=args.config)
    except:
        default_config = 'config/config.json'
        parse_config(default_config)
    yield 

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            query = await websocket.receive_text()
            query = json.loads(query)
            result = await agent.ainvoke(query["input"], query["chat_history"])
            response = result["output"]
            logger.info(f"Sending response: {response}")
            await manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await manager.send_personal_message(f"An error occurred: {e}", websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
