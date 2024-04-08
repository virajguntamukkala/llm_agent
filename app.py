import asyncio
import websockets

async def chat_with_agent():
    async with websockets.connect("ws://localhost:8000/chat",  ping_interval=None) as websocket:
        while True:
            query = input("Enter your query (or type 'exit' to quit): ")
            if query.lower() == "exit":
                await websocket.send("exit")
                break
            await websocket.send(query)
            response = await websocket.recv()
            print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(chat_with_agent())
