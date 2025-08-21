from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import uuid
import os
import logging
import secrets
import random

from ..core.dependencies import get_db, get_current_user
from ..core.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.auth import CreationUtilisateur, ConnexionUtilisateur, Jeton, ReponseUtilisateur, ProfilUtilisateurDetaille
from ..schemas.password_reset import (
    DemandeResetPassword, VerificationCodeReset, NouveauMotDePasse, 
    ReponseResetPassword, MethodeVerification
)
from ..models.utilisateur import Utilisateur
from ..models.password_reset import PasswordReset
from ..models.journal_audit import JournalAudit
from ..models.email_verification import EmailVerification
from ..services.eir_notifications import EIRNotificationService
from ..services.sms_service import sms_service
from ..core.i18n_deps import get_current_translator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authentification", tags=["Authentification"])

@router.post("/inscription")
async def register(user_data: CreationUtilisateur, request: Request, db: Session = Depends(get_db), translator = Depends(get_current_translator)):
    try:
        existing_user = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("email_deja_enregistre")
            )

        if user_data.type_utilisateur == "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translator.translate("inscription_admin_interdite")
            )
        
        default_access_level = "standard"
        if user_data.type_utilisateur == "operateur":
            default_access_level = "eleve"
        
        hashed_password = get_password_hash(user_data.mot_de_passe)
        user = Utilisateur(
            id=uuid.uuid4(),
            nom=user_data.nom,
            email=user_data.email,
            mot_de_passe=hashed_password,
            type_utilisateur=user_data.type_utilisateur,
            niveau_acces=default_access_level,
            est_actif=True,
            email_valide=False,
            numero_telephone=getattr(user_data, 'numero_telephone', None)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Inscription utilisateur: {user.email}",
            date=datetime.now(),
            utilisateur_id=user.id
        )
        db.add(audit)
        db.commit()

        try:
            token = secrets.token_urlsafe(32)
            verification = EmailVerification(
                utilisateur_id=user.id,
                token=token,
                date_expiration=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            db.add(verification)
            db.commit()

            origin = request.headers.get("origin")
            allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
            
            base_url = allowed_origins[0] if allowed_origins and allowed_origins[0] else "https://votre-site.com"
            if origin and origin in allowed_origins:
                base_url = origin

            verification_url = f"{base_url}/verify-email?token={token}"

            await EIRNotificationService.notifier_verification_email(
                user_id=str(user.id),
                verification_url=verification_url
            )
            logger.info(f"Email de vérification envoyé à : {user.email}")
        except Exception as e:
            logger.warning(f"Échec de l'envoi de l'email de vérification à {user.email}: {str(e)}")

        logger.info(f"Nouvel utilisateur inscrit (non validé) : {user.email}")

        return {
            "message": translator.translate("inscription_reussie_verifier_email"),
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur")
        )

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db), translator = Depends(get_current_translator)):
    verification = db.query(EmailVerification).filter(EmailVerification.token == token).first()
    if not verification:
        raise HTTPException(status_code=400, detail=translator.translate("token_verification_invalide"))
    if verification.used:
        raise HTTPException(status_code=400, detail=translator.translate("lien_verification_utilise"))
    
    date_exp = verification.date_expiration
    if date_exp.tzinfo is None:
        date_exp = date_exp.replace(tzinfo=timezone.utc)
    if date_exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail=translator.translate("lien_verification_expire"))

    user = db.query(Utilisateur).filter(Utilisateur.id == verification.utilisateur_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=translator.translate("utilisateur_non_trouve"))
    
    user.email_valide = True
    verification.used = True
    db.commit()
    
    try:
        await EIRNotificationService.notifier_email_verifie(str(user.id))
    except Exception as e:
        logger.warning(f"Erreur lors de l'envoi de la notification de succès de vérification: {str(e)}")
        
    return {"message": translator.translate("email_verifie_succes_connexion")}

