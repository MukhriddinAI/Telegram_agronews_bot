from crewai import Task


def filter_and_analyse_task(agent, scraped_articles: list[dict]):
    """Filter and select the 2 best articles (1 Uzbek + 1 World) from pre-scraped data."""
    formatted = []
    for i, a in enumerate(scraped_articles, 1):
        formatted.append(
            f"[{i}] Sarlavha: {a['sarlavha']}\n"
            f"    Guruh: {a['guruh']}\n"
            f"    Mazmun: {a['mazmun']}\n"
            f"    URL: {a['url']}"
        )
    articles_text = "\n\n".join(formatted)

    return Task(
        description=f"""
            Quyidagi scraped yangiliklar ro'yxatini tahlil qiling va ANIQ 2 ta tanlang:

            {articles_text}

            QOIDA (MAJBURIY):
            - 1-yangilik: "guruh": "uzbekiston" bo'lganlardan ENG MUHIMI
            - 2-yangilik: "guruh": "jahon" bo'lganlardan ENG MUHIMI
            - Har bir guruhdan FAQAT 1 ta tanlang

            FILTRLASH:
            - Fake, takroriy va eski yangiliklarni olib tashlang
            - Ahamiyatliligi va dolzarbligi asosida tanlang

            URL BO'YICHA QOIDA (ENG MUHIM):
            - "url" maydoniga ro'yxatdagi HAQIQIY URL ni AYNAN KO'CHIRING
            - URL ni o'zgartirmang, taxmin qilmang, to'qimang

            NATIJA FORMATI - FAQAT JSON:
            [
              {{"sarlavha": "...", "mazmun": "...", "url": "https://..."}}
            ]
        """,
        expected_output="JSON massiv: 2 ta yangilik — 1 ta O'zbekiston + 1 ta Jahon (sarlavha, mazmun, url)",
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
                    "Manba": "oldingi agentdan kelgan haqiqiy URL"
                }
            ]

            3. URL BO'YICHA QOIDA (ENG MUHIM):
            - "Manba" = oldingi agentdan kelgan "url" maydonidagi HAQIQIY URL ni AYNAN KO'CHIRING
            - URL to'qimang, o'zgartirmang — faqat berilgan URL ni ko'chiring

            4. BOSHQA TALABLAR:
            - JSON massiv bo'lishi SHART (faqat 2 ta element)
            - Markdown, izohlar, qo'shimcha belgilar YO'Q
            - Faqat to'g'ri JSON struktura
        """,
        expected_output="To'g'ri formatdagi JSON massiv (2 ta yangilik, haqiqiy URL bilan)",
        agent=agent,
    )
