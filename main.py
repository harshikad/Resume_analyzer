from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import fitz  # PyMuPDF for PDF parsing
import os
import shutil
import json
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .database import SessionLocal, engine
from .models import Resume, Base
from langchain_google_genai import GoogleGenerativeAI

from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API Key
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY is missing! Set it in .env or environment variables.")

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Google Gemini API Key setup
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure "uploads/" directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text.strip()

def analyze_resume(text):
    response = llm.invoke(text)  # Call Google Gemini API
    print("DEBUG: Raw Response from AI Model:", response)  # Debug Print

    if not response:
        raise HTTPException(status_code=500, detail="LLM returned an empty response!")

    try:
        return json.loads(response)  # Ensure valid JSON
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")



@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    print("📂 Received file:", file.filename)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("📜 Extracting text from PDF...")
    extracted_text = extract_text_from_pdf(file_path)
    
    if not extracted_text:
        print("❌ Failed to extract text.")
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")

    print("🤖 Analyzing resume with Gemini API...")
    resume_data = analyze_resume(extracted_text)
    
    print("✅ Extracted Data:", resume_data)

    try:
        resume_entry = Resume(file_name=file.filename, **resume_data)
        db.add(resume_entry)
        db.commit()
        db.refresh(resume_entry)
        print("✅ Resume saved successfully in DB!")

    except Exception as e:
        print("❌ Database Error:", e)
        raise HTTPException(status_code=500, detail="Database error while saving resume.")

    return {"message": "Resume uploaded successfully!", "data": resume_data}

# Fetch all resumes
@app.get("/get_resumes/")
def get_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).all()
    return resumes if resumes else {"message": "No resumes found."}

# Fetch resume details by ID
@app.get("/resume/{id}/")
def get_resume_details(id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
