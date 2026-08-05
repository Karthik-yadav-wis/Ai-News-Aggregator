from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import User, Interest, UserInterest
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from services.news_fetcher import fetch_news
from services.rag_pipeline import process_and_store_articles
from services.summarizer import summarize_interests
from services.wiki_image import fetch_topic_image  
from services.scheduler import scheduler


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class InterestsRequest(BaseModel):
    interests: list[str]


class FetchNewsRequest(BaseModel):
    interests: Optional[list[str]] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload.get("user_id")

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    print("[Scheduler] Started — refreshing all saved interests periodically")


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()


@app.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password)
    )

    db.add(user)
    db.commit()

    return {"message": "User created successfully"}


@app.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/user/interests")
def save_user_interests(
    request: InterestsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for interest_name in request.interests:

        interest = db.query(Interest).filter(
            Interest.name == interest_name
        ).first()

        if not interest:
            image_url = fetch_topic_image(interest_name)
            interest = Interest(name=interest_name, image_url=image_url)
            db.add(interest)
            db.commit()
            db.refresh(interest)

        existing = db.query(UserInterest).filter(
            UserInterest.user_id == current_user.id,
            UserInterest.interest_id == interest.id
        ).first()

        if not existing:
            user_interest = UserInterest(
                user_id=current_user.id,
                interest_id=interest.id
            )
            db.add(user_interest)

    db.commit()

    return {"message": "Interests saved successfully"}


@app.get("/user/interests")
def get_user_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_interests = db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id
    ).all()

    result = []
    for ui in user_interests:
        interest = db.query(Interest).filter(Interest.id == ui.interest_id).first()
        if interest:
            result.append({
                "name": interest.name,
                "image_url": interest.image_url
            })

    return {"interests": result}


@app.post("/fetch-news")
def fetch_and_store_news(
    payload: Optional[FetchNewsRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # If the frontend sent a specific list of interests, only fetch those
    # (used when a user adds a new interest — don't re-fetch everything).
    # If no body was sent, fall back to ALL of the user's saved interests
    # (used for first-time onboarding and the manual refresh button).
    if payload and payload.interests:
        target_names = payload.interests
    else:
        user_interests = db.query(UserInterest).filter(
            UserInterest.user_id == current_user.id
        ).all()

        target_names = []
        for user_interest in user_interests:
            interest = db.query(Interest).filter(
                Interest.id == user_interest.interest_id
            ).first()
            if interest:
                target_names.append(interest.name)

    stored_chunks = 0
    for name in target_names:
        articles = fetch_news(name)
        stored_chunks += process_and_store_articles(articles, db,name)

    return {
        "message": "News fetched successfully",
        "chunks_stored": stored_chunks
    }


@app.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_interests = db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id
    ).all()

    interest_names = []
    for ui in user_interests:
        interest = db.query(Interest).filter(Interest.id == ui.interest_id).first()
        if interest:
            interest_names.append(interest.name)

    if not interest_names:
        raise HTTPException(status_code=400, detail="No interests set")

    summary = summarize_interests(interest_names)

    return {"summary": summary}