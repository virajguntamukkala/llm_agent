# api.py
from fastapi import FastAPI, WebSocket
from llm import create_agent
from langchain_core.messages import AIMessage, HumanMessage

app = FastAPI()

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    agent_executor = await create_agent("config.json")
    chat_history = []
    while True:
        query = await websocket.receive_text()
        if query.lower() == "exit":
            await websocket.close()
            break
        result = await agent_executor.ainvoke({"input": query, "chat_history": chat_history})
        chat_history.extend(
            [
                HumanMessage(content=query),
                AIMessage(content=result["output"]),
            ]
        )
        await websocket.send_text(result["output"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)