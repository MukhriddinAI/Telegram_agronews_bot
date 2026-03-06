from crewai import Agent

_BASE_AGENT = dict(
    allow_code_execution=False,
    memory=False,
    verbose=False,
    allow_delegation=False,
    cache=True,
    max_retry_limit=2,
    max_rpm=5
)

def news_filter_analyser(llm):
    return Agent(
        role="News Filter and Analyser",
        goal="Fake/eski/takroriy yangiliklarni olib tashlash, so'ng eng muhim 2 ta yangilikni tanlash.",
        backstory="Agro yangiliklar tahlilchisi va fact-checking mutaxassisi",
        max_iter=1,
        max_execution_time=180,
        llm=llm,
        **_BASE_AGENT
    )

def agronews_summarizer(llm):
    return Agent(
        role="Agro News Summarizer",
        goal="Yangiliklarga jozibali, aniq sarlavha yozish va qisqacha mazmunini taqdim etuvchi agent",
        backstory="Telegram blog muharriri.",
        max_iter=1,
        max_execution_time=180,
        llm=llm,
        **_BASE_AGENT
    )