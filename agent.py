from crewai import Agent

def agronews_scraper(LLM,searching_tool):
    return Agent(
        role = "Agro News Scraper",
        goal = "O'zbekiston va Jahon bo'ylab qishloq xo'jaligi yangiliklarini taqdim etuvchi agent.",
        backstory = ("Eng so'nggi qishloq xo'jaligi yangiliklari,\n"
                     "texnologiyalari va tendentsiyalari haqida xabardor \n"
                     "bo'lishni istagan foydalanuvchilarga yordam berish uchun yaratilgan agent."),
        allow_code_execution=False,
        memory=True,
        reasoning=False,
        tracing=True,
        verbose=True,
        allow_delegation=False,
        cache=True ,
        max_execution_time=200, 
        max_retry_limit=3,  
        max_concurrent_executions=2,
        max_rpm=4,
        llm=LLM ,
        tools = [searching_tool])

def agronews_summarizer(LLM,searching_tool):
    return Agent(
        role = "Agro News Summarizer",
        goal = "O'zbekiston va Jahon bo'ylab qishloq xo'jaligi yangiliklarini qisqacha mazmunini taqdim etuvchi agent.",
        backstory = ("Yangiliklarni qisqacha va aniq mazmunini taqdim etishni istagan foydalanuvchilarga yordam berish uchun yaratilgan agent."),
        allow_code_execution=False,
        memory=True,
        reasoning=False,
        tracing=True,
        verbose=True,
        allow_delegation=False,
        cache=True ,
        max_execution_time=200, 
        max_retry_limit=3,  
        max_concurrent_executions=2,
        max_rpm=3,
        llm=LLM ,
        tools = [searching_tool])