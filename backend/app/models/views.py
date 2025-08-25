from starlette_admin.contrib.sqla import Admin, ModelView
from .utilisateur import Utilisateur
from .appareil import Appareil
from .sim import SIM
from .notification import Notification
from .journal_audit import JournalAudit
from .imei import IMEI
from .recherche import Recherche
from .import_export import ImportExport
from .password_reset import PasswordReset
from .email_verification import EmailVerification

# استورد باقي النماذج هنا

class UtilisateurAdmin(ModelView, model=Utilisateur):
    column_list = ["id", "nom", "email", "type_utilisateur"]

class AppareilAdmin(ModelView, model=Appareil):
    column_list = ["id", "imei", "utilisateur_id"]

class SimAdmin(ModelView,model=SIM):
    column_list = ["id", "numero", "utilisateur_id","iccid","operateur"]

class NotificationAdmin(ModelView, model=Notification):
    column_list = ["id", "type", "destinataire", "statut"]

class RechercheAdmin(ModelView, model=Recherche):
    column_list = ["id", "utilisateur_id", "date_recherche", "resultats"]

class ImportExportAdmin(ModelView, model=ImportExport):
    column_list = ["id", "type", "date_import", "date_export"]

class PasswordResetAdmin(ModelView, model=PasswordReset):
    column_list = ["id", "utilisateur_id", "date_demande", "date_expiration"]

class EmailVerificationAdmin(ModelView, model=EmailVerification):
    column_list = ["id", "utilisateur_id", "date_envoi", "date_verification"]

# أضف باقي النماذج بنفس الطريقة
