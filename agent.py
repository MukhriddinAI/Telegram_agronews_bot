from crewai import Agent

_BASE_AGENT = dict(
    allow_code_execution=False,
    memory=False,
    reasoning=False,
    tracing=False,
    verbose=False,
    allow_delegation=False,
    cache=True,
    max_retry_limit=2,
    max_concurrent_executions=1,
    max_rpm=5,
)


def agronews_scraper(llm, searching_tool):
    return Agent(
        role="Agro News Scraper",
        goal="O'zbekiston va Jahon bo'ylab qishloq xo'jaligi eng muhim yangiliklarini 10 ta vebsaytdan yig'ish.",
        backstory="Agro sohada 20 yillik tajribaga ega jurnalist",
        max_iter=3,
        max_execution_time=120,
        llm=llm,
        tools=[searching_tool],
        **_BASE_AGENT,
    )


def validator(llm):
    return Agent(
        role="News Validator",
        goal="Fake, takroriy va eski yangiliklarni aniqlash.",
        backstory="Fact-checking mutaxassisi",
        max_iter=2,
        max_execution_time=90,
        llm=llm,
        **_BASE_AGENT,
    )


def news_analyser(llm):
    return Agent(
        role="News analyser",
        goal="Eng muhim yangiliklarni aniqlash.",
        backstory="Agro yangiliklar tahlilchisi",
        max_iter=2,
        max_execution_time=90,
        llm=llm,
        **_BASE_AGENT,
    )


def agronews_summarizer(llm):
    return Agent(
        role="Agro News Summarizer",
        goal="Yangiliklarga jozibali, aniq sarlavha yozish va qisqacha mazmunini taqdim etuvchi agent",
        backstory="Telegram blog muharriri.",
        max_iter=2,
        max_execution_time=90,
        llm=llm,
        **_BASE_AGENT,
    )
