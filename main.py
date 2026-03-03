import os
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

from sources import NEWS_SOURCES
from agent import agronews_scraper, agronews_summarizer, news_analyser, validator
from task import news_scraper_task, text_summarizer_task, validator_task, analyser_task
from config import SEPARATOR, OUTPUTS_DIR, GEMINI_MODELS
from crewai import Crew, LLM, Process
from crewai.tools import tool
from duckduckgo_search import DDGS
import litellm

logger = logging.getLogger(__name__)


@tool("Search the web")
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=3)
        if not results:
            return "No results found."
        formatted = [
            f"Title: {r['title']}\nLink: {r['href']}\nDescription: {r['body']}\n"
            for r in results
        ]
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {e}"


def initialize_llm():
    """Initialize LLM with model fallback chain defined in config.GEMINI_MODELS.

    Makes a minimal probe call per model to verify it is accessible before
    returning — this ensures the fallback chain actually triggers on quota
    or auth errors rather than always returning the first model.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    for model, description in GEMINI_MODELS:
        try:
            logger.info("Probing model: %s", description)
            litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                api_key=api_key,
            )
            llm = LLM(
                provider="litellm",
                model=model,
                api_key=api_key,
                temperature=0.7,
            )
            logger.info("Successfully initialized: %s", description)
            return llm
        except Exception as e:
            logger.warning("Model %s unavailable: %s", description, e)
    raise RuntimeError("All LLM initialization attempts failed. Check your API key and quota.")


def crew_run(search_tool=None):
    """Run the full crew workflow and return the raw result."""
    if search_tool is None:
        search_tool = duckduckgo_search

    logger.info(SEPARATOR)
    logger.info("AGRO NEWS SCRAPER - STARTING")
    logger.info(SEPARATOR)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    try:
        llm = initialize_llm()
    except Exception as e:
        logger.error("LLM Initialization Error: %s", e)
        raise

    logger.info("Creating Agents...")
    agent1 = agronews_scraper(llm, search_tool)
    agent2 = validator(llm)
    agent3 = news_analyser(llm)
    agent4 = agronews_summarizer(llm)
    logger.info("All agents created")

    logger.info("Creating Tasks...")
    task1 = news_scraper_task(search_tool, agent1, sources=NEWS_SOURCES)
    task2 = validator_task(agent2)
    task3 = analyser_task(agent3)
    task4 = text_summarizer_task(agent4)
    logger.info("All tasks created")

    logger.info("Starting Crew Workflow...")
    crew = Crew(
        agents=[agent1, agent2, agent3, agent4],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=False,
        max_rpm=10,
        full_output=True,
    )

    try:
        result = crew.kickoff(inputs={"topic": "Qishloq xo'jaligi yangiliklari"})
        logger.info("CREW WORKFLOW COMPLETED SUCCESSFULLY")
        return result
    except Exception as e:
        logger.error("CREW WORKFLOW FAILED: %s", e)
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        final_result = crew_run()
        print("\nFinal Result:")
        print(final_result)
    except Exception as e:
        logger.error("Main execution failed: %s", e)
        raise SystemExit(1)
