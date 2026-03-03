from crewai import Task
from datetime import datetime


def news_scraper_task(searching_tool, agent, sources):
    year = datetime.now().year
    return Task(
        description=(f"""
            MAQSAD: Qishloq xo'jaligi bo'yicha eng so'nggi 10 ta haqiqiy yangilik topish.

            QIDIRUV SO'ROVLARI (KETMA-KET BAJARING):
            1. "Uzbekistan agriculture news today {year}"
            2. "agricultural news today farms crops {year}"
            3. "qishloq xo'jaligi yangiliklar {year}"
            4. "world agriculture food news latest"
            5. "agronews farming latest {year}"

            ISHONCHLI MANBALAR (natijalarni shu saytlardan afzal ko'ring):
            - Jahon: {sources['world']}
            - O'zbekiston: {sources['uz']}

            QOIDALAR:
            - Har bir so'rovdan 2-3 ta yangilik oling
            - Jami hech bo'lmasa 5 ta (imkon bo'lsa 10 ta) haqiqiy yangilik yig'ing
            - "Yangilik topilmadi" deb YOZMANG — boshqa so'rov bilan qidirishni davom ettiring

            CHIQARISH FORMATI - QATTIY JSON MASSIV:
            [
              {{
                "sarlavha": "Yangilik sarlavhasi",
                "mazmun": "100-150 so'z mazmun",
                "url": "DuckDuckGo natijasidagi Link: qiymatidan olingan HAQIQIY URL"
              }}
            ]

            URL BO'YICHA QOIDA (ENG MUHIM):
            - "url" maydoniga FAQAT DuckDuckGo qidiruv natijasidagi "Link:" ni yozing
            - URL ni o'zgartirmang, taxmin qilmang, to'ldirmang
            - Agar maqola havolasi topilmasa, manba domenini yozing (masalan: https://agronews.com)
        """),
        expected_output="JSON massiv: kamida 5 ta yangilik (sarlavha, mazmun, url)",
        agent=agent,
        tools=[searching_tool],
    )


def validator_task(agent):
    return Task(
        description="""
            Oldingi taskdan kelgan yangiliklarni tekshiring:
            1. Fake yangiliklarni aniqlang va olib tashlang
            2. Takroriy yangiliklarni olib tashlang
            3. 7 kundan eski yangiliklarni olib tashlang
            4. Faqat ishonchli yangiliklarni qoldiring

            MUHIM: Har bir yangilikdagi "url" maydonini O'ZGARTIRMANG!
            URL ni aynan scraper bergan ko'rinishda saqlang.

            NATIJA: Tozalangan yangiliklarni JSON formatda qaytaring (sarlavha, mazmun, url)
        """,
        expected_output="JSON massiv: tekshirilgan yangililar (sarlavha, mazmun, url)",
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

            MUHIM (QOIDA):
            -  Har bir yangilikdagi "url" maydonini O'ZGARTIRMANG!
            URL ni aynan scraper bergan ko'rinishda saqlang.
            - Faqat 2 ta yangilik tanlang - eng sara va eng muhim ikki yangilik
            - JSON formatda qaytaring (sarlavha, mazmun, url)
        """,
        expected_output="JSON massiv: 2 ta yangilik (sarlavha, mazmun, url)",
        agent=agent,
    )


def text_summarizer_task(agent):
    return Task(
        description="""
            Tanlangan 2 ta yangilikni Telegram blog formatiga keltiring.

            1. Har bir yangilik uchun:
               - Jozibali sarlavha (50-70 belgi) - o'zbek tilida
               - Qisqacha mazmun (100-150 so'z) - aniq, foydali va qiziqarli, o'zbek tilida
               - Manba havolasi

            2. CHIQARISH FORMATI - FAQAT JSON (hech qanday qo'shimcha matn yo'q):
            [
                {
                    "Sarlavha": "Jozibali sarlavha",
                    "Yangilik matni": "Qisqacha va aniq mazmun",
                    "Manba": "oldingi agentdan kelgan url qiymati"
                }
            ]

            3. URL BO'YICHA QOIDA (ENG MUHIM - BU QOIDANI BUZISH MUMKIN EMAS):
            - "Manba" = oldingi agentdan kelgan "url" maydonini AYNAN KO'CHIRING
            - URL ni O'ZGARTIRMANG, QISQARTIRMANG, TO'QIMANG
            - Yangi URL to'qimang - hatto manba nomi o'xshash bo'lsa ham
            - Agar url bo'sh yoki yo'q bo'lsa, FAQAT manba domenini yozing

            4. BOSHQA TALABLAR:
            - JSON massiv bo'lishi SHART (faqat 2 ta element)
            - Markdown, izohlar, qo'shimcha belgilar YO'Q
            - Faqat to'g'ri JSON struktura
        """,
        expected_output="To'g'ri formatdagi JSON massiv (2 ta yangilik, haqiqiy URL bilan)",
        agent=agent,
    )
