from typing import Optional, Type
import arxiv
import aiohttp
import feedparser

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool


class ArxivRetrievalInput(BaseModel):
    query: str = Field(description="paper query")
    num_results: int = Field(description="number of results")


class ArxivRetrievalTool(BaseTool):
    name = "Arxivpaper"
    description = "useful for when you need to find research papers"
    args_schema: Type[BaseModel] = ArxivRetrievalInput

    def _run(self, query: str, num_results : int = 10, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=num_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = client.results(search)
        return list(results)
    
    async def _arun(self, query: str, num_results: int = 10, run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        """Use the tool asynchronously."""
        async with aiohttp.ClientSession() as session:
            url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={num_results}&sortBy=relevance"
            async with session.get(url) as response:
                data = await response.text()
                results = self._parse_arxiv_response(data)

        return results
    
    def _parse_arxiv_response(self, response_text: str):
        feed = feedparser.parse(response_text)
        results = []

        for entry in feed.entries:
            result = {
                "title": entry.title,
                "authors": [author.name for author in entry.authors],
                "published": entry.published,
                "id": entry.id.split("/")[-1],
                "summary": entry.summary,
                "pdf_url": None,
            }

            for link in entry.links:
                if link.rel == "alternate" and link.type == "application/pdf":
                    result["pdf_url"] = link.href
                    break

            results.append(result)

        return results