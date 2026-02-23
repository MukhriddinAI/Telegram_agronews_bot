from datetime import datetime
from crewai import Task
from dotenv import load_dotenv
import os
load_dotenv(override=True)

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def news_scraper_task(searching_tool, agent, links):
    return Task(
        description=(f"""
            1. Quyidagi vebsaytlardan eng so'nggi agro yangiliklarni qidiring.
            2. Har bir manbadan FAQAT 1 ta eng muhim yangilikni tanlang.
            3. O'zbekiston yangiliklari: {links[0]}
            4. Jahon yangiliklari: {links[1]}
            
            MUHIM: 
            - Jami 10 ta yangilik (5 ta O'zbekiston + 5 ta Jahon)
            - Har bir yangilik uchun: sarlavha, qisqacha mazmun, manba havolasi
            - Faqat bugungi yoki kechagi yangiliklarni oling
            
            Manba:
            {links}
        """),
        expected_output="Jami 10 ta yangilik (sarlavha, mazmun, havola)",
        agent=agent,
        tools=[searching_tool]
    )

def validator_task(agent):
    return Task(
        description="""
            Oldingi taskdan kelgan yangiliklarni tekshiring:
            1. Fake yangiliklarni aniqlang va olib tashlang
            2. Takroriy yangiliklarni olib tashlang
            3. 7 kundan eski yangiliklarni olib tashlang
            4. Faqat ishonchli yangiliklarni qoldiring
            
            NATIJA: Tozalangan yangiliklarni qaytaring
        """,
        expected_output="Tekshirilgan va tozalangan yangililar ro'yxati",
        agent=agent,
    )

def analyser_task(agent):
    return Task(
        description="""
            Validatsiyadan o'tgan yangiliklardan:
            1. Eng muhim va qiziqarli 2 ta yangilikni tanlang
            2. O'zbekiston yoki Jahon yangiliklaridan eng dolzarbini tanlang
            3. Turli mavzularni qamrab oling

            TANLASH MEZONLARI:
            - Ahamiyatliligi (eng birinchi)
            - Dolzarbligi (bugungi sana)
            - O'quvchiga foydasi

            MUHIM: Faqat 2 ta yangilik tanlang - eng sara va eng muhim ikki yangilik
        """,
        expected_output="Eng muhim 2 ta yangilik",
        agent=agent
    )

def text_summerizer_task(agent):
    filename = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Task(
        description="""
            Tanlangan 2 ta yangilikni Telegram blog formatiga keltiring:

            1. Har bir yangilik uchun:
               - Jozibali sarlavha (50-70 belgi)
               - Qisqacha mazmun (100-150 so'z) - aniq, foydali va qiziqarli
               - Manba havolasi

            2. JSON FORMAT (QATTIY QOIDALAR):
            [
                {
                    "Sarlavha": "Jozibali sarlavha",
                    "Yangilik matni": "Qisqacha va aniq mazmun",
                    "Manba": "https://source-link.com"
                }
            ]

            3. TALABLAR:
            - JSON massiv bo'lishi SHART (faqat 2 ta element)
            - Markdown, izohlar, qo'shimcha belgilar YO'Q
            - Faqat to'g'ri JSON struktura
            - O'zbek tilida yozing
        """,
        expected_output="To'g'ri formatdagi JSON massiv (2 ta yangilik)",
        agent=agent,
        output_file=f"outputs/{filename}_agro_news.json"
    )