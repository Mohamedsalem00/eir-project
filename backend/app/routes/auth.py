from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from ..core.dependencies import get_db, get_current_user
from ..core.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
from ..models.utilisateur import Utilisateur
from ..models.journal_audit import JournalAudit
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.mot_de_passe)
    user = Utilisateur(
        id=uuid.uuid4(),
        nom=user_data.nom,
        email=user_data.email,
        mot_de_passe=hashed_password,
        type_utilisateur=user_data.type_utilisateur
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log the registration
    audit = JournalAudit(
        id=uuid.uuid4(),
        action=f"User registered: {user.email}",
        date=datetime.now(),
        utilisateur_id=user.id
    )
    db.add(audit)
    db.commit()
    
    return UserResponse(
        id=str(user.id),
        nom=user.nom,
        email=user.email,
        type_utilisateur=user.type_utilisateur
    )


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    print(f"Login attempt for email: {user_credentials.email}")  # Debug
    
    user = db.query(Utilisateur).filter(Utilisateur.email == user_credentials.email).first()
    
    if not user:
        print("User not found in database")  # Debug
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"User found: {user.email}")  # Debug
    print(f"Password hash from DB: {user.mot_de_passe[:20]}...")  # Debug (first 20 chars only)
    
    # Verify the password against the hashed password in database
    password_valid = verify_password(user_credentials.mot_de_passe, user.mot_de_passe)
    print(f"Password verification result: {password_valid}")  # Debug
    
    if not password_valid:
        print("Password verification failed")  # Debug
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.type_utilisateur
        },
        expires_delta=access_token_expires
    )
    
    # Log the login
    audit = JournalAudit(
        id=uuid.uuid4(),
        action=f"User login: {user.email}",
        date=datetime.now(),
        utilisateur_id=user.id
    )
    db.add(audit)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: Utilisateur = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        nom=current_user.nom,
        email=current_user.email,
        type_utilisateur=current_user.type_utilisateur
    )

@router.post("/logout")
def logout(current_user: Utilisateur = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user (mainly for logging purposes)"""
    # Log the logout
    audit = JournalAudit(
        id=uuid.uuid4(),
        action=f"User logout: {current_user.email}",
        date=datetime.now(),
        utilisateur_id=current_user.id
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Successfully logged out"}
