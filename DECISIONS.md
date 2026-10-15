# Design Decisions

## 1. Programming Language
Python is used because it is simple and suitable for API development.

## 2. Framework
FastAPI is used to build REST API endpoints and provide automatic API documentation.

## 3. Database
MongoDB is used to store employee details, attendance records, and audit logs.

## 4. Attendance Records
Punch-in and punch-out times are stored for each employee and attendance date.

## 5. Audit Logs
Attendance corrections are recorded with details about the changes and the reason.

## 6. Analytics
Database aggregation is used to calculate daily attendance summaries and employee working hours.

## 7. Limitations
The application requires MongoDB to run. Testing and some attendance rules may need further implementation.
