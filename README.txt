🗨️ Simple Chatbot with FastAPI  

This is a simple chatbot application built using FastAPI. It includes user authentication (signup & login) and provides predefined chatbot responses based on user input. The application features a session-based login system and a web interface using Jinja2 templates.  

🚀 Features  
✔️ User Signup & Login (Session-based Authentication)  
✔️ Secure Password Hashing with **bcrypt**  
✔️ Simple Chatbot with GenAI Integarated  
✔️ Frontend with **HTML, CSS, JavaScript (Fetch API)**  
✔️ Uses **PostgreSQL / SQLite** for user authentication  
✔️ Built with **FastAPI** and **SQLAlchemy**  

🛠️ Tech Stack  
Backend: FastAPI, SQLAlchemy  
Frontend: HTML, CSS, JavaScript  
Database: PostgreSQL (or SQLite for development)  
Authentication: Session-based login with hashed passwords  
Deployment: Works locally  

📌 Installation  

1️⃣ Clone the Repository  
git clone https://github.com/manogar231/simple-chat-bot.git
cd simple-chat-bot

2️⃣ Create a Virtual Environment  
python -m venv venv
source venv/bin/activate  

3️⃣ Install Dependencies  
pip install -r requirements.txt

4️⃣ Set Up Environment Variables  
Create a `.env` file in the project directory and add:  

DATABASE_URL=sqlite:///./test.db  # Change to your PostgreSQL URL if needed
SECRET_KEY=your_secret_key //just a ramdom key (word)
GOOGLE_API_KEY=<your_GENAI_API_key> you need to add the your api key here
GOOGLE_Model=gemini-1.5-flash // Change the model accordingly

5️⃣ Create DataBase in SQL or PostgreSQL 
  **You no need to create table at all. 

6️⃣ Start the Server  

uvicorn main:app --reload

The application will be accessible at: **http://127.0.0.1:8000/**  

🖥️ Usage  
1️⃣ Signup at `/signup/`  
2️⃣ Login at `/login/`  
3️⃣ Chat with the bot at `/chat/`  

🎯 API Endpoints  

| Method | Endpoint   | Description |
|--------|-----------|-------------|
| GET    | `/`       | Homepage    |
| GET    | `/signup/` | Signup Page |
| POST   | `/signup/` | Register New User |
| GET    | `/login/` | Login Page |
| POST   | `/login/` | Authenticate User |
| GET    | `/logout/` | Logout User |
| POST   | `/chat/` | Chatbot API |   // This api Endpoint is will Works for GenAI too 
