import importlib

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class ResearchAssistantAgent:
    def __init__(self, config):
        tools = []
        for tool in config['tools']:
            tool_module = importlib.import_module(f"src.tools.{tool['module']}")
            tool_class = getattr(tool_module, tool['name'])
            tools.append(tool_class())

        llm = ChatOpenAI(
            model=config['llm']['model'],
            temperature=config['llm']['temperature'],
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        MEMORY_KEY = "chat_history"
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    config['prompts']['system']
                ),
                MessagesPlaceholder(variable_name=MEMORY_KEY),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=config['verbose'])


    async def ainvoke(self, query, chat_history):
        try:
            return await self.agent_executor.ainvoke({"input": query, "chat_history": chat_history})
        except Exception as e:
            raise RuntimeError(f"Error invoking agent: {str(e)}")
  

    async def astream(self, query, chat_history):
        async for response in self.agent_executor.astream({"input": query, "chat_history": chat_history}):
            if isinstance(response, str):
                yield response
            elif hasattr(response, 'output'):
                yield response['output']