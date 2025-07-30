from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Any, Optional
from datetime import datetime

class APIMetadata(BaseModel):
    """API metadata information"""
    name: str = Field(..., description="API service name")
    version: str = Field(..., description="API version")
    build: str = Field(..., description="Build version")
    environment: str = Field(..., description="Deployment environment")
    uptime_status: str = Field(..., description="Service uptime status")

class ContactInfo(BaseModel):
    """Contact information"""
    organization: str = Field(..., description="Organization name")
    email: str = Field(..., description="Contact email")
    support_email: str = Field(..., description="Support email")
    documentation_url: str = Field(..., description="Documentation URL")

class SecurityInfo(BaseModel):
    """Security and compliance information"""
    authentication_methods: List[str] = Field(..., description="Supported authentication methods")
    rate_limiting: str = Field(..., description="Rate limiting policy")
    compliance_standards: List[str] = Field(..., description="Compliance standards")
    data_encryption: str = Field(..., description="Data encryption status")

class ServiceCapabilities(BaseModel):
    """Service capabilities and features"""
    imei_validation: Dict[str, Any] = Field(..., description="IMEI validation capabilities")
    device_management: Dict[str, Any] = Field(..., description="Device management features")
    user_management: Dict[str, Any] = Field(..., description="User management features")
    analytics: Dict[str, Any] = Field(..., description="Analytics capabilities")
    bulk_operations: Dict[str, Any] = Field(..., description="Bulk operation support")

class APIEndpoints(BaseModel):
    """Available API endpoints"""
    public: Dict[str, str] = Field(..., description="Public endpoints")
    authenticated: Dict[str, str] = Field(..., description="Authenticated user endpoints")
    admin: Dict[str, str] = Field(..., description="Admin-only endpoints")

class TechnicalSpecs(BaseModel):
    """Technical specifications"""
    supported_formats: List[str] = Field(..., description="Supported data formats")
    max_request_size: str = Field(..., description="Maximum request size")
    response_time_sla: str = Field(..., description="Response time SLA")
    availability_sla: str = Field(..., description="Availability SLA")
    sdk_support: List[str] = Field(..., description="Available SDKs")

class WelcomeResponse(BaseModel):
    """Professional API welcome response"""
    title: str = Field(..., description="API title")
    description: str = Field(..., description="API description")
    tagline: str = Field(..., description="API tagline")
    status: str = Field(..., description="Current API status")
    timestamp: str = Field(..., description="Response timestamp")
    language: str = Field(..., description="Response language")
    
    # Core information
    api: APIMetadata
    contact: ContactInfo
    security: SecurityInfo
    
    # Service details
    capabilities: ServiceCapabilities
    endpoints: APIEndpoints
    technical_specs: TechnicalSpecs
    
    # Quick start
    quick_start: Dict[str, str] = Field(..., description="Quick start information")
    
    # Legal
    legal: Dict[str, str] = Field(..., description="Legal information")

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    uptime: str
    database: Dict[str, str]
    system_info: Dict[str, str]
    endpoints_status: Dict[str, str]
    security_status: Dict[str, str]

class APIInfoResponse(BaseModel):
    api_name: str
    version: str
    description: str
    purpose: str
    capabilities: Dict[str, Dict[str, Any]]
    technical_specifications: Dict[str, str]
    compliance_features: Dict[str, str]
    supported_formats: Dict[str, List[str]]
    integration_ready: Dict[str, str]