import os
import hmac
import hashlib
import uuid
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from urllib.parse import parse_qsl

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL") or os.getenv("NUXT_PUBLIC_API_BASE", "")
WEB_APP_URL = os.getenv("WEB_APP_URL", "")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")

SYSTEM_PROMPT = """You are the official AI assistant of the Xafsizyol app. Always reply in the same language the user writes in: Uzbek, Russian, or English. Be friendly, concise, and helpful.

━━━ ABOUT THE PROJECT ━━━
Xafsizyol ("Safe Road" in Uzbek) is a civic platform for reporting road potholes and hazards across Uzbekistan.
How it works: citizens report a problem → authorities review it → problem gets fixed.
Platform: Telegram Mini App (runs inside Telegram, no browser needed).
Website: also accessible via web browser.
Region: Uzbekistan, primarily Tashkent and all provinces (viloyatlar).
Languages: Uzbek, Russian, English.
Free to use for all citizens.

━━━ REAL ROAD SITUATION IN UZBEKISTAN ━━━
Road infrastructure in Uzbekistan has significant challenges:
• Tashkent: High-traffic roads like Amir Temur shoh ko'chasi, Chilonzor ko'chalari, Yunusabad, Mirzo Ulug'bek districts frequently have potholes
• Seasonal damage: Spring thaw causes major road cracking; summer heat expands cracks further
• Common pothole causes: heavy truck traffic, poor drainage, old asphalt, freeze-thaw cycles
• Government responsible: Toshkent shahar yo'l xo'jaligi boshqarmasi (Tashkent City Road Management) and regional hokimiyat
• Reporting helps: collected data allows authorities to prioritize repairs by severity and frequency of complaints
• Real impact: vehicle damage from potholes costs Uzbek drivers millions of soums annually (tire damage, suspension, rims)

━━━ KEY FEATURES ━━━
• Report a problem: take a photo, pin location on map, choose severity
• Interactive map: all reports visible on map with filters
• Voting: users can vote on important problems to raise their priority
• Status tracking: each report has a lifecycle status
• My reports: view all your submitted reports in one place
• Admin panel: authorities can manage and update report statuses

━━━ HOW TO REPORT (step by step) ━━━
1. Press "Muammoni xabar qilish" button in the bot
2. Inside the Mini App, press the "+" button
3. Take a photo or choose from gallery (required)
4. Confirm your location on the map (GPS auto-detects, you can adjust)
5. Choose severity: Small / Medium / Critical
6. Write a short description (optional but helpful)
7. Enter your phone number (optional — for authorities to contact you)
8. Press "Yuborish" — report appears on the map instantly

━━━ SEVERITY LEVELS ━━━
• Small (Kichik / Небольшая) — minor crack or small pothole, driveable with care
• Medium (O'rta / Средняя) — noticeable pothole, caution needed, can damage tires
• Critical (Kritik / Критичная) — dangerous, deep or wide pothole, urgent repair needed, risk of accidents

━━━ REPORT STATUSES ━━━
• Pending (Kutilmoqda / Ожидает) — new report, not yet reviewed by authorities
• In Progress (Ko'rib chiqilmoqda / На проверке) — authorities have started working on it
• Fixed (Bajarildi / Исправлено) — problem has been resolved and road is repaired

━━━ MAP FILTERS ━━━
• All (Hammasi / Все) — show all reports
• Critical (Xavfli / Критичные) — only Critical severity reports
• Recent (Yaqinda / Недавние) — latest submitted reports
• Fixed (Tuzatilgan / Исправленные) — resolved problems

━━━ API & TECHNICAL INFO ━━━
The Xafsizyol backend API (v3) provides:
- GET /api/reports — get all reports
- GET /api/reports/{id} — get a specific report by ID
- GET /api/reports/user/{userId} — get reports by a specific user
- POST /api/reports — create a new report (requires: lat, lng, address, severity, description; optional: photo, city, district, userId, phoneNumber)
- POST /api/reports/{id}/vote — add a vote to a report
- PATCH /api/reports/{id}/status — update report status (Pending → In Progress → Fixed)
- POST /api/auth/validate — validate Telegram initData
- GET /api/health — API health check

━━━ FREQUENTLY ASKED QUESTIONS ━━━

Q (UZ): Bu ilova nima?
A: Xafsizyol — yo'llardagi chuqurlar haqida xabar berish ilovasi. Telegram orqali ishlaydi. Rasm olib, xaritada joylashuvni belgilab, muammo haqida xabar qilasiz — bepul va oson.

Q (RU): Что такое Xafsizyol?
A: Xafsizyol — приложение для сообщений о дорожных ямах. Работает через Telegram Mini App. Сфотографируй яму, отметь на карте — и отчёт сразу виден властям.

Q (EN): What is Xafsizyol?
A: Xafsizyol is a road pothole reporting app for Uzbekistan. It works as a Telegram Mini App. Take a photo, pin the location on the map, and your report is instantly visible to road authorities.

Q: Qanday ishlataman / Как пользоваться / How to use?
A (UZ): "Muammoni xabar qilish" → "+" tugmasi → rasm → joylashuv → jiddiylik → Yuborish.
A (RU): Нажмите "Muammoni xabar qilish" → "+" → фото → местоположение → серьёзность → Отправить.
A (EN): Tap "Report a problem" → "+" button → photo → location → severity → Submit.

Q: Xabarim qachon ko'riladi / Когда рассмотрят / When will my report be reviewed?
A: After submission it gets "Pending" status. Authorities change it to "In Progress" when they start, and "Fixed" when repaired. You'll get a Telegram notification on each status change.

Q: Ovoz berish nima uchun / Зачем голосовать / Why vote?
A: Votes show how many people are affected by the same problem. More votes = higher priority for authorities. If you see a pothole that also bothers you, vote for it!

Q: Rasm majburiyми / Фото обязательно / Is photo required?
A (UZ): Ha, rasm majburiy — muammoni tasdiqlash uchun kerak.
A (RU): Да, фото обязательно для подтверждения проблемы.
A (EN): Yes, a photo is required to verify the reported issue.

Q: Telefon raqam nima uchun / Зачем номер / Why phone number?
A: Optional. Authorities may contact you for more details if needed.

Q: Xaritada ko'rinmayapti / Не отображается на карте / Not showing on map?
A: Refresh the page. If still not visible, make sure GPS location was accurately pinned when submitting.

Q: Bepulmi / Бесплатно ли / Is it free?
A: Yes, completely free for all citizens.

━━━ RULES FOR RESPONSES ━━━
- ALWAYS reply in the same language the user used (Uzbek → Uzbek, Russian → Russian, English → English)
- For completely unrelated topics (sports, music, politics, cooking, etc.): reply "Men faqat Xafsizyol ilovasi bo'yicha yordam bera olaman" / "Я могу помочь только по вопросам приложения Xafsizyol" / "I can only help with Xafsizyol app questions"
- Keep answers short and clear
- Use bullet points for multi-step instructions"""
DB_PATH = os.path.join(os.path.dirname(__file__), "reports.db")

