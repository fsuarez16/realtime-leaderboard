from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import SessionLocal, User, Score, get_db
from. redis_client import redis_client
from .auth import create_access_token, decode_token, get_password_hash, verify_password
# from .models import User, ScoreSubmission
# from .models import User
# from .models import ScoreSubmission
from datetime import datetime

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime


# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./leaderboard.db"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from contextlib import contextmanager
@contextmanager
def db_session(db_url):
    """ Creates a context with an open SQLAlchemy session.
    """
    engine = create_engine(db_url)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_session
    db_session.close()
    connection.close()


# with db_session("sqlite:///./leaderboard.db") as db:
#     foos = db.query(User).all()
#     print(foos)
engine = create_engine('sqlite:///./leaderboard.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create a query to select all users
print(User)
query = session.query(User)
print(query)

app = FastAPI()

# Add enumerate to Jinja2 globals
templates = Jinja2Templates(directory="backend/templates")
templates.env.globals.update(enumerate=enumerate)

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Register page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Submit score page
@app.get("/submit_score", response_class=HTMLResponse)
async def submit_score_page(request: Request):
    return templates.TemplateResponse("submit_score.html", {"request": request})

# Leaderboard page
# Leaderboard page
@app.get("/leaderboard/{game}", response_class=HTMLResponse)
async def leaderboard_page(request: Request, game: str, db: Session = Depends(get_db)):
    # Fetch all scores from Redis (real-time leaderboard)
    redis_scores = redis_client.zrevrange(f"leaderboard:{game}", 0, -1, withscores=True)

    # Fetch all scores from SQLite (persistent score history)
    sqlite_scores = db.query(Score).filter(Score.game == game).all()

    # Combine Redis and SQLite scores
    all_scores = []
    for username, score in redis_scores:
        all_scores.append({"username": username, "score": score, "source": "Redis"})

    for score in sqlite_scores:
        user = db.query(User).filter(User.id == score.user_id).first()
        if user:
            all_scores.append({"username": user.username, "score": score.score, "source": "SQLite"})

    # Sort all scores by score in descending order
    all_scores.sort(key=lambda x: x["score"], reverse=True)

    return templates.TemplateResponse("leaderboard.html", {"request": request, "game": game, "leaderboard": all_scores})



# Login form submission
@app.post("/login", response_class=RedirectResponse)
async def login_form(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()  # Corrected query
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": username})
    response = RedirectResponse(url="/submit_score", status_code=303)
    response.set_cookie(key="access_token", value=access_token)
    return response

# Register form submission
@app.post("/register", response_class=RedirectResponse)
async def register_form(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()  # Corrected query
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

# Submit score form submission
@app.post("/submit_score", response_class=RedirectResponse)
async def submit_score_form(
    request: Request,
    game: str = Form(...),
    score: float = Form(...),
    db: Session = Depends(get_db)
):
    # Server-side validation
    if score < 0 or score > 9:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 9.")

    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(access_token)
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()  # Corrected query
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Add score to Redis leaderboard
        redis_client.zadd(f"leaderboard:{game}", {username: score})

        # Save score to SQLite database
        new_score = Score(user_id=user.id, game=game, score=score, timestamp=datetime.utcnow())
        db.add(new_score)
        db.commit()

        return RedirectResponse(url=f"/leaderboard/{game}", status_code=303)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")