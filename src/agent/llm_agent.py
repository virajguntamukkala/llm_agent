from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks import FileCallbackHandler

import json
import importlib
from loguru import logger
import argparse


def main():
    parser = argparse.ArgumentParser(description="Research Helper LLM Agent",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("config_file", help="Config file location")
    args = parser.parse_args()

    with open(args.config_file) as f:
        config = json.load(f)

    logfile = config['logging']['output']
    logger.add(logfile, colorize=True, enqueue=True)
    handler = FileCallbackHandler(logfile)

    tools_config = config['tools']
    tools = []

    for tool in tools_config:
        tool_module = importlib.import_module(tool['module'])
        tool_fn = getattr(tool_module, tool['name'])
        tools.append(tool_fn)

    llm = ChatOpenAI(model=config['llm']['model'], temperature=config['llm']['temperature'])

    MEMORY_KEY = "chat_history"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                config['prompts']['initial'],
            ),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm_with_tools = llm.bind_tools(tools)
    chat_history = []

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, callbacks=[handler], verbose=True)

    while True:
        query = input("Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        result = agent_executor.invoke({"input": query, "chat_history": chat_history})

        chat_history.extend(
            [
                HumanMessage(content=query),
                AIMessage(content=result["output"]),
            ]
        )
        logger.info([
                HumanMessage(content=query),
                AIMessage(content=result["output"]),
            ])


if __name__ == "__main__":
    main()