app = FastAPI(title="Xafsizyol API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic models ────────────────────────────────────────────────────────

class Severity(str, Enum):
    Small = "Small"
    Medium = "Medium"
    Critical = "Critical"

class Status(str, Enum):
    Pending = "Pending"
    InProgress = "In Progress"
    Fixed = "Fixed"

class ReportCreate(BaseModel):
    photo: Optional[str] = None
    lat: float
    lng: float
    address: str
    city: Optional[str] = None
    district: Optional[str] = None
    severity: Severity
    description: str
    userId: Optional[str] = None
    phoneNumber: Optional[str] = None

class Report(ReportCreate):
    id: str
    createdAt: str
    status: Status
    votes: int

class ValidateRequest(BaseModel):
    initData: str


# ─── SQLite helpers ──────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id          TEXT PRIMARY KEY,
                photo       TEXT,
                lat         REAL NOT NULL,
                lng         REAL NOT NULL,
                address     TEXT NOT NULL,
                city        TEXT,
                district    TEXT,
                severity    TEXT NOT NULL,
                description TEXT NOT NULL,
                userId      TEXT,
                phoneNumber TEXT,
                createdAt   TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'Pending',
                votes       INTEGER NOT NULL DEFAULT 0
            )
        """)
        # Seed mock data only once
        if conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 0:
            now = datetime.utcnow()
            seed = [
                ("mock1", "https://picsum.photos/seed/pothole1/600/400", 41.3115, 69.2401,
                 "Amir Temur shoh ko'chasi, Tashkent", "Tashkent", "Yunusabad",
                 "Critical", "A deep pothole in the middle lane, very dangerous for tires.",
                 "test_user_123", "+998901234567",
                 (now - timedelta(days=2)).isoformat() + "Z", "Pending", 12),
                ("mock2", "https://picsum.photos/seed/pothole2/600/400", 41.2995, 69.2601,
                 "Shota Rustaveli ko'chasi, Tashkent", "Tashkent", "Yakkasaroy",
                 "Medium", "Several medium potholes near the bus stop.",
                 "test_user_123", "+998901234567",
                 (now - timedelta(days=5)).isoformat() + "Z", "In Progress", 5),
                ("mock3", "https://picsum.photos/seed/pothole3/600/400", 41.2850, 69.2250,
                 "Chilonzor ko'chasi, Tashkent", "Tashkent", "Chilonzor",
                 "Small", "Small cracks turning into a pothole.",
                 "other_user", "+998998765432",
                 (now - timedelta(days=10)).isoformat() + "Z", "Fixed", 2),
            ]
            conn.executemany(
                "INSERT INTO reports VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", seed
            )
    print(f"[DB] SQLite ready: {DB_PATH}")


def row_to_report(row) -> Report:
    return Report(
        id=row["id"], photo=row["photo"], lat=row["lat"], lng=row["lng"],
        address=row["address"], city=row["city"], district=row["district"],
        severity=row["severity"], description=row["description"],
        userId=row["userId"], phoneNumber=row["phoneNumber"],
        createdAt=row["createdAt"], status=row["status"], votes=row["votes"],
    )


# ─── Startup ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ─── Telegram helpers ────────────────────────────────────────────────────────

async def send_telegram_message(chat_id: str, text: str, reply_markup: dict | None = None) -> bool:
    if not chat_id or not TELEGRAM_BOT_TOKEN:
        return False
    try:
        payload: dict = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            return r.status_code == 200
    except Exception as e:
        print(f"[Telegram] error: {e}")
        return False


def validate_init_data(init_data: str) -> bool:
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return False
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, received_hash)
    except Exception:
        return False


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Xafsizyol API v3 (SQLite)"}


@app.get("/api/health")
def health():
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    return {"status": "ok", "reports": count}


@app.post("/api/auth/validate")
def validate_telegram(body: ValidateRequest):
    if validate_init_data(body.initData):
        return {"valid": True}
    raise HTTPException(status_code=401, detail="Invalid Telegram initData")


@app.get("/api/reports", response_model=List[Report])
def get_all_reports():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY createdAt DESC"
        ).fetchall()
    return [row_to_report(r) for r in rows]


@app.get("/api/reports/user/{user_id}", response_model=List[Report])
def get_user_reports(user_id: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE userId=? ORDER BY createdAt DESC", (user_id,)
        ).fetchall()
    return [row_to_report(r) for r in rows]


@app.get("/api/reports/{report_id}", response_model=Report)
def get_report(report_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    return row_to_report(row)


@app.post("/api/reports", response_model=Report)
async def create_report(report_in: ReportCreate):
    new_id = uuid.uuid4().hex[:8]
    created_at = datetime.utcnow().isoformat() + "Z"

    with get_db() as conn:
        conn.execute(
            """INSERT INTO reports
               (id,photo,lat,lng,address,city,district,severity,description,
                userId,phoneNumber,createdAt,status,votes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (new_id, report_in.photo, report_in.lat, report_in.lng,
             report_in.address, report_in.city, report_in.district,
             report_in.severity.value, report_in.description,
             report_in.userId, report_in.phoneNumber,
             created_at, "Pending", 0),
        )
        row = conn.execute("SELECT * FROM reports WHERE id=?", (new_id,)).fetchone()

    new_report = row_to_report(row)

    severity_emoji = {"Small": "🟡", "Medium": "🟠", "Critical": "🔴"}.get(
        new_report.severity.value, "⚪"
    )
    msg = (
        f"<b>Yangi muammo xabari!</b>\n\n"
        f"{severity_emoji} <b>Daraja:</b> {new_report.severity.value}\n"
        f"📍 <b>Manzil:</b> {new_report.address}\n"
        f"📝 <b>Tavsif:</b> {new_report.description}\n"
        f"🆔 <b>ID:</b> {new_report.id}"
    )

    if new_report.userId and new_report.userId.isdigit():
        await send_telegram_message(new_report.userId, msg)
    if ADMIN_CHAT_ID:
        await send_telegram_message(ADMIN_CHAT_ID, msg)

    return new_report


