# Auto-Attendance-Tracker

A web-based automatic attendance management system using face recognition. Built with Flask, OpenCV (LBPH), and SQLite — no cloud services required.

## Features

- **Student Enrollment** — Enroll students with photos via upload or live camera capture
- **Face Recognition** — LBPH-based face recognition using OpenCV (no dlib/Azure required)
- **Attendance Marking** — Mark FN (Forenoon) and AN (Afternoon) sessions from a single class photo
- **Excel Reports** — Auto-generated color-coded attendance reports downloadable as `.xlsx`
- **Role-based Portals** — Separate dashboards for Admin, Class Teacher, and Student
- **Timetable Management** — Class teachers can manage their subject timetable
- **Manual Edit** — Edit or delete attendance records manually

## Tech Stack

- **Backend** — Python, Flask
- **Face Recognition** — OpenCV (LBPH Face Recognizer + Haar Cascade)
- **Database** — SQLite
- **Reports** — openpyxl
- **Frontend** — HTML, CSS (Jinja2 templates)

## Project Structure

```
Auto-Attendance-Tracker/
├── app.py                  # Main Flask application
├── face_engine.py          # Face detection & recognition logic
├── database.py             # DB schema & initialization
├── templates/
│   ├── admin/              # Admin portal pages
│   ├── ct/                 # Class teacher portal pages
│   └── student/            # Student portal pages
├── dataset/                # Enrolled student face images
├── data/                   # Trained models & excel per class/year
├── excel_reports/          # Generated attendance Excel files
├── uploads/                # Uploaded/captured class photos
└── requirements.txt
```

## Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/shambavi2007/Auto-Attendance-Tracker.git
cd Auto-Attendance-Tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the application**
```bash
python app.py
```

**4. Open in browser**
```
http://localhost:5000
```

## Default Admin Login

| Email | Password |
|-------|----------|
| admin@attendease.com | admin123 |

## How It Works

1. **Class Teacher signs up** → assigned to a class & section
2. **Enroll students** → upload or capture face photos per student
3. **Train model** → builds an LBPH model for the class
4. **Mark attendance** → upload a class photo → system detects & identifies faces → marks FN/AN status
5. **Download report** → export attendance as Excel with color-coded present/absent cells

## Requirements

```
flask
opencv-python
opencv-contrib-python
numpy
openpyxl
```

See `requirements.txt` for full list.

## License

MIT License — see [LICENSE](LICENSE)
