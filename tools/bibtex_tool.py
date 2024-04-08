from langchain_core.tools import tool
import bibtexparser
import arxiv2bib

@tool
def bibtex_retrieval(query: str) -> str:
    """Retrieve Bibtex information for the given query."""
    with open("bibtex_file.bib", "r") as file:
        bibtex_data = file.read()
    
    # Parse the Bibtex file using bibtexparser
    bib_database = bibtexparser.loads(bibtex_data)
    
    # Search for the relevant Bibtex entry based on the query
    for entry in bib_database.entries:
        if query in entry["title"] or query in entry["author"]:
            return entry["title"]
    
    return "No matching Bibtex entry found."


@tool
def bibtex_generation(arxiv_id_nums : list):
        """Generate Bibtex entry for the given Arxiv paper id number as a list."""
        bibtex_entries = arxiv2bib.arxiv2bib(arxiv_id_nums)
        return '\n\n'.join(str(v.bibtex()) for v in bibtex_entries)
    

# @tool
# def bibtex_generation(arxiv_paper_info: str) -> str:
#     """Generate Bibtex entry for the given Arxiv paper information."""
#     print('arxiv_paper_info', arxiv_paper_info)
#     bib_database = bibtexparser.loads(arxiv_paper_info)
#     print('bib_database', bib_database)
#     return bibtexparser.dumps(bib_database)

