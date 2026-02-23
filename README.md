# 🌾 Agro News Bot — Telegram Yangiliklar Agenti

Kunlik agro yangiliklarni avtomatik yig'ib, eng sara **2 tasini** Telegram kanalingizga jo'natuvchi AI agent tizimi.

---

## 📋 Loyiha haqida

Bu loyiha **CrewAI** va **Google Gemini** yordamida O'zbekiston va jahon qishloq xo'jaligi yangiliklarini avtomatik ravishda yig'adi, tahlil qiladi va to'g'ridan-to'g'ri Telegram kanalingizga jo'natadi.

### ✅ Asosiy xususiyatlar

| Xususiyat | Tavsif |
|-----------|--------|
| 🔍 Yangilik yig'ish | 10 ta vebsaytdan (5 O'zbekiston + 5 Jahon) |
| 🧹 Filtrlash | Fake, takroriy va eski yangiliklarni olib tashlash |
| 🏆 Saralash | Eng muhim **2 ta** yangilikni tanlash |
| 📝 Formatlash | Telegram HTML formatida qisqacha mazmun |
| 📨 Jo'natish | Telegram Bot API orqali avtomatik yuborish |
| 🔄 Retry | Xato bo'lsa avtomatik qayta urinish (3 marta) |
| 💾 Saqlash | Natijalar JSON fayl sifatida `outputs/` ga saqlanadi |

---

## 🏗️ Arxitektura

Loyiha **4 ta AI agent** dan iborat (sequential pipeline):

```
[Scraper] → [Validator] → [Analyser] → [Summarizer] → [Telegram]
```

| Agent | Vazifa |
|-------|--------|
| **Agro News Scraper** | 10 ta vebsaytdan yangiliklarni DuckDuckGo orqali qidiradi |
| **News Validator** | Fake, takroriy va 7 kundan eski yangiliklarni o'chiradi |
| **News Analyser** | Eng muhim va dolzarb **2 ta** yangilikni tanlaydi |
| **Agro News Summarizer** | Telegram formatida JSON chiqaradi |

---

## 📁 Fayl tuzilishi

```
Telegram_agronews_bot/
├── agent.py            # 4 ta AI agent ta'rifi
├── task.py             # 4 ta task ta'rifi
├── sources.py          # O'zbekiston va Jahon yangilik URL'lari
├── main.py             # CrewAI crew va LLM sozlamalari
├── run.py              # Asosiy entry point (retry + Telegram)
├── telegram_sender.py  # Telegram Bot API integratsiyasi
├── check_quota.py      # Google API quota tekshiruvchi
├── requirements.txt    # Python kutubxonalari
├── .env.template       # Environment variables namunasi
├── .gitignore          # .env va boshqalar gitdan chiqarilgan
├── README.md           # Bu fayl
└── outputs/            # JSON natijalar (avtomatik yaratiladi)
```

---

## 🚀 O'rnatish va sozlash

### 1. Repozitoriyani klonlang

```bash
git clone https://github.com/MukhriddinAI/Telegram_agronews_bot.git
cd Telegram_agronews_bot
```

### 2. Virtual muhit va kutubxonalar

```bash
python -m venv newsagent_env
# Windows:
newsagent_env\Scripts\activate
# Linux/Mac:
source newsagent_env/bin/activate

pip install -r requirements.txt
```

### 3. `.env` fayl yarating

```bash
cp .env.template .env
```

`.env` faylini to'ldiring:

```env
GOOGLE_API_KEY=your_google_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_username
```

### 4. Ishga tushiring

```bash
# Windows (encoding muammosini oldini olish uchun):
PYTHONIOENCODING=utf-8 python run.py

# yoki oddiy:
python run.py
```

---

## 🔑 API Kalitlarni Olish

### Google Gemini API Key

