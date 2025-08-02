from datetime import datetime, timedelta
from typing import Dict, Any
from ..i18n.translator import Translator
from ..schemas.system import WelcomeResponse, APIMetadata, ContactInfo, SecurityInfo, ServiceCapabilities, APIEndpoints, TechnicalSpecs
import platform
import psutil
import os

class WelcomeService:
    def __init__(self, translator: Translator):
        self.translator = translator
        self.start_time = datetime.now()
    
    def get_welcome_response(self, request_url: str = "", user_type: str = "visitor") -> WelcomeResponse:
        """Generate comprehensive welcome response"""
        current_time = datetime.now()
        
        return WelcomeResponse(
            title=self.translator.translate("welcome_title"),
            description=self.translator.translate("description_bienvenue"),
            tagline=self.translator.translate("slogan_bienvenue"),
            status=self.translator.translate("statut_api"),
            timestamp=current_time.isoformat(),
            language=self.translator.current_language,
            
            api=APIMetadata(
                name=self.translator.translate("nom_service"),
                version=self.translator.translate("version_api"),
                build=self.translator.translate("version_construction"),
                environment=self.translator.translate("environnement"),
                uptime_status=self.translator.translate("statut_temps_fonctionnement")
            ),
            
            contact=ContactInfo(
                organization=self.translator.translate("organisation"),
                email=self.translator.translate("email_contact"),
                support_email=self.translator.translate("email_support"),
                documentation_url=self.translator.translate("url_documentation")
            ),
            
            security=SecurityInfo(
                authentication_methods=["JWT Bearer Token", "API Key (Enterprise)"],
                rate_limiting=self.translator.translate("limites_taux"),
                compliance_standards=["GDPR", "SOX", "ISO 27001", "GSMA Guidelines"],
                data_encryption="TLS 1.3, AES-256"
            ),
            
            capabilities=self._get_service_capabilities(),
            endpoints=self._get_api_endpoints(user_type),
            technical_specs=self._get_technical_specs(),
            
            quick_start={
                "documentation": self.translator.translate("url_documentation"),
                "interactive_docs": f"{request_url.rstrip('/')}/docs" if request_url else "/docs",
                "health_check": f"{request_url.rstrip('/')}/verification-etat" if request_url else "/verification-etat",
                "imei_check_example": f"{request_url.rstrip('/')}/imei/123456789012345" if request_url else "/imei/123456789012345",
                "supported_languages": f"{request_url.rstrip('/')}/languages" if request_url else "/languages"
            },
            
            legal={
                "terms_of_service": self.translator.translate("conditions_service"),
                "privacy_policy": self.translator.translate("politique_confidentialite"),
                "license": self.translator.translate("licence"),
                "data_retention": "Data retained according to regional regulations"
            }
        )
    
    def _get_service_capabilities(self) -> ServiceCapabilities:
        """Get service capabilities"""
        return ServiceCapabilities(
            imei_validation={
                "real_time_lookup": True,
                "batch_validation": True,
                "history_tracking": True,
                "status_monitoring": True,
                "supported_formats": ["15-digit IMEI", "14-digit IMEI"]
            },
            device_management={
                "device_registration": True,
                "multi_imei_support": True,
                "device_assignment": True,
                "bulk_import": True,
                "brand_analytics": True
            },
            user_management={
                "role_based_access": True,
                "multi_tenant": True,
                "audit_logging": True,
                "user_analytics": True
            },
            analytics={
                "search_analytics": True,
                "device_statistics": True,
                "usage_reports": True,
                "compliance_reports": True,
                "real_time_dashboard": True
            },
            bulk_operations={
                "bulk_device_import": True,
                "bulk_user_creation": True,
                "batch_status_updates": True,
                "scheduled_operations": True
            }
        )
    
    def _get_api_endpoints(self, user_type: str) -> APIEndpoints:
        """Get available endpoints based on user type"""
        public_endpoints = {
            "imei_lookup": "/imei/{imei}",
            "imei_search_log": "/imei/{imei}/search",
            "public_statistics": "/public/stats",
            "health_check": "/verification-etat",
            "api_info": "/",
            "supported_languages": "/languages"
        }
        
        authenticated_endpoints = {
            **public_endpoints,
            "user_devices": "/devices",
            "user_sims": "/sims",
            "search_history": "/searches",
            "user_profile": "/users/{user_id}",
            "notifications": "/notifications",
            "analytics": "/analytics/searches"
        }
        
        admin_endpoints = {
            **authenticated_endpoints,
            "user_management": "/users",
            "admin_users": "/admin/users",
            "device_management": "/admin/devices",
            "bulk_operations": "/admin/bulk-import-devices",
            "audit_logs": "/admin/audit-logs",
            "system_analytics": "/analytics/devices"
        }
        
        endpoints = APIEndpoints(
            public=public_endpoints,
            authenticated=authenticated_endpoints if user_type in ["user", "admin"] else {},
            admin=admin_endpoints if user_type == "admin" else {}
        )
        
        return endpoints
    
    def _get_technical_specs(self) -> TechnicalSpecs:
        """Get technical specifications"""
        return TechnicalSpecs(
            supported_formats=["JSON", "XML (on request)"],
            max_request_size="10MB",
            response_time_sla="< 200ms (95th percentile)",
            availability_sla="99.9% uptime",
            sdk_support=["Python", "JavaScript", "Java", "cURL examples"]
        )
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for health checks"""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime": str(uptime),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total // (1024**3)} GB",
            "disk_usage": f"{psutil.disk_usage('/').percent}%",
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else "N/A"
        }