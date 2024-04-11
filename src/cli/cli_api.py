import asyncio
import json
import os
import sys
import websockets
import argparse
from loguru import logger
from langchain_core.messages import AIMessage, HumanMessage


async def chat_with_agent(config):
    url = config['api']['url']
    chat_history = []
    while True:
        try:
            async with websockets.connect(url) as websocket:
                while True:
                    query = input("Enter your query (or type 'exit' to quit): ")
                    if query.lower() in ["exit", "quit"]:
                        logger.info("Exiting the CLI")
                        print("Goodbye!")
                        return

                    chat_history_json = [
                        {"role": "human", "content": message.content}
                        if isinstance(message, HumanMessage)
                        else {"role": "ai", "content": message.content}
                        for message in chat_history
                    ]

                    await websocket.send(json.dumps({"input": query, "chat_history": chat_history_json}))
                    response = await websocket.recv()
                    logger.info("Agent response: {}", response)
                    print(f"Agent: {response}")

                    chat_history.append(HumanMessage(content=query))
                    chat_history.append(AIMessage(content=response))

        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(config['api']['reconnect_delay'])


async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Research Assistant CLI API')
    parser.add_argument('--config', type=str, default='config/config.json', help='Path to the config.json file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    log_file = os.path.join(config['logging']['output'], 'cli_api.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger.remove()
    logger.add(log_file, format="{time} {level} {message}", rotation="10 MB", compression="zip")

    await chat_with_agent(config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical("Unhandled exception: {}", e)
        print(f"An unhandled exception occurred: {e}")
        sys.exit(1)