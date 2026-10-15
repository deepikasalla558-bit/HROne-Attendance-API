
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = FastAPI(title="HROne Employee Attendance API")

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client["hrone_attendance"]

employees = db["employees"]
attendance = db["attendance"]
audit_logs = db["audit_logs"]

employees.create_index("employee_id", unique=True)
attendance.create_index(
    [("employee_id", 1), ("date", 1)],
    unique=True
)


def current_time():
    return datetime.now(timezone.utc)


class Employee(BaseModel):
    employee_id: str
    name: str
    department: str = "General"


class PunchRequest(BaseModel):
    employee_id: str


class CorrectionRequest(BaseModel):
    employee_id: str
    date: str
    punch_in: datetime | None = None
    punch_out: datetime | None = None
    reason: str
    corrected_by: str


@app.get("/")
def home():
    return {"message": "Employee Attendance API is running"}


@app.post("/employees")
def create_employee(request: Employee):
    try:
        employees.insert_one(request.model_dump())
    except DuplicateKeyError:
        raise HTTPException(409, "Employee already exists")

    return {"message": "Employee created successfully"}


@app.get("/employees")
def list_employees():
    return [
        {key: value for key, value in item.items() if key != "_id"}
        for item in employees.find()
    ]


@app.post("/attendance/punch-in")
def punch_in(request: PunchRequest):
    if not employees.find_one({"employee_id": request.employee_id}):
        raise HTTPException(404, "Employee not found")

    now = current_time()
    date = now.date().isoformat()

    existing = attendance.find_one({
        "employee_id": request.employee_id,
        "date": date
    })

    if existing:
        raise HTTPException(400, "Attendance already exists for today")

    attendance.insert_one({
        "employee_id": request.employee_id,
        "date": date,
        "punch_in": now,
        "punch_out": None,
        "working_hours": None
    })

    return {"message": "Punch-in successful", "time": now.isoformat()}


@app.post("/attendance/punch-out")
def punch_out(request: PunchRequest):
    now = current_time()
    date = now.date().isoformat()

    record = attendance.find_one({
        "employee_id": request.employee_id,
        "date": date
    })

    if not record or not record.get("punch_in"):
        raise HTTPException(400, "Please punch in first")

    if record.get("punch_out"):
        raise HTTPException(400, "Already punched out")

    punch_in_time = record["punch_in"]
    if punch_in_time.tzinfo is None:
        punch_in_time = punch_in_time.replace(tzinfo=timezone.utc)

    hours = round((now - punch_in_time).total_seconds() / 3600, 2)

    attendance.update_one(
        {"_id": record["_id"]},
        {"$set": {"punch_out": now, "working_hours": hours}}
    )

    return {"message": "Punch-out successful", "working_hours": hours}


@app.get("/attendance/{employee_id}")
def get_attendance(employee_id: str):
    if not employees.find_one({"employee_id": employee_id}):
        raise HTTPException(404, "Employee not found")

    records = attendance.find({"employee_id": employee_id})

    return [
        {key: value for key, value in item.items() if key != "_id"}
        for item in records
    ]


@app.post("/attendance/correction")
def correct_attendance(request: CorrectionRequest):
    record = attendance.find_one({
        "employee_id": request.employee_id,
        "date": request.date
    })

    if not record:
        raise HTTPException(404, "Attendance record not found")

    changes = {}
    if request.punch_in is not None:
        changes["punch_in"] = request.punch_in
    if request.punch_out is not None:
        changes["punch_out"] = request.punch_out

    if not changes:
        raise HTTPException(400, "Provide a punch-in or punch-out correction")

    old_values = {key: record.get(key) for key in changes}
    new_in = changes.get("punch_in", record.get("punch_in"))
    new_out = changes.get("punch_out", record.get("punch_out"))

    if new_in and new_out and new_out <= new_in:
        raise HTTPException(400, "Punch-out must be after punch-in")

    if new_in and new_out:
        changes["working_hours"] = round(
            (new_out - new_in).total_seconds() / 3600, 2
        )

    attendance.update_one(
        {"_id": record["_id"]},
        {"$set": changes}
    )

    audit_logs.insert_one({
        "employee_id": request.employee_id,
        "date": request.date,
        "old_values": old_values,
        "new_values": changes,
        "reason": request.reason,
        "corrected_by": request.corrected_by,
        "corrected_at": current_time()
    })

    return {"message": "Correction saved with audit history"}


@app.get("/analytics/daily")
def daily_analytics(date: str):
    pipeline = [
        {"$match": {"date": date}},
        {"$group": {
            "_id": "$date",
            "employees_present": {"$sum": 1},
            "total_working_hours": {
                "$sum": {"$ifNull": ["$working_hours", 0]}
            }
        }}
    ]

    return list(attendance.aggregate(pipeline))


@app.get("/analytics/employee-hours")
def employee_hours():
    pipeline = [
        {"$group": {
            "_id": "$employee_id",
            "total_working_hours": {
                "$sum": {"$ifNull": ["$working_hours", 0]}
            }
        }}
    ]

    return list(attendance.aggregate(pipeline))


@app.get("/attendance-audit/{employee_id}")
def get_audit_history(employee_id: str):
    logs = audit_logs.find({"employee_id": employee_id})

    return [
        {key: value for key, value in item.items() if key != "_id"}
        for item in logs
    ]
