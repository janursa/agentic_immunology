# Literature — Function Reference

> Module: `tool.literature`
> Import: `from tool.literature import <function_name>`

**8 functions** — PubMed/Semantic Scholar search, paper retrieval, citation analysis

```python
from tool.literature import <function_name>
```

---

### `fetch_supplementary_info_from_doi`
*Supplementary Retrieval*
Fetches supplementary information for a paper given its DOI and saves it to a specified directory.

**Required:** `doi` (str)
**Optional:** `output_dir='supplementary_info'` (str)

### `query_arxiv`
*arXiv Search*
Query arXiv for papers based on the provided search query.

**Required:** `query` (str)
**Optional:** `max_papers=10` (int)

### `query_scholar`
*Google Scholar*
Query Google Scholar for papers based on the provided search query and return the first search result.

**Required:** `query` (str)
**Optional:** —

### `query_pubmed`
*PubMed Search*
Query PubMed for papers based on the provided search query.

**Required:** `query` (str)
**Optional:** `max_papers=10` (int), `max_retries=3` (int)

### `search_google`
*Google Search*
Search using Google search and return formatted results.

**Required:** `query` (str)
**Optional:** `num_results=3` (int), `language='en'` (str)

### `extract_url_content`
*URL Content Extraction*
Extract the text content of a webpage using requests and BeautifulSoup.

**Required:** `url` (str)
**Optional:** —

### `extract_pdf_content`
*PDF Content Extraction*
Extract text content from a PDF file.

**Required:** `url` (str)
**Optional:** —

### `advanced_web_search_claude`
*Advanced Web Search*
Initiate an advanced web search by launching a specialized agent to collect relevant information and citations through multiple rounds of web searches for a given query.

**Required:** `query` (str)
**Optional:** `max_searches=1` (int), `max_retries=3` (int)
