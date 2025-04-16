from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base, User
import google.generativeai as genai 

load_dotenv()

app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"), session_cookie="session_id")

# Jinja2 templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create DB tables
Base.metadata.create_all(bind=engine)


# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Ensure this is set in your .env
genai.configure(api_key=GOOGLE_API_KEY)

GOOGLE_MODEL = os.getenv("GOOGLE_Model")
model = genai.GenerativeModel(GOOGLE_MODEL)  # Or your preferred model


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Home Page - Redirect to login if not authenticated
@app.get("/")
async def home(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return RedirectResponse(url="/chat", status_code=303)

# Signup Page
@app.get("/signup/")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Login Page
@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Signup
@app.post("/signup/")
async def signup(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose a different one.")

    hashed_password = pwd_context.hash(password)  # Hash password before storing
    print("Storing Hashed Password:", hashed_password)  # Debugging print

    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

# Login
@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=400, detail="User does not exist.")

    print("Stored Hashed Password:", user.hashed_password)  # Debugging print

    if not pwd_context.verify(password, user.hashed_password):
        print("Password verification failed!")  # Debugging print
        raise HTTPException(status_code=400, detail="Incorrect password.")

    request.session["user"] = user.username
    return RedirectResponse(url="/chat", status_code=303)

# Logout
@app.get("/logout/")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# Chat Page - Redirect to login if not authenticated
@app.get("/chat/")
async def chat_page(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("index.html", {"request": request, "username": user})

# Chatbot Endpoint
@app.post("/chat/")
async def chatbot(request: Request, message: str = Form(...)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    message = message.lower().strip()  # Ensure consistent format

    # Mental health prompt check
    if is_mental_health_related(message):
        try:
            response = generate_mental_health_response(message)
        except Exception as e:
            print(f"Error generating response: {e}")
            response = "I'm having trouble processing that right now. Please try again later."
    else:
        response = "I'm designed to help with mental health related questions.  Please rephrase your query or ask something related to mental well-being."

    return JSONResponse({"response": response})

# Helper function to check if a message is mental health related.  This is a VERY basic example; improve it for production.
def is_mental_health_related(message: str) -> bool:
    keywords = ["stress", "anxiety", "depression", "mental health", "therapy", "feeling down", "suicidal", "panic"]
    return any(keyword in message for keyword in keywords)

# Helper function to generate mental health response using Gemini
def generate_mental_health_response(message: str) -> str:
    prompt = f"""You are a supportive and helpful AI assistant specializing in mental health support.  Respond to the following message with empathy and provide helpful advice, resources, or coping strategies. Keep your responses very brief and concise, ideally under 50 words. Avoid giving medical diagnoses. If the user expresses thoughts of self-harm or suicide, gently encourage them to seek professional help immediately and provide resources like the Suicide Prevention Lifeline.

    Message: {message}

    Response:"""

    chat = model.start_chat()
    response = chat.send_message(prompt)  # Directly send the prompt
    return response.text