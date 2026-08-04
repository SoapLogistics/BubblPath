import logging
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", module="duckduckgo_search")
    from duckduckgo_search import DDGS

logger = logging.getLogger("solomon_web_crawler")

class SolomonWebCrawler:
    """
    Equips Solomon with the ability to scrape the live internet using DuckDuckGo.
    This replaces all simulation with hard reality.
    """
    def __init__(self):
        self.ddgs = DDGS()

    def search_and_extract(self, query: str, max_results: int = 3) -> str:
        """
        Executes a live web search for a given query and compiles the text snippets.
        """
        logger.info(f"[WEB CRAWLER] Initiating live web extraction for query: '{query}'")
        try:
            results = self.ddgs.text(query, max_results=max_results)
            extracted_text = []
            
            for idx, res in enumerate(results):
                title = res.get('title', 'Unknown Title')
                body = res.get('body', '')
                extracted_text.append(f"[{idx+1}] {title}: {body}")
                
            if not extracted_text:
                return f"[WEB CRAWLER FAILURE] No live data found for query: {query}"
                
            return " | ".join(extracted_text)
            
        except Exception as e:
            logger.error(f"[WEB CRAWLER EXCEPTION] {e}")
            return f"[WEB CRAWLER FAILURE] Connection to live internet severed: {e}"
