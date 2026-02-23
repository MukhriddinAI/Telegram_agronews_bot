from sources import news_urls_uz, news_urls_world
from agent import agronews_scraper, agronews_summarizer, news_analyser, validator
from task import news_scraper_task, text_summerizer_task, validator_task, analyser_task

from crewai import Crew, LLM, Process
from crewai.tools import tool
from dotenv import load_dotenv
import os
from duckduckgo_search import DDGS
import time

load_dotenv(override=True)

@tool("Search the web")
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=3)  # Reduced to 3 for faster results
        
        if not results:
            return "No results found."
        
        # Format results nicely
        formatted_results = []
        for result in results:
            formatted_results.append(
                f"Title: {result['title']}\n"
                f"Link: {result['href']}\n"
                f"Description: {result['body']}\n"
            )
        
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Search error: {str(e)}"


def initialize_llm():
    """
    Initialize LLM with fallback options.
    Priority: gemini-1.5-flash > gemini-2.0-flash > gemini-2.5-flash
    """
    models_to_try = [
        ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("gemini/gemini-2.5-flash-preview-04-17", "Gemini 2.5 Flash Preview"),
        ("gemini/gemini-2.0-flash-exp", "Gemini 2.0 Flash Experimental"),
    ]
    
    for model, description in models_to_try:
        try:
            print(f"🔄 Trying to initialize: {description}")
            llm = LLM(
                provider="litellm",
                model=model,
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            )
            print(f"✅ Successfully initialized: {description}")
            return llm
        except Exception as e:
            print(f"⚠️ Failed to initialize {description}: {str(e)}")
            continue
    
    raise Exception("❌ All LLM initialization attempts failed. Check your API key and quota.")


def crew_run(search_tool=duckduckgo_search):
    """
    Main function to run the crew workflow
    """
    print("=" * 60)
    print("🌾 AGRO NEWS SCRAPER - STARTING")
    print("=" * 60)
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Initialize LLM with fallback
    try:
        Llm = initialize_llm()
    except Exception as e:
        print(f"❌ LLM Initialization Error: {e}")
        raise
    
    # Small delay to avoid immediate rate limiting
    time.sleep(2)
    
    # Agents
    print("\n📋 Creating Agents...")
    agent1 = agronews_scraper(Llm, duckduckgo_search)
    agent2 = validator(Llm)
    agent3 = news_analyser(Llm)
    agent4 = agronews_summarizer(Llm)
    print("✅ All agents created")
    
    # Tasks
    print("\n📝 Creating Tasks...")
    task1 = news_scraper_task(duckduckgo_search, agent1, links=[news_urls_uz, news_urls_world])
    task2 = validator_task(agent2)
    task3 = analyser_task(agent3)
    task4 = text_summerizer_task(agent4)
    print("✅ All tasks created")
    
    # Crew kickoff
    print("\n🚀 Starting Crew Workflow...")
    print("-" * 60)
    
    crew = Crew(
        agents=[agent1, agent2, agent3, agent4],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True,
        max_rpm=10,  # Global rate limit
        full_output=True
    )
    
    try:
        result = crew.kickoff(inputs={"topic": "Qishloq xo'jaligi yangiliklari"})
        print("\n" + "=" * 60)
        print("✅ CREW WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)
        return result
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ CREW WORKFLOW FAILED: {str(e)}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    try:
        final_result = crew_run()
        print("\n📊 Final Result:")
        print(final_result)
    except Exception as e:
        print(f"\n❌ Main execution failed: {e}")
        print("\n💡 Suggestions:")
        print("   1. Check your Google API key in .env file")
        print("   2. Verify your API quota at https://ai.dev/rate-limit")
        print("   3. Wait for quota reset (midnight Pacific Time)")
        print("   4. Consider upgrading to paid tier for higher limits")