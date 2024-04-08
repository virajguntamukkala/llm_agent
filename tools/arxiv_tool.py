from langchain_core.tools import tool
import arxiv

@tool
def arxiv_retrieval(query, num_results=10):
    """A tool to retrieve information from Arxiv."""
    client = arxiv.Client()

    search = arxiv.Search(
        query = query,
        max_results = num_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    results = client.results(search)
    all_results = list(results)

    return all_results