1. [aistudio.google.com](https://aistudio.google.com) ga kiring
2. **"Get API key"** → **"Create API key in new project"**
3. Billing ulangan loyihadan kalit oling (to'lovli quota ko'proq)
4. Kalitni `.env` ga qo'ying: `GOOGLE_API_KEY=...`

> **Muhim:** `GOOGLE_API_KEY` Windows tizim environment variable sifatida o'rnatilgan bo'lsa, `.env` dagi qiymat ustunlik qiladi (`load_dotenv(override=True)` tufayli).

### Telegram Bot Token

1. Telegramda **@BotFather** ni oching
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `Agro Yangiliklar`)
4. Username kiriting (masalan: `agro_news_uz_bot`) — oxiri `bot` bilan tugashi shart
5. Olingan tokenni `.env` ga qo'ying: `TELEGRAM_BOT_TOKEN=...`

### Telegram Chat ID

**Public kanal uchun:**
```env
TELEGRAM_CHAT_ID=@kanal_username
```

**Private kanal uchun:**
1. Botni kanalga **Admin** qilib qo'shing
2. Brauzerda oching: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. `"chat": {"id": -1001234567890}` — shu raqamni oling
```env
TELEGRAM_CHAT_ID=-1001234567890
```

---

## 🔧 Konfiguratsiya

### Yangilik manbalari (`sources.py`)

```python
news_urls_uz = (
    "https://agro.gov.uz/",
    "https://agrokomakchi.uz/",
    "https://agroworld.uz/uz/yangiliklar/",
    "https://agro-olam.uz/category/yangiliklar/",
    "https://old.agroinspeksiya.uz/oz/news"
)

news_urls_world = (
    "https://agronews.com/eu/en/news",
    "https://www.farms.com/news",
    "https://www.brownfieldagnews.com/",
    "https://www.agriculture.com/news",
    "https://www.agri-pulse.com/news"
)
```

### LLM Modellari (`main.py`)

