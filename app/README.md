
# HROne Employee Attendance API

## Project Overview
This project is a REST API for managing employee attendance
using Python, FastAPI, and MongoDB.

## Technologies Used
- Python 3.11+
- FastAPI
- MongoDB
- PyMongo

## Features
- Create and view employees
- Record employee punch-in and punch-out
- Calculate working hours
- Correct attendance records
- Maintain attendance correction history
- Generate daily attendance analytics
- Calculate total working hours using MongoDB aggregation

## Setup Instructions
1. Install Python 3.11 or later.
2. Install and start MongoDB.
3. Install the required packages:

   pip install -r requirements.txt

4. Start the application:

   uvicorn app.main:app --reload

5. Open the API documentation:

   http://127.0.0.1:8000/docs

## Database Configuration
The application uses MongoDB.
The default connection is mongodb://localhost:27017.
Set the MONGODB_URI environment variable to use another
MongoDB connection string.

## Current Limitations
This is an initial implementation and has not yet been
fully tested against the assignment requirements.

Late-arrival rules, overtime calculations, and other
business rules need further implementation or verification.
Automated tests and complete API contract validation are
still pending.
