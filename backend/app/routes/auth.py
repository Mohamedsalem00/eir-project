from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import uuid
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
from ..services.eir_notifications import EIRNotificationService, envoyer_notification_bienvenue
from ..services.sms_service import sms_service
from ..core.i18n_deps import get_current_translator

# Configuration du logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authentification", tags=["Authentification"])

@router.post("/inscription", response_model=ReponseUtilisateur)
async def register(user_data: CreationUtilisateur, request: Request, db: Session = Depends(get_db)):
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
        
        # 📧 Send welcome email notification
        try:
            await envoyer_notification_bienvenue(str(user.id))
            logger.info(f"Welcome email sent to: {user.email}")
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
        
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
async def login(user_credentials: ConnexionUtilisateur, request: Request, db: Session = Depends(get_db)):
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
        
        # 📧 Send security alert for suspicious activity (example: new IP)
        try:
            # You can add logic here to detect suspicious login patterns
            ip_address = request.client.host if request.client else "unknown"
            # For now, just log the successful login
            logger.info(f"Login from IP: {ip_address} for user: {user.email}")
            
            # Uncomment to send security alerts for new IPs:
            await EIRNotificationService.notifier_activite_suspecte(
                user_id=str(user.id),
                activite="Connexion depuis nouvelle IP",
                details={
                    "ip_address": ip_address,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "description": f"Connexion réussie depuis {ip_address}"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to process login security check: {str(e)}")
        
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

@router.get("/profile", response_model=ProfilUtilisateurDetaille)
async def get_profile_detailed(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Récupérer le profil utilisateur détaillé
    
    Retourne les informations complètes du profil de l'utilisateur actuellement connecté,
    incluant les statistiques, permissions et informations de sécurité.
    
    ### Informations retournées:
    - **Informations de base**: ID, nom, email, type
    - **Dates importantes**: Création du compte, dernière connexion
    - **Statut et sécurité**: Statut du compte, permissions
    - **Statistiques**: Nombre de connexions, activités récentes
    - **Support multilingue**: Messages dans la langue préférée
    
    Args:
        current_user: Utilisateur authentifié (injecté automatiquement)
        db: Session de base de données
        translator: Service de traduction
    
    Returns:
        ProfilUtilisateurDetaille: Informations complètes du profil utilisateur
    
    Raises:
        HTTPException: Si le token est invalide ou expiré (401)
    """
    try:
        logger.info(f"Récupération du profil détaillé pour l'utilisateur: {current_user.email}")
        
        # Récupérer les statistiques de l'utilisateur
        from ..models.journal_audit import JournalAudit
        
        # Dernière connexion (dernière entrée "Connexion utilisateur" dans les logs)
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
        
        # Définir les permissions selon le type d'utilisateur
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
        elif current_user.type_utilisateur == "utilisateur_authentifie":
            permissions = [
                "consultation_appareils",
                "recherche_imei",
                "consultation_historique_personnel"
            ]
        
        # Statistiques détaillées
        statistiques = {
            "nombre_connexions": nb_connexions,
            "activites_7_derniers_jours": activites_recentes,
            "compte_cree_depuis_jours": (datetime.now() - current_user.date_creation).days if hasattr(current_user, 'date_creation') and current_user.date_creation else 0,
            "derniere_activite": derniere_connexion.isoformat() if derniere_connexion else None
        }
        
        # Déterminer le statut du compte
        statut_compte = "active"  # Par défaut, pourrait être enrichi avec une logique métier
        
        # Enregistrer la consultation du profil dans l'audit
        audit = JournalAudit(
            id=uuid.uuid4(),
            action=f"Consultation profil: {current_user.email}",
            date=datetime.now(),
            utilisateur_id=current_user.id
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"Profil détaillé récupéré avec succès pour: {current_user.email}")
        
        return ProfilUtilisateurDetaille(
            id=str(current_user.id),
            nom=current_user.nom,
            email=current_user.email,
            type_utilisateur=current_user.type_utilisateur,
            date_creation=getattr(current_user, 'date_creation', None),
            derniere_connexion=derniere_connexion,
            statut_compte=statut_compte,
            permissions=permissions,
            statistiques=statistiques
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
            type_utilisateur=current_user.type_utilisateur
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