@app.post("/api/reports/{report_id}/vote", response_model=Report)
def vote_report(report_id: str):
    with get_db() as conn:
        updated = conn.execute(
            "UPDATE reports SET votes = votes + 1 WHERE id=?", (report_id,)
        ).rowcount
        if updated == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    return row_to_report(row)


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "uz"

@app.post("/api/chat")
async def web_chat(body: ChatRequest):
    reply = await ask_ollama(body.message)
    return {"reply": reply}


async def ask_ollama(user_message: str) -> str:
    if not OLLAMA_API_KEY:
        return "⚠️ AI yordamchi hozir mavjud emas."
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://ollama.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
                json={
                    "model": "gemma3:4b",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                },
            )
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Ollama] error: {e}")
        return "⚠️ Kechirasiz, xatolik yuz berdi. Qayta urinib ko'ring."


@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"ok": True}

    message = data.get("message", {})
    if not message:
        return {"ok": True}

    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "")
    first_name = message.get("from", {}).get("first_name", "Foydalanuvchi")

    if text == "/start":
        greeting = (
            f"Assalomu alaykum, <b>{first_name}</b>! 👋\n\n"
            f"<b>Xafsizyol</b> botiga xush kelibsiz! 🚗\n\n"
            f"Bu bot orqali yo'llardagi chuqurlar va muammolarni xabar qilishingiz mumkin.\n\n"
            f"❓ Savol bo'lsa — yozing, men yordam beraman!\n\n"
            f"Boshlash uchun quyidagi tugmani bosing 👇"
        )
        markup = None
        if WEB_APP_URL:
            markup = {
                "inline_keyboard": [[
                    {"text": "🗺 Muammoni xabar qilish", "web_app": {"url": WEB_APP_URL}}
                ]]
            }
        await send_telegram_message(chat_id, greeting, markup)

    elif text and not text.startswith("/"):
        # AI response via Ollama
        reply = await ask_ollama(text)
        await send_telegram_message(chat_id, reply)

    return {"ok": True}


