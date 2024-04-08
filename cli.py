# cli.py
import asyncio
from llm import create_agent
from langchain_core.messages import AIMessage, HumanMessage

async def cli():
    agent_executor = await create_agent("config.json")
    chat_history = []
    while True:
        query = input("Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        result = await agent_executor.ainvoke({"input": query, "chat_history": chat_history})
        print(result["output"])

        chat_history.extend(
            [
                HumanMessage(content=query),
                AIMessage(content=result["output"]),
            ]
        )

if __name__ == "__main__":
    asyncio.run(cli())
