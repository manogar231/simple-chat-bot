from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base, User

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

# Predefined chatbot responses
chat_responses = {
    "hello": "Hi there! How can I help you today?",
    "how are you": "I'm just a bot, but I'm here to help!",
    "stress": "It's okay to feel stressed. Try deep breathing exercises!",
    "default": "I'm not sure about that, but I'm here to listen."
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Add HTML Page Routes Here
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup/")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Signup
@app.post("/signup/")
async def signup(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose a different one.")

    hashed_password = pwd_context.hash(password)  # Ensure password is hashed before storing
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

# Chatbot Endpoint
@app.post("/chat/")
async def chatbot(request: Request, message: str = Form(...)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    message = message.lower().strip()  # Ensure consistent format

    # Improve chatbot responses with better keyword matching
    if "hello" in message:
        response = "Hi there! How can I help you today?"
    elif "how are you" in message:
        response = "I'm just a bot, but I'm here to help!"
    elif "stress" in message or "stressed" in message:
        response = "It's okay to feel stressed. Try deep breathing exercises!"
    elif "help" in message:
        response = "I'm here to assist you! Please tell me what you need help with."
    else:
        response = "I'm not sure about that, but I'm here to listen."

    return JSONResponse({"response": response})


@app.get("/chat/")
async def chat_page(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("index.html", {"request": request, "username": user})


