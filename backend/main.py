from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime, timedelta

app = FastAPI(
    title="Xafsizyol API",
    description="Full Backend API for Xafsizyol pothole reporting project",
    version="1.0.0"
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

# In-memory database with mock data mirroring frontend 'reports.ts'
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
        votes=12
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
        votes=5
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
        votes=2
    )
]

@app.get("/", summary="Root endpoint")
def read_root():
    return {"message": "Welcome to Xafsizyol Full API!"}

@app.get("/api/reports", response_model=List[Report], summary="Get all reports")
def get_all_reports():
    """
    Returns a list of all reports (potholes), ordered by newest first.
    """
    # Sort by createdAt descending
    return sorted(reports_db, key=lambda r: r.createdAt, reverse=True)

@app.get("/api/reports/user/{user_id}", response_model=List[Report], summary="Get reports by user ID")
def get_user_reports(user_id: str):
    """
    Returns a list of reports created by a specific user.
    """
    user_reports = [r for r in reports_db if r.userId == user_id]
    return sorted(user_reports, key=lambda r: r.createdAt, reverse=True)

@app.get("/api/reports/{report_id}", response_model=Report, summary="Get a specific report")
def get_report(report_id: str):
    """
    Returns the details of a specific report by ID.
    """
    for r in reports_db:
        if r.id == report_id:
            return r
    raise HTTPException(status_code=404, detail="Report not found")

@app.post("/api/reports", response_model=Report, summary="Create a new report")
def create_report(report_in: ReportCreate):
    """
    Submit a new pothole report.
    """
    new_report = Report(
        id=uuid.uuid4().hex[:8],
        createdAt=datetime.utcnow().isoformat() + "Z",
        status=Status.Pending,
        votes=0,
        **report_in.dict()
    )
    reports_db.insert(0, new_report)
    return new_report

@app.post("/api/reports/{report_id}/vote", response_model=Report, summary="Vote on a report")
def vote_report(report_id: str):
    """
    Increment the vote count for a specific report.
    """
    for r in reports_db:
        if r.id == report_id:
            r.votes += 1
            return r
    raise HTTPException(status_code=404, detail="Report not found")

@app.patch("/api/reports/{report_id}/status", response_model=Report, summary="Update report status (Admin)")
def update_report_status(report_id: str, status: Status):
    """
    Update the status of a report (e.g. from Pending to Fixed).
    """
    for r in reports_db:
        if r.id == report_id:
            r.status = status
            return r
    raise HTTPException(status_code=404, detail="Report not found")
