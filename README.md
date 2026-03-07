# 🌾 Agro News Bot — Telegram Yangiliklar Agenti

Kunlik agro yangiliklarni avtomatik yig'ib, eng sara **2 tasini** Telegram kanalingizga jo'natuvchi AI agent tizimi.

---

## Qanday ishlaydi

```
[Scraper] → [Validator + Analyser] → [Summarizer] → [Telegram]
```

| Agent | Vazifa |
|-------|--------|
| **Scraper** | 10 ta saytdan (5 O'zbekiston + 5 Jahon) DuckDuckGo orqali yangilik qidiradi |
| **Validator** +  **Analyser** | Eng muhim **2 ta** yangilikni tanlaydi va fake, takroriy va 7 kundan eski yangiliklarni olib tashlaydi |
| **Summarizer** | Telegram HTML formatida JSON chiqaradi |

---

## Fayl tuzilishi

```
├── run.py              # Asosiy entry point
├── main.py             # CrewAI crew va LLM sozlamalari
├── agent.py            # 4 ta AI agent
├── task.py             # 4 ta task
├── sources.py          # Yangilik URL manbalari
├── config.py           # Umumiy konstantalar
├── telegram_sender.py  # Telegram Bot API
├── translator.py       # Matnni istalgan tilga tarjima qiluvchi
├── check_quota.py      # Google API quota tekshiruvchi
├── .env                # API kalitlar (gitga kirmaydi)
└── outputs/            # JSON natijalar (avtomatik yaratiladi)
```

---

## O'rnatish

### 1. Repozitoriyani klonlang

```bash
git clone https://github.com/IfodaAI/Agro_Newagent_AI.git
cd Agro_Newagent_AI
```

### 2. Kutubxonalar

```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
```

### 3. `.env` fayl

```env
GOOGLE_API_KEY=your_google_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_username
```

### 4. Ishga tushiring

```bash
python run.py
```

---

## API Kalitlar

### Google Gemini
1. [aistudio.google.com](https://aistudio.google.com) → **Get API key**
2. Kalitni `.env` ga qo'ying: `GOOGLE_API_KEY=...`

### Telegram Bot
1. **@BotFather** → `/newbot` → token oling
2. Botni kanalga **Admin** qilib qo'shing
3. `.env` ga qo'ying: `TELEGRAM_BOT_TOKEN=...`

**Chat ID (private kanal):**
```
https://api.telegram.org/bot<TOKEN>/getUpdates
→ "chat": {"id": -1001234567890}
```

---

## Muammolarni hal qilish

| Xato | Sabab | Yechim |
|------|-------|--------|
| `429 Quota Exceeded` | Kunlik limit tugagan | Ertaga kuting yoki billing yoqing |
| `400 API Key Invalid` | Kalit noto'g'ri | [aistudio.google.com](https://aistudio.google.com) dan yangi kalit oling |
| Telegram yuborilmadi | Bot admin emas | Botni kanalga admin qilib qo'shing |
| JSON parse xatosi | LLM noto'g'ri format | `run.py` avtomatik qayta urinadi |

```bash
# Quota tekshirish:
python check_quota.py

# Telegram bot tekshirish:
python -c "from telegram_sender import validate_bot_connection; validate_bot_connection()"
```

---

## Avtomatlashtirish

**Windows Task Scheduler** — har kuni soat 08:00:
```
Action: python D:\path\to\run.py
```

**Linux/Mac Cron:**
```bash
0 8 * * * cd /path/to/bot && python run.py
```

---

**Muallif:** MukhriddinAI · **Stack:** CrewAI + Gemini + Telegram Bot API
