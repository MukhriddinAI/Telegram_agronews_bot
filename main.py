import json
import logging
import os
import re

from dotenv import load_dotenv
load_dotenv(override=True)

from agent import agronews_summarizer, news_filter_analyser
from config import GEMINI_MODELS, OUTPUTS_DIR, SEPARATOR
from crewai import Crew, LLM, Process
from scraper import scrape_agro_news
from task import filter_and_analyse_task, text_summarizer_task

logger = logging.getLogger(__name__)


def initialize_llm():
    """Initialize LLM using the first available model in the fallback chain."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model, description = GEMINI_MODELS[0]
    logger.info("Using model: %s", description)
    return LLM(model=model, api_key=api_key, temperature=0.7)


def crew_run():
    """Scrape news with BeautifulSoup then run the filter+summarizer crew."""
    logger.info(SEPARATOR)
    logger.info("AGRO NEWS SCRAPER - STARTING")
    logger.info(SEPARATOR)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Step 1: Scrape articles directly (no LLM agent needed)
    logger.info("Scraping news from websites...")
    scraped_articles = scrape_agro_news()
    if not scraped_articles:
        raise ValueError("No articles scraped from any source.")
    logger.info("Scraped %d articles total.", len(scraped_articles))

    try:
        llm = initialize_llm()
    except Exception as e:
        logger.error("LLM Initialization Error: %s", e)
        raise

    logger.info("Creating Agents...")
    agent_filter = news_filter_analyser(llm)
    agent_summary = agronews_summarizer(llm)
    logger.info("All agents created")

    logger.info("Creating Tasks...")
    task_filter = filter_and_analyse_task(agent_filter, scraped_articles)
    task_summary = text_summarizer_task(agent_summary)
    logger.info("All tasks created")

    logger.info("Starting Crew Workflow...")
    crew = Crew(
        agents=[agent_filter, agent_summary],
        tasks=[task_filter, task_summary],
        process=Process.sequential,
        verbose=False,
        max_rpm=10,
        full_output=True,
    )

    try:
        result = crew.kickoff(inputs={"topic": "Qishloq xo'jaligi yangiliklari"})
        logger.info("CREW WORKFLOW COMPLETED SUCCESSFULLY")

        raw = result.raw
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON array found in crew result")
        items = json.loads(match.group())
        logger.info("Parsed %d news items from result.", len(items))
        return items

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
