import os
from crewai import Agent
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def agronews_scraper(LLM, searching_tool):
    return Agent(
        role="Agro News Scraper",
        goal="O'zbekiston va Jahon bo'ylab qishloq xo'jaligi eng muhim yangiliklarini 10 ta vebsaytdan yig'ish.",
        backstory="Agro sohada 20 yillik tajribaga ega jurnalist",
        allow_code_execution=False,
        memory=False,
        reasoning=False,
        tracing=False,
        verbose=False,
        allow_delegation=False,
        cache=True,
        max_iter=3,  # Limit iterations to reduce API calls
        max_execution_time=120,
        max_retry_limit=2,  # Reduced from 3
        max_concurrent_executions=1,  # Reduced to minimize parallel calls
        max_rpm=5,  # Increased slightly for better flow
        llm=LLM,
        tools=[searching_tool]
    )

def validator(LLM):
    return Agent(
        role="News Validator",
        goal="Fake, takroriy va eski yangiliklarni aniqlash.",
        backstory="Fact-checking mutaxassisi",
        allow_code_execution=False,
        memory=False,
        reasoning=False,
        tracing=False,
        verbose=False,
        allow_delegation=False,
        cache=True,
        max_iter=2,  # Limit iterations
        max_execution_time=90,
        max_retry_limit=2,
        max_concurrent_executions=1,
        max_rpm=5,
        llm=LLM
    )

def news_analyser(LLM):
    return Agent(
        role="News analyser",
        goal="Eng muhim yangiliklarni aniqlash.",
        backstory="Agro yangiliklar tahlilchisi",
        allow_code_execution=False,
        memory=False,
        reasoning=False,
        tracing=False,
        verbose=False,
        allow_delegation=False,
        cache=True,
        max_iter=2,  # Limit iterations
        max_execution_time=90,
        max_retry_limit=2,
        max_concurrent_executions=1,
        max_rpm=5,
        llm=LLM
    )
    
def agronews_summarizer(LLM):
    return Agent(
        role="Agro News Summarizer",
        goal="Yangiliklarga jozibali, aniq sarlavha yozish va qisqacha mazmunini taqdim etuvchi agent",
        backstory="Telegram blog muharriri.",
        allow_code_execution=False,
        memory=False,
        reasoning=False,
        tracing=False,
        verbose=False,
        allow_delegation=False,
        cache=True,
        max_iter=2,  # Limit iterations
        max_execution_time=90,
        max_retry_limit=2,
        max_concurrent_executions=1,
        max_rpm=5,
        llm=LLM
    )