from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.wiki_image import fetch_wikipedia_image

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


Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class InterestsRequest(BaseModel):
    interests: list[str]


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
        interest_name_normalized = interest_name.strip().lower()
        interest = db.query(Interest).filter(Interest.name == interest_name_normalized).first()

        if not interest:
            image_url = fetch_wikipedia_image(interest_name_normalized)
            interest = Interest(name=interest_name_normalized, image_url=image_url)
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


@app.post("/fetch-news")
def fetch_and_store_news(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_interests = db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id
    ).all()

    stored_chunks = 0

    for user_interest in user_interests:
        interest = db.query(Interest).filter(
            Interest.id == user_interest.interest_id
        ).first()

        if interest:
            articles = fetch_news(interest.name)
            stored_chunks += process_and_store_articles(articles)

    return {
        "message": "News fetched successfully",
        "chunks_stored": stored_chunks
    }

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