@router.post("/resend-verification-email")
async def resend_verification_email(data: dict, request: Request, db: Session = Depends(get_db), translator = Depends(get_current_translator)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail=translator.translate("email_requis"))
    
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=translator.translate("utilisateur_non_trouve"))
    if user.email_valide:
        raise HTTPException(status_code=400, detail=translator.translate("email_deja_verifie"))

    db.query(EmailVerification).filter(
        EmailVerification.utilisateur_id == user.id,
        EmailVerification.used == False
    ).update({"used": True})
    
    token = secrets.token_urlsafe(32)
    verification = EmailVerification(
        utilisateur_id=user.id,
        token=token,
        date_expiration=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    db.add(verification)
    db.commit()

    origin = request.headers.get("origin")
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    base_url = allowed_origins[0] if allowed_origins and allowed_origins[0] else "https://eir-project.vercel.app"
    if origin and origin in allowed_origins:
        base_url = origin
    verification_url = f"{base_url}/verify-email?token={token}"

    try:
        await EIRNotificationService.notifier_verification_email(str(user.id), verification_url=verification_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=translator.translate("erreur_envoi_email"))
        
    return {"message": translator.translate("nouvel_email_verification_envoye")}



@router.post("/connexion", response_model=Jeton)
async def login(user_credentials: ConnexionUtilisateur, request: Request, db: Session = Depends(get_db), translator = Depends(get_current_translator)):
    """
    Connexion utilisateur
    """
    try:
        logger.info(f"Tentative de connexion pour l'email: {user_credentials.email}")

        user = db.query(Utilisateur).filter(Utilisateur.email == user_credentials.email).first()

        if not user:
            logger.warning(f"Tentative de connexion avec email inexistant: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=translator.translate("email_ou_mot_de_passe_incorrect"),
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Vérifier si l'email a été validé
        if not user.email_valide:
            logger.warning(f"Tentative de connexion avec email non vérifié: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="EMAIL_NON_VERIFIE"

            )

        password_valid = verify_password(user_credentials.mot_de_passe, user.mot_de_passe)

        if not password_valid:
            logger.warning(f"Échec de la vérification du mot de passe pour: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=translator.translate("email_ou_mot_de_passe_incorrect"),
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "user_type": user.type_utilisateur},
            expires_delta=access_token_expires
        )

        logger.info(f"Connexion réussie pour l'utilisateur: {user.email}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException as http_exc:
        # Propager l'exception HTTP pour que FastAPI gère le code et le message
        raise http_exc
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur")
        )

@router.get("/profile", response_model=ProfilUtilisateurDetaille)
async def get_profile_detailed(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Récupérer le profil utilisateur détaillé pour le frontend
    """
    try:
        logger.info(f"Récupération du profil détaillé pour l'utilisateur: {current_user.email}")

        from ..models.journal_audit import JournalAudit

        # Dernière connexion
        derniere_connexion_audit = db.query(JournalAudit).filter(
            JournalAudit.utilisateur_id == current_user.id,
            JournalAudit.action.like('Connexion utilisateur:%')
        ).order_by(JournalAudit.date.desc()).first()
        derniere_connexion = derniere_connexion_audit.date if derniere_connexion_audit else None

        # Nombre total de connexions
        nb_connexions = db.query(JournalAudit).filter(
            JournalAudit.utilisateur_id == current_user.id,
            JournalAudit.action.like('Connexion utilisateur:%')
        ).count()

        # Activités récentes (7 derniers jours)
        date_limite = datetime.now() - timedelta(days=7)
        activites_recentes = db.query(JournalAudit).filter(
            JournalAudit.utilisateur_id == current_user.id,
            JournalAudit.date >= date_limite
        ).count()

        # Permissions dynamiques selon type et niveau d'accès
        permissions = []
        if current_user.type_utilisateur == "administrateur":
            permissions = [
                "gestion_utilisateurs",
                "gestion_appareils",
                "consultation_audits",
                "gestion_notifications",
                "configuration_systeme",
                "export_donnees",
                "gestion_base_donnees"
            ]
        elif current_user.type_utilisateur == "operateur":
            permissions = [
                "consultation_appareils",
                "recherche_imei",
                "recherche_tac",
                "consultation_historique_organisation",
                "gestion_organisation"
            ]
        elif current_user.type_utilisateur == "utilisateur_authentifie":
            permissions = [
                "consultation_appareils",
                "recherche_imei",
                "recherche_tac",
                "consultation_historique_personnel"
            ]
        else:
            permissions = ["consultation_appareils"]

        # Statistiques détaillées
        statistiques = {
            "nombre_connexions": nb_connexions,
            "activites_7_derniers_jours": activites_recentes,
            "compte_cree_depuis_jours": (datetime.now() - current_user.date_creation).days if getattr(current_user, 'date_creation', None) else 0,
            "derniere_activite": derniere_connexion.isoformat() if derniere_connexion else None
        }

        # Statut du compte
        statut_compte = "active" if current_user.est_actif else "inactif"

        # Audit log
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Consultation profil: {current_user.email}",
            date=datetime.now(),
            utilisateur_id=current_user.id
        )
        db.add(audit)
        db.commit()

        logger.info(f"Profil détaillé récupéré avec succès pour: {current_user.email}")

        # Return all relevant fields for frontend
        return ProfilUtilisateurDetaille(
            id=str(current_user.id),
            nom=current_user.nom,
            email=current_user.email,
            type_utilisateur=current_user.type_utilisateur,
            date_creation=getattr(current_user, 'date_creation', None),
            derniere_connexion=derniere_connexion,
            niveau_acces=getattr(current_user, 'niveau_acces', None),
            portee_donnees=getattr(current_user, 'portee_donnees', None),
            organisation=getattr(current_user, 'organisation', None),
            statut_compte=statut_compte,
            permissions=permissions,
            statistiques=statistiques,
            marques_autorisees=getattr(current_user, 'marques_autorisees', []),
            plages_imei_autorisees=getattr(current_user, 'plages_imei_autorisees', [])
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil détaillé: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur") if 'translator' in locals() else "Erreur interne du serveur lors de la récupération du profil"
        )

@router.get("/profile/simple", response_model=ReponseUtilisateur)
def get_profile_simple(current_user: Utilisateur = Depends(get_current_user)):
    """
    Récupérer le profil utilisateur (version simple)
    
    Version allégée qui retourne uniquement les informations de base.
    Utile pour les applications qui n'ont besoin que des données essentielles.
    
    Args:
        current_user: Utilisateur authentifié (injecté automatiquement)
    
    Returns:
        ReponseUtilisateur: Informations de base du profil utilisateur
    """
    try:
        logger.info(f"Récupération du profil simple pour l'utilisateur: {current_user.email}")
        
        return ReponseUtilisateur(
            id=str(current_user.id),
            nom=current_user.nom,
            email=current_user.email,
            type_utilisateur=current_user.type_utilisateur,
            niveau_acces=current_user.niveau_acces
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil simple: {str(e)}")
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


# ==========================================
# ENDPOINTS DE RÉINITIALISATION DE MOT DE PASSE
# ==========================================

@router.post("/mot-de-passe-oublie", response_model=ReponseResetPassword)
async def demander_reset_password(
    demande: DemandeResetPassword,
    request: Request,
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Demander une réinitialisation de mot de passe
    
    Génère un token de réinitialisation et envoie un code de vérification 
    par email ou SMS selon la méthode choisie.
    
    ### Support Multilingue:
    - Utilisez l'en-tête `Accept-Language` pour recevoir les messages dans votre langue
    - Langues supportées: `fr` (français), `en` (anglais), `ar` (arabe)
    
    ### Méthodes de vérification:
    - **EMAIL**: Code envoyé par email (par défaut)
    - **SMS**: Code envoyé par SMS (nécessite numéro de téléphone)
    
    ### Sécurité:
    - Token valide pour 1 heure
    - Code de vérification à 6 chiffres
    - Journalisation des tentatives
    """
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(Utilisateur).filter(Utilisateur.email == demande.email).first()
        if not user:
            # Ne pas révéler si l'email existe ou non pour la sécurité
            logger.warning(f"Tentative de reset pour email inexistant: {demande.email}")
            return ReponseResetPassword(
                success=True,
                message=translator.translate("reset_password_demande_envoyee"),
                token=None,
                methode_verification=None,
                expires_in_minutes=60
            )
        
        # Vérifier la méthode de vérification
        if demande.methode_verification == MethodeVerification.SMS and not demande.telephone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("telephone_requis_sms")
            )
        
        # Invalider tous les anciens tokens de reset pour cet utilisateur
        db.query(PasswordReset).filter(
            PasswordReset.utilisateur_id == user.id,
            PasswordReset.utilise == False
        ).update({"utilise": True})
        
        # Générer un nouveau token et code de vérification
        reset_token = secrets.token_urlsafe(32)
        verification_code = str(random.randint(100000, 999999))
        
        # Créer l'enregistrement de reset
        password_reset = PasswordReset(
            utilisateur_id=user.id,
            token=reset_token,
            methode_verification=demande.methode_verification.value,
            code_verification=verification_code,
            email=demande.email,
            telephone=demande.telephone if demande.methode_verification == MethodeVerification.SMS else None,
            adresse_ip=request.client.host if request.client else None
        )
        
        db.add(password_reset)
        db.commit()
        
        # Envoyer le code de vérification
        if demande.methode_verification == MethodeVerification.EMAIL:
            try:
                await EIRNotificationService.notifier_reset_password(
                    user_id=str(user.id),
                    lien_reset=f"Code de vérification: {verification_code}"
                )
                logger.info(f"Email de reset password envoyé à: {user.email}")
            except Exception as e:
                logger.error(f"Erreur envoi email reset password: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=translator.translate("erreur_envoi_email")
                )
        
        elif demande.methode_verification == MethodeVerification.SMS:
            try:
                message = f"Code de vérification EIR: {verification_code}. Valide pendant 1 heure."
                sms_result = sms_service.send_sms(demande.telephone, message)
                if not sms_result.get('success', False):
                    raise Exception(sms_result.get('error', 'Erreur inconnue'))
                logger.info(f"SMS de reset password envoyé à: {demande.telephone}")
            except Exception as e:
                logger.error(f"Erreur envoi SMS reset password: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=translator.translate("erreur_envoi_sms")
                )
        
        # Journaliser la demande
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Demande reset password: {user.email} via {demande.methode_verification.value}",
            date=datetime.now(),
            utilisateur_id=user.id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Demande de reset password pour: {user.email} via {demande.methode_verification.value}")
        
        return ReponseResetPassword(
            success=True,
            message=translator.translate("reset_password_code_envoye"),
            token=reset_token,
            methode_verification=demande.methode_verification.value,
            expires_in_minutes=60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la demande de reset password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur")
        )


@router.post("/verifier-code-reset", response_model=ReponseResetPassword)
async def verifier_code_reset(
    verification: VerificationCodeReset,
    request: Request,
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Vérifier le code de réinitialisation
    
    Valide le code de vérification reçu par email ou SMS.
    Une fois validé, le token peut être utilisé pour changer le mot de passe.
    
    ### Paramètres:
    - **token**: Token de reset reçu
    - **code_verification**: Code à 6 chiffres reçu par email/SMS
    
    ### Retour:
    - Token validé pour procéder au changement de mot de passe
    """
    try:
        # Chercher le token de reset
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.token == verification.token,
            PasswordReset.utilise == False
        ).first()
        
        if not password_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("token_reset_invalide")
            )
        
        # Vérifier l'expiration
        if password_reset.is_expired():
            password_reset.utilise = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("token_reset_expire")
            )
        
        # Vérifier le code de vérification
        if password_reset.code_verification != verification.code_verification:
            # Journaliser la tentative de code incorrect
            audit = JournalAudit(
                id=uuid.uuid4(),
                action=f"Code de vérification incorrect pour token: {verification.token[:8]}...",
                date=datetime.now(),
                utilisateur_id=password_reset.utilisateur_id
            )
            db.add(audit)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("code_verification_incorrect")
            )
        
        # Journaliser la vérification réussie
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Code de vérification validé pour: {password_reset.utilisateur.email}",
            date=datetime.now(),
            utilisateur_id=password_reset.utilisateur_id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Code de vérification validé pour l'utilisateur: {password_reset.utilisateur.email}")
        
        # Calculer le temps restant avant expiration
        time_remaining = password_reset.date_expiration - datetime.now(timezone.utc)
        expires_in_minutes = max(0, int(time_remaining.total_seconds() / 60))
        
        return ReponseResetPassword(
            success=True,
            message=translator.translate("code_verification_valide"),
            token=verification.token,
            methode_verification=password_reset.methode_verification,
            expires_in_minutes=expires_in_minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur")
        )


@router.post("/nouveau-mot-de-passe", response_model=ReponseResetPassword)
async def changer_mot_de_passe(
    nouveau_mdp: NouveauMotDePasse,
    request: Request,
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Définir un nouveau mot de passe
    
    Change le mot de passe de l'utilisateur avec un token validé.
    
    ### Paramètres:
    - **token**: Token validé lors de la vérification du code
    - **nouveau_mot_de_passe**: Nouveau mot de passe (minimum 8 caractères)
    - **confirmer_mot_de_passe**: Confirmation du nouveau mot de passe
    
    ### Sécurité:
    - Le token devient inutilisable après usage
    - Journalisation complète de l'opération
    - Notification de sécurité envoyée
    """
    try:
        # Valider que les mots de passe correspondent
        try:
            nouveau_mdp.validate_passwords_match()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("mots_passe_non_identiques")
            )
        
        # Chercher le token de reset
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.token == nouveau_mdp.token,
            PasswordReset.utilise == False
        ).first()
        
        if not password_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("token_reset_invalide")
            )
        
        # Vérifier l'expiration
        if password_reset.is_expired():
            password_reset.utilise = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("token_reset_expire")
            )
        
        # Récupérer l'utilisateur
        user = password_reset.utilisateur
        
        # Hasher le nouveau mot de passe
        hashed_password = get_password_hash(nouveau_mdp.nouveau_mot_de_passe)
        
        # Mettre à jour le mot de passe
        user.mot_de_passe = hashed_password
        
        # Marquer le token comme utilisé
        password_reset.mark_as_used()
        
        # Invalider tous les autres tokens de reset pour cet utilisateur
        db.query(PasswordReset).filter(
            PasswordReset.utilisateur_id == user.id,
            PasswordReset.id != password_reset.id,
            PasswordReset.utilise == False
        ).update({"utilise": True})
        
        db.commit()
        
        # Journaliser le changement de mot de passe
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Mot de passe changé avec succès: {user.email}",
            date=datetime.now(),
            utilisateur_id=user.id
        )
        db.add(audit)
        db.commit()
        
        # Envoyer une notification de sécurité
        try:
            await EIRNotificationService.notifier_activite_suspecte(
                user_id=str(user.id),
                activite="Changement de mot de passe",
                details={
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "description": "Votre mot de passe a été changé avec succès",
                    "methode": password_reset.methode_verification
                }
            )
            logger.info(f"Notification de sécurité envoyée à: {user.email}")
        except Exception as e:
            logger.warning(f"Erreur envoi notification sécurité: {str(e)}")
        
        logger.info(f"Mot de passe changé avec succès pour: {user.email}")
        
        return ReponseResetPassword(
            success=True,
            message=translator.translate("mot_passe_change_succes"),
            token=None,  # Token invalidé après utilisation
            methode_verification=password_reset.methode_verification,
            expires_in_minutes=None  # Plus d'expiration après changement réussi
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_interne_serveur")
        )
