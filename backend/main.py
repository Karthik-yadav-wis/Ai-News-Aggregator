from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User
from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth import verify_token
from models import (
    User,
    Interest,
    UserInterest
)


Base.metadata.create_all(bind=engine)

app = FastAPI()
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload.get("user_id")

    db: Session = SessionLocal()

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
    request: SignupRequest
):

    db: Session = SessionLocal()

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
        password_hash=hash_password(
            request.password
        )
    )

    db.add(user)
    db.commit()

    return {
        "message": "User created successfully"
    }

@app.post("/login")
def login(
    request: LoginRequest
):

    db: Session = SessionLocal()

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"user_id": user.id}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/user/interests")
def save_user_interests(
    request: InterestsRequest,
    current_user: User = Depends(get_current_user)
):

    db: Session = SessionLocal()

    for interest_name in request.interests:

        # Check if interest exists
        interest = db.query(Interest).filter(
            Interest.name == interest_name
        ).first()

        # Create interest if not exists
        if not interest:

            interest = Interest(
                name=interest_name
            )

            db.add(interest)
            db.commit()
            db.refresh(interest)

        # Check relationship exists
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

    return {
        "message": "Interests saved successfully"
    }