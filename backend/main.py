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
BACKEND_URL = os.getenv("BACKEND_URL", "")
WEB_APP_URL = os.getenv("WEB_APP_URL", "")
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
