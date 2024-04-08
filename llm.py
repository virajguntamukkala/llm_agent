# llm.py
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
import json
import importlib

async def create_agent(config_path):
    with open(config_path) as f:
        config = json.load(f)

    tools_config = config['tools']
    tools = []

    for tool in tools_config:
        tool_module = importlib.import_module(tool['module'])
        tool_fn = getattr(tool_module, tool['name'])
        tools.append(tool_fn)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    MEMORY_KEY = "chat_history"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are very powerful assistant",
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
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
