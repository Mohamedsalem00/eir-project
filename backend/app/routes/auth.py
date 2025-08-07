from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
import logging

from ..core.dependencies import get_db, get_current_user
from ..core.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.auth import CreationUtilisateur, ConnexionUtilisateur, Jeton, ReponseUtilisateur
from ..models.utilisateur import Utilisateur
from ..models.journal_audit import JournalAudit
from datetime import datetime

# Configuration du logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authentification", tags=["Authentification"])

@router.post("/inscription", response_model=ReponseUtilisateur)
def register(user_data: CreationUtilisateur, request: Request, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    
    Crée un nouveau compte utilisateur avec les informations fournies.
    L'email doit être unique dans le système.
    
    Args:
        user_data: Données d'inscription de l'utilisateur
        request: Objet de requête FastAPI
        db: Session de base de données
    
    Returns:
        ReponseUtilisateur: Informations de l'utilisateur créé
    
    Raises:
        HTTPException: Si l'email est déjà utilisé (400)
    """
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
        if existing_user:
            logger.warning(f"Tentative d'inscription avec email existant: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà enregistré dans le système"
            )
        
        # Créer un nouveau utilisateur
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
        
        # Enregistrer l'inscription dans le journal d'audit
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Inscription utilisateur: {user.email}",
            date=datetime.now(),
            utilisateur_id=user.id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Nouvel utilisateur inscrit: {user.email}")
        
        return ReponseUtilisateur(
            id=str(user.id),
            nom=user.nom,
            email=user.email,
            type_utilisateur=user.type_utilisateur
        )
        
    except HTTPException:
        # Re-lancer les exceptions HTTP
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de l'inscription"
        )


@router.post("/connexion", response_model=Jeton)
def login(user_credentials: ConnexionUtilisateur, request: Request, db: Session = Depends(get_db)):
    """
    Connexion utilisateur
    
    Authentifie un utilisateur avec son email et mot de passe.
    Retourne un token JWT valide pour l'accès aux ressources protégées.
    
    Args:
        user_credentials: Informations de connexion (email et mot de passe)
        request: Objet de requête FastAPI
        db: Session de base de données
    
    Returns:
        Jeton: Token d'accès JWT et type de token
    
    Raises:
        HTTPException: Si les identifiants sont incorrects (401)
    """
    try:
        logger.info(f"Tentative de connexion pour l'email: {user_credentials.email}")
        
        user = db.query(Utilisateur).filter(Utilisateur.email == user_credentials.email).first()
        
        if not user:
            logger.warning(f"Tentative de connexion avec email inexistant: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Utilisateur trouvé: {user.email}")
        
        # Vérifier le mot de passe contre le hash stocké en base
        password_valid = verify_password(user_credentials.mot_de_passe, user.mot_de_passe)
        
        if not password_valid:
            logger.warning(f"Échec de la vérification du mot de passe pour: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Créer le token d'accès
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "user_type": user.type_utilisateur
            },
            expires_delta=access_token_expires
        )
        
        # Enregistrer la connexion dans le journal d'audit
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Connexion utilisateur: {user.email}",
            date=datetime.now(),
            utilisateur_id=user.id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Connexion réussie pour l'utilisateur: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        # Re-lancer les exceptions HTTP
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de la connexion"
        )

@router.get("/profile", response_model=ReponseUtilisateur)
def get_profile(current_user: Utilisateur = Depends(get_current_user)):
    """
    Récupérer le profil utilisateur
    
    Retourne les informations du profil de l'utilisateur actuellement connecté.
    Nécessite un token d'authentification valide dans l'en-tête Authorization.
    
    Args:
        current_user: Utilisateur authentifié (injecté automatiquement)
    
    Returns:
        ReponseUtilisateur: Informations du profil utilisateur
    
    Raises:
        HTTPException: Si le token est invalide ou expiré (401)
    """
    try:
        logger.info(f"Récupération du profil pour l'utilisateur: {current_user.email}")
        
        return ReponseUtilisateur(
            id=str(current_user.id),
            nom=current_user.nom,
            email=current_user.email,
            type_utilisateur=current_user.type_utilisateur
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de la récupération du profil"
        )

@router.post("/deconnexion")
def logout(current_user: Utilisateur = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Déconnexion utilisateur
    
    Déconnecte l'utilisateur actuellement connecté et enregistre l'action
    dans le journal d'audit à des fins de traçabilité et de sécurité.
    
    Note: Dans une implémentation JWT stateless, cette fonction sert principalement
    à l'audit. Pour une sécurité renforcée, considérez l'implémentation d'une
    liste noire de tokens (token blacklist).
    
    Args:
        current_user: Utilisateur authentifié (injecté automatiquement)
        db: Session de base de données
    
    Returns:
        dict: Message de confirmation de déconnexion
    
    Raises:
        HTTPException: Si le token est invalide (401) ou erreur serveur (500)
    """
    try:
        logger.info(f"Déconnexion de l'utilisateur: {current_user.email}")
        
        # Enregistrer la déconnexion dans le journal d'audit
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Déconnexion utilisateur: {current_user.email}",
            date=datetime.now(),
            utilisateur_id=current_user.id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Déconnexion réussie pour l'utilisateur: {current_user.email}")
        
        return {"message": "Déconnexion réussie"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur lors de la déconnexion"
        )
