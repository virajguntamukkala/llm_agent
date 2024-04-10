import asyncio
import json
import os
import websockets
import streamlit as st
import time
from loguru import logger
import argparse


def response_generator(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

async def chat_with_agent(query, chat_history, websocket):
    await websocket.send(json.dumps({"input": query, "chat_history": chat_history}))
    response = await websocket.recv()
    return chat_history + [{"role": "human", "content": query}, {"role": "ai", "content": response}]

async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Streamlit App')
    parser.add_argument('--config', type=str, default='config/config.json', help='Path to the config.json file')
    args = parser.parse_args()

    # Load configuration from the specified file
    config_path = args.config
    with open(config_path) as f:
        config = json.load(f)

    # Configure logging
    log_file = os.path.join(config['logging']['output'], 'app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger.remove()
    logger.add(log_file, format="{time} {level} {message}", rotation="10 MB", compression="zip")

    st.set_page_config(page_title=config['app']['title'])
    st.title(config['app']['title'])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    try:
        async with websockets.connect(config['api']['url']) as websocket:
            user_input = st.chat_input("Ask any research questions...")
            while True:
                if user_input:
                    for idx, message in enumerate(st.session_state.chat_history):
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    with st.spinner("Waiting for response..."):
                        st.session_state.chat_history = await chat_with_agent(user_input, st.session_state.chat_history, websocket)
                    with st.chat_message(st.session_state.chat_history[-2]["role"]):
                        st.markdown(st.session_state.chat_history[-2]["content"])
                    with st.chat_message(st.session_state.chat_history[-1]["role"]):
                        st.write_stream(response_generator(st.session_state.chat_history[-1]["content"]))

                    user_input = None
                else:
                    await asyncio.sleep(0.1)  # Sleep briefly to avoid busy-waiting
    except websockets.exceptions.ConnectionClosed:
        logger.error("WebSocket connection closed. Reconnecting...")
        await asyncio.sleep(config['api']['reconnect_delay'])
        await main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical("Unhandled exception: {}", e)
        st.error(f"An unhandled exception occurred: {e}")
        raise e
