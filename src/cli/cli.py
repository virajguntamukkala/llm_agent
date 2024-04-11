import asyncio
import argparse
import os
import json
import importlib
from loguru import logger
from langchain_core.messages import AIMessage, HumanMessage

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def main():
    parser = argparse.ArgumentParser(description='Research Assistant CLI')
    parser.add_argument('--config', type=str, default='config/config.json', help='Path to the config.json file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    log_file = os.path.join(config['logging']['output'], 'cli.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger.remove()
    logger.add(log_file, format="{time} {level} {message}", rotation="10 MB", compression="zip")

    agent_config = config["agent"]['name']
    agent_module, agent_class = agent_config.split(".")
    agent_module = importlib.import_module(f"src.agent.{agent_module}")
    agent_class = getattr(agent_module, agent_class)
    agent_executor = agent_class(config['agent'])

    chat_history = []
    while True:
        try:
            query = input(bcolors.OKBLUE + "Enter your query (or type 'exit' or 'quit' to exit): " +  bcolors.ENDC)
            logger.info("Query: {}", query)
            if query.lower() in ["exit", "quit"]:
                logger.info("Exiting the CLI")
                print("Goodbye!")
                break

            if not query:
                print(bcolors.WARNING + "Please enter a query." + bcolors.ENDC)
                continue
            
            print(bcolors.OKBLUE + "Agent: ", end="" +  bcolors.ENDC) 
            result = await agent_executor.ainvoke(query, chat_history)
            print()
            logger.info("Agent response: {}", result['output'])

            chat_history.extend(
                [
                    HumanMessage(content=query),
                    AIMessage(content=result["output"]),
                ]
            )
        except KeyboardInterrupt:
            logger.info("CLI interrupted by user")
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
