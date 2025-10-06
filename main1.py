from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import numpy as np
import uuid
import cv2
import base64
import os
import tempfile
from gtts import gTTS
from urllib.parse import quote_plus

# -----------------------
# Custom Module Imports
# -----------------------
from agent.bp2 import chat_with_agent
from face_recognitionplsql import (
    load_face_app,
    cosine_similarity,
    identify_person,
    generate_card_for_employee
)
from databasePLSQL import fetch_all_employees
from datetime import date, datetime

# -----------------------
# App Initialization
# -----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------
# Static & Template Mounts
# -----------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output_cards", StaticFiles(directory="output_cards"), name="output_cards")
templates = Jinja2Templates(directory="templates")

# -----------------------
# Routes
# -----------------------

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/index", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/hr", response_class=HTMLResponse)
def hr_page(request: Request):
    return templates.TemplateResponse("hr.html", {"request": request})

@app.get("/other_emp_benefits", response_class=HTMLResponse)
def hr_page(request: Request):
    return templates.TemplateResponse("other_emp_benefits.html", {"request": request})

@app.get("/holidays", response_class=HTMLResponse)
def holidays_page(request: Request):
    return templates.TemplateResponse("holidays.html", {"request": request})

@app.get("/insurance", response_class=HTMLResponse)
def insurance_page(request: Request):
    return templates.TemplateResponse("insurance.html", {"request": request})


# @app.get("/chat", response_class=HTMLResponse)
# def chat(request: Request):
#     name = request.query_params.get("name", "Guest")
#     return templates.TemplateResponse("chat.html", {"request": request, "name": name})

@app.get("/scan", response_class=HTMLResponse)
def scan_page(request: Request):
    return templates.TemplateResponse("Scanpage.html", {"request": request})


@app.get("/facerecog", response_class=HTMLResponse)
def face_recog_page(request: Request):
    # Optionally pass name param
    name = request.query_params.get("name", "Guest")
    return templates.TemplateResponse("FaceRecog.html", {"request": request, "name": name})


@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    # ⚠️ Replace chat.html with Chat1.html here
    name = request.query_params.get("name", "Guest")
    return templates.TemplateResponse("Chat1.html", {"request": request, "name": name})


@app.get("/template", response_class=HTMLResponse)
def show_template(request: Request, title: str = "", message: str = "", image: str = ""):
    return templates.TemplateResponse("template.html", {
        "request": request,
        "title": title,
        "message": message,
        "image": image
    })
@app.get("/wishes-page", response_class=HTMLResponse)
def wishes_page(request: Request):
    return templates.TemplateResponse("wishes.html", {"request": request})
@app.get("/office-layout", response_class=HTMLResponse)
def office_layout(request: Request):
    return templates.TemplateResponse("office_layout.html", {"request": request})

# @app.get("/wishes")
# def get_wishes():
#     today = date.today()
#     employees = fetch_all_employees()

#     birthdays = []
#     anniversaries = []

#     if employees:
#         for emp in employees:
#             name = emp.get("name")
#             dob_str = emp.get("dob")
#             doj_str = emp.get("doj")  # joining date (if you store work anniversary)

#             # ✅ Birthday check
#             if dob_str:
#                 try:
#                     dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
#                     if (dob.month, dob.day) == (today.month, today.day):
#                         birthdays.append(name)
#                 except Exception:
#                     pass

#             # 🎉 Work anniversary check
#             if doj_str:
#                 try:
#                     doj = datetime.strptime(doj_str, "%Y-%m-%d").date()
#                     if (doj.month, doj.day) == (today.month, today.day):
#                         anniversaries.append(name)
#                 except Exception:
#                     pass

#     return JSONResponse({
#         "birthdays": birthdays,
#         "anniversaries": anniversaries
#     })

# -----------------------
# Voice Q&A API
# -----------------------
class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Question):
    try:
        result = chat_with_agent(q.question)
        return {"answer": result}
    except Exception as e:
        print("❌ Error in /ask:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------
# Face Recognition API
# -----------------------
@app.post("/recognize-face")
async def recognize_face(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        app_model = load_face_app()
        faces = app_model.get(frame)

        if not faces:
            return JSONResponse({"success": False, "message": "No face detected"})

        emb = faces[0].embedding
        employees = fetch_all_employees()
        match = identify_person(emb, employees)

        if match:
            name = match.get("name")
            greeting_data = generate_card_for_employee(match)

            greeting = ""
            redirect_url = None

            if greeting_data:
                # Create redirect URL for /template
                redirect_url = (
                    f"/template?"
                    f"title={quote_plus(greeting_data['event'])}"
                    f"&message={quote_plus(greeting_data['message'])}"
                    f"&image={quote_plus(greeting_data['image_url'])}"
                )
                greeting = greeting_data["message"]
            else:
                greeting = f"Hello {name}, good to see you!"

            audio_b64 = text_to_base64(greeting)

            return {
                "success": True,
                "name": name,
                "greeting": greeting,
                "audio_base64": audio_b64,
                "redirect_url": redirect_url
            }

        else:
            return JSONResponse({"success": False, "message": "Face not recognized"})

    except Exception as e:
        print("❌ Face recognition error:", str(e))
        raise HTTPException(status_code=500, detail="Error processing face image")


# -----------------------
# Utility: Text to Base64 Audio
# -----------------------
def text_to_base64(text):
    tts = gTTS(text=text[:300], lang="en")
    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp3")
    tts.save(temp_path)

    with open(temp_path, "rb") as f:
        audio_data = f.read()
    os.remove(temp_path)

    return base64.b64encode(audio_data).decode()
