import os
import hmac
from dotenv import load_dotenv
load_dotenv()
import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from urllib.parse import parse_qsl

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

app = FastAPI(
    title="Xafsizyol API",
    description="Backend API for Xafsizyol pothole reporting project",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


reports_db: List[Report] = [
    Report(
        id="mock1",
        photo="https://picsum.photos/seed/pothole1/600/400",
        lat=41.3115,
        lng=69.2401,
        address="Amir Temur shoh ko'chasi, Tashkent",
        city="Tashkent",
        district="Yunusabad",
        severity=Severity.Critical,
        description="A deep pothole in the middle lane, very dangerous for tires.",
        createdAt=(datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
        status=Status.Pending,
        userId="test_user_123",
        phoneNumber="+998901234567",
        votes=12,
    ),
    Report(
        id="mock2",
        photo="https://picsum.photos/seed/pothole2/600/400",
        lat=41.2995,
        lng=69.2601,
        address="Shota Rustaveli ko'chasi, Tashkent",
        city="Tashkent",
        district="Yakkasaroy",
        severity=Severity.Medium,
        description="Several medium potholes near the bus stop.",
        createdAt=(datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
        status=Status.InProgress,
        userId="test_user_123",
        phoneNumber="+998901234567",
        votes=5,
    ),
    Report(
        id="mock3",
        photo="https://picsum.photos/seed/pothole3/600/400",
        lat=41.2850,
        lng=69.2250,
        address="Chilonzor ko'chasi, Tashkent",
        city="Tashkent",
        district="Chilonzor",
        severity=Severity.Small,
        description="Small cracks turning into a pothole.",
        createdAt=(datetime.utcnow() - timedelta(days=10)).isoformat() + "Z",
        status=Status.Fixed,
        userId="other_user",
        phoneNumber="+998998765432",
        votes=2,
    ),
]


# ─── Telegram helpers ───────────────────────────────────────────────────────

async def send_telegram_message(chat_id: str, text: str) -> bool:
    if not chat_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            return resp.status_code == 200
    except Exception as e:
        print(f"[Telegram] send error: {e}")
        return False


def validate_init_data(init_data: str) -> bool:
    """Validate Telegram Web App initData via HMAC-SHA256."""
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return False

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        computed = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, received_hash)
    except Exception:
        return False


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.get("/", summary="Health check")
def read_root():
    return {"status": "ok", "message": "Xafsizyol API v2"}


@app.get("/api/health")
def health():
    return {"status": "ok", "reports": len(reports_db)}


@app.post("/api/auth/validate", summary="Validate Telegram Web App initData")
def validate_telegram(body: ValidateRequest):
    if validate_init_data(body.initData):
        return {"valid": True}
    raise HTTPException(status_code=401, detail="Invalid Telegram initData")


@app.get("/api/reports", response_model=List[Report])
def get_all_reports():
    return sorted(reports_db, key=lambda r: r.createdAt, reverse=True)


@app.get("/api/reports/user/{user_id}", response_model=List[Report])
def get_user_reports(user_id: str):
    user_reports = [r for r in reports_db if r.userId == user_id]
    return sorted(user_reports, key=lambda r: r.createdAt, reverse=True)


@app.get("/api/reports/{report_id}", response_model=Report)
def get_report(report_id: str):
    for r in reports_db:
        if r.id == report_id:
            return r
    raise HTTPException(status_code=404, detail="Report not found")


@app.post("/api/reports", response_model=Report)
async def create_report(report_in: ReportCreate):
    new_report = Report(
        id=uuid.uuid4().hex[:8],
        createdAt=datetime.utcnow().isoformat() + "Z",
        status=Status.Pending,
        votes=0,
        **report_in.model_dump(),
    )
    reports_db.insert(0, new_report)

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

    # Notify the reporter
    if new_report.userId and new_report.userId.isdigit():
        await send_telegram_message(new_report.userId, msg)

    # Notify admin if configured
    if ADMIN_CHAT_ID:
        await send_telegram_message(ADMIN_CHAT_ID, msg)

    return new_report


@app.post("/api/reports/{report_id}/vote", response_model=Report)
def vote_report(report_id: str):
    for r in reports_db:
        if r.id == report_id:
            r.votes += 1
            return r
    raise HTTPException(status_code=404, detail="Report not found")


@app.patch("/api/reports/{report_id}/status", response_model=Report)
async def update_report_status(report_id: str, status: Status):
    for r in reports_db:
        if r.id == report_id:
            r.status = status
            # Notify user about status change
            status_labels = {
                Status.Pending: "⏳ Kutilmoqda",
                Status.InProgress: "🔧 Ko'rib chiqilmoqda",
                Status.Fixed: "✅ Bajarildi",
            }
            if r.userId and r.userId.isdigit():
                msg = (
                    f"<b>Xabaringiz holati yangilandi!</b>\n\n"
                    f"📍 {r.address}\n"
                    f"📌 Yangi holat: {status_labels.get(status, status.value)}"
                )
                await send_telegram_message(r.userId, msg)
            return r
    raise HTTPException(status_code=404, detail="Report not found")
