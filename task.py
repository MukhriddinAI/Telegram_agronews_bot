from datetime import datetime
from crewai import Task
from crewai_tools import FileWriterTool

filter_tool = FileWriterTool()

def news_scraper_task(searching_tool,agent,links):
    return Task(description = ( f"""
            1. Agro sohasidagi eng so'nggi yangiliklarni aniqlang.
            2. Eng muhim yangiliklarni tanlang.
            3. 1 ta Jahon  agro yangiliklarini qaytar.{links[1]}
            4. 1 ta O'zbekiston agro yangiliklarini qaytar.{links[0]}
            Manba:
            {links}"""),
            expected_output="Successfully scraped news articles in JSON format",
            agent=agent,
            multimodal=True,
            tools=[searching_tool, filter_tool]
            )


def text_summerizer_task(searching_tool,agent,links):
    return Task(description = ( f"""
            1. Yangiliklarni tahlil qil.
            2. Telegram blog uchun mos so'z limiti.
            3. Yangilikni qisqacha mazmunini yoz.
            4. FORMAT :
            [{{
                "Sarlavha" : "..." , 
                "Yangilik matni" : "..." ,
                "Manba" : "source_link" }}]
            5. FORMATNI BUZMA.
            6. FAOL MATN, IZOHLAR, BELGILAR YO‘Q.
            7. JSON massiv bo‘lsin.
    """
    ),
        expected_output="Valid JSON output for a Telegram Channel post",
        agent=agent,
        output_file=f"{datetime.now().isoformat()}_data.json",
        multimodal=True,
        tools=[searching_tool, filter_tool])