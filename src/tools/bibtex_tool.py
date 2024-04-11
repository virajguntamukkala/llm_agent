from typing import Optional, Type
import arxiv2bib

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool


class BibtexGenerationInput(BaseModel):
    arxiv_id_nums: list[str] = Field(description="arxiv paper ids")


class BibtexGenerationTool(BaseTool):
    name = "BibTexGeneration"
    description = "useful for when you need to create a bibtex for a paper(s)"
    args_schema: Type[BaseModel] = BibtexGenerationInput

    def _run(self, arxiv_id_nums: list[str], run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        bibtex_entries = arxiv2bib.arxiv2bib(arxiv_id_nums)
        return '\n\n'.join(str(v.bibtex()) for v in bibtex_entries)

    async def _arun(self, arxiv_id_nums: list[str], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        bibtex_entries = await self._get_bibtex_entries(arxiv_id_nums)
        return '\n\n'.join(str(v.bibtex()) for v in bibtex_entries)

    async def _get_bibtex_entries(self, arxiv_id_nums: list[str]) -> list:
        """Get the Bibtex entries for the given Arxiv paper IDs."""
        return arxiv2bib.arxiv2bib(arxiv_id_nums)