Prioritet tartibi (birinchisi ishlamasa keyingisiga o'tadi):

```python
models_to_try = [
    ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash"),
    ("gemini/gemini-2.5-flash-preview-04-17", "Gemini 2.5 Flash Preview"),
    ("gemini/gemini-2.0-flash-exp", "Gemini 2.0 Flash Experimental"),
]
```

### Agent sozlamalari (`agent.py`)

```python
max_iter=3              # Maksimal iteratsiya soni
max_execution_time=120  # Maksimal vaqt (soniyada)
max_retry_limit=2       # Qayta urinishlar soni
max_rpm=5               # Daqiqada maksimal so'rovlar
```

---

## 📊 Natija formati

### Telegram xabari (HTML):

```
📅 Kunlik Agro Yangiliklar
23.02.2026

Bugungi eng so'nggi 2 ta agro yangilik:

---

1. Qishloq xo'jaligida "Yashil iqtisodiyot": Yangi strategiyalar

O'zbekiston Qishloq xo'jaligi vazirligida resurs tejovchi
texnologiyalar va ekologik toza mahsulotlar yetishtirish
bo'yicha strategik rejalar muhokama qilindi...

🔗 Manbaga o'tish
```

### JSON fayl (`outputs/` papkasida):

```json
[
  {
    "Sarlavha": "Yangilik sarlavhasi",
    "Yangilik matni": "Qisqacha mazmun (100-150 so'z)",
    "Manba": "https://source-url.com"
  },
  {
    "Sarlavha": "Ikkinchi yangilik sarlavhasi",
    "Yangilik matni": "Qisqacha mazmun...",
    "Manba": "https://source-url.com"
  }
]
```

---

## ⏰ Kunlik avtomatlashtirish

### Windows Task Scheduler

1. `Win + R` → `taskschd.msc`
2. **"Create Basic Task"** → Har kuni soat 08:00
3. Action: `PYTHONIOENCODING=utf-8 python D:\path\to\run.py`

### Linux/Mac Cron

```bash
crontab -e
# Har kuni ertalab 08:00 da:
0 8 * * * cd /path/to/bot && PYTHONIOENCODING=utf-8 python run.py
```

---

## ⚠️ Muammolarni hal qilish

### 1. Quota Exceeded (429 xatosi)

**Sabab:** Kunlik bepul quota tugagan

**Yechim:**
- Ertaga kuting (quota Pacific Time yarim tunda yangilanadi — O'zbekiston: ~08:00-09:00)
- [aistudio.google.com](https://aistudio.google.com) da billing yoqing
- Yangi Google Cloud Project yaratib, yangi API kalit oling

### 2. API Key Invalid (400 xatosi)

**Sabab:** Kalit noto'g'ri yoki Gemini API yoqilmagan

**Yechim:**
- [aistudio.google.com](https://aistudio.google.com) dan to'g'ri kalit oling
- Kalit va loyihada Gemini API yoqilganligini tekshiring
- Windows tizimida eski kalit environment variable sifatida saqlangan bo'lishi mumkin — `.env` da yangi kalit yozing (`override=True` avtomatik qo'llanadi)

### 3. Model Not Found (404 xatosi)

**Sabab:** Eski model yangi foydalanuvchilar uchun o'chirilgan

**Yechim:** `main.py` da modellar ro'yxati yangilangan — `gemini-2.5-flash` ishlatiladi

### 4. Telegram xabar yuborilmadi

**Sabab:** Bot kanalga admin qilib qo'shilmagan yoki noto'g'ri CHAT_ID

**Yechim:**
```bash
# Botni tekshirish:
python -c "from telegram_sender import validate_bot_connection; validate_bot_connection()"
```
- Botni kanalga **Admin** qilib qo'shing
- `TELEGRAM_CHAT_ID` to'g'riligini tekshiring (`@username` yoki `-100...`)

### 5. JSON Parsing Error

**Sabab:** LLM natijasi to'g'ri JSON formatida emas

**Yechim:** `run.py` avtomatik qayta urinadi. Agar davom etsa, `task.py` dagi prompt ko'rsatmalarini tekshiring.

### 6. DuckDuckGo Search Error

```bash
pip install --upgrade duckduckgo-search
```

---

## 📈 API Quota monitoringi

```bash
python check_quota.py
```

Yoki brauzerda: [ai.dev/rate-limit](https://ai.dev/rate-limit)

---

## 🔍 Loyiha ishlash jarayoni

```
python run.py
     │
     ├── 🤖 Telegram bot ulanishi tekshiriladi
     │
     ├── 🔄 Attempt 1/3
     │    ├── LLM (gemini-2.5-flash) ishga tushiriladi
     │    ├── Agent 1 (Scraper): 10 ta saytdan yangilik qidiradi
     │    ├── Agent 2 (Validator): Fake/eski yangiliklarni olib tashlaydi
     │    ├── Agent 3 (Analyser): Eng sara 2 ta yangilikni tanlaydi
     │    └── Agent 4 (Summarizer): Telegram JSON formatini yaratadi
     │
     ├── 📊 JSON parse qilinadi
     ├── 💾 outputs/ ga saqlanadi
     └── 📨 Telegram kanaliga 2 ta xabar yuboriladi
```

---

## 📞 Foydali havolalar

- [Google AI Studio](https://aistudio.google.com) — API kalit olish
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [CrewAI Docs](https://docs.crewai.com)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 🤝 Hissa qo'shish

Pull request'lar xush kelibsiz!

1. Fork qiling
2. Feature branch yarating: `git checkout -b feature/yangi-xususiyat`
3. Commit qiling: `git commit -m 'Yangi xususiyat qo'shildi'`
4. Push qiling: `git push origin feature/yangi-xususiyat`
5. Pull Request oching

---

## ✨ Kelajakdagi rejalar

- [x] Telegram bot integratsiyasi ✅
- [x] Kunlik eng sara 2 ta yangilik tanlash ✅
- [x] Retry va quota boshqaruvi ✅
- [ ] Scheduling (Cron job / Task Scheduler)
- [ ] PostgreSQL — yuborilgan yangiliklarni saqlash (takrorlanmasin)
- [ ] Web dashboard
- [ ] Ko'proq yangilik manbalari
- [ ] Rasm bilan xabar yuborish

---

**Muallif:** MukhriddinAI
**Versiya:** 2.0.0
**Yangilangan:** 2026
