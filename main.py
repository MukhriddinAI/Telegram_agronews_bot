from sources import news_urls_uz, news_urls_world
from task import news_scraper_task, text_summerizer_task
from agent import agronews_scraper, agronews_summarizer
from crewai import Crew ,LLM , Process
from dotenv import load_dotenv
import litellm
from crewai_tools import SerperDevTool
import os

load_dotenv()
searching_tool = SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))

def run():
    # LLM
    Llm = LLM(
    provider= "litellm" ,
    model = "gemini/gemini-2.5-flash" ,
    api_key=os.getenv("GOOGLE_API_KEY"))
    # Agent
    agent1 = agronews_scraper(Llm,searching_tool)
    agent2 = agronews_summarizer(Llm,searching_tool)
    task1 = news_scraper_task(searching_tool,agent1,links=[news_urls_uz,news_urls_world])
    task2 = text_summerizer_task(searching_tool,agent2,links=[news_urls_uz,news_urls_world])


    crew = Crew(agents=[agent1,agent2], tasks=[task1,task2],
                process=Process.sequential,
                tracing=True,
                verbose=True,
                max_rpm=3)
    
    result = crew.kickoff(inputs={"topic": "Qishloq xo'jaligi yangiliklari"})

    return result