@app.get("/api/setup-webhook")
async def setup_webhook():
    if not BACKEND_URL:
        raise HTTPException(status_code=400, detail="BACKEND_URL not set in environment")
    webhook_url = f"{BACKEND_URL}/webhook"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{TELEGRAM_API}/setWebhook",
            json={"url": webhook_url, "drop_pending_updates": True},
        )
    result = r.json()
    print(f"[Webhook] setWebhook → {result}")
    return result


@app.patch("/api/reports/{report_id}/status", response_model=Report)
async def update_report_status(report_id: str, status: Status):
    with get_db() as conn:
        updated = conn.execute(
            "UPDATE reports SET status=? WHERE id=?", (status.value, report_id)
        ).rowcount
        if updated == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()

    report = row_to_report(row)
    status_labels = {
        "Pending": "⏳ Kutilmoqda",
        "In Progress": "🔧 Ko'rib chiqilmoqda",
        "Fixed": "✅ Bajarildi",
    }
    if report.userId and report.userId.isdigit():
        msg = (
            f"<b>Xabaringiz holati yangilandi!</b>\n\n"
            f"📍 {report.address}\n"
            f"📌 Yangi holat: {status_labels.get(status.value, status.value)}"
        )
        await send_telegram_message(report.userId, msg)

    return report
