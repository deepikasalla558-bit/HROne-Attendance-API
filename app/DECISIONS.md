
# Design Decisions

## 1. Framework
FastAPI is used to create REST API endpoints because it
supports request validation and automatic API documentation.

## 2. Database
MongoDB is used to store employee information, attendance
records, and attendance correction history.

## 3. Employee Management
Each employee has a unique employee ID to identify records.

## 4. Attendance Tracking
Punch-in and punch-out timestamps are stored in the database.
Working hours are calculated from the recorded timestamps.

## 5. Attendance Corrections
Corrections save the previous values, updated values,
reason, person making the correction, and correction time.

## 6. Analytics
MongoDB aggregation pipelines calculate employee working
hours and daily attendance summaries.

## 7. Configuration
The MongoDB connection string can be configured using the
MONGODB_URI environment variable.

## Limitations
These are initial design decisions. Additional business rules,
testing, and validation against the complete assignment
specification are still required.
