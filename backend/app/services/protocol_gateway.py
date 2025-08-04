from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

class ProtocolType(Enum):
    REST = "rest"
    MAP = "map" 
    SOAP = "soap"
    SS7 = "ss7"

class ProtocolAdapter(ABC):
    """Interface pour adaptateurs de protocole"""
    
    @abstractmethod
    def format_request(self, data: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_format(self, data: Dict[str, Any]) -> bool:
        pass

class MAPAdapter(ProtocolAdapter):
    """Adaptateur pour protocole MAP"""
    
    def format_request(self, data: Dict[str, Any]) -> str:
        imei = data.get("imei")
        return f"""
        MAP-CHECK-IMEI-REQ {{
            imei: {imei},
            operation: "check-equipment-status",
            version: "3"
        }}
        """
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        # Parsing de la réponse MAP
        return {
            "status": "allowed",
            "imei": "123456789012345",
            "result_code": "success"
        }
    
    def validate_format(self, data: Dict[str, Any]) -> bool:
        return "imei" in data and len(data["imei"]) == 15

class SOAPAdapter(ProtocolAdapter):
    """Adaptateur pour protocole SOAP"""
    
    def format_request(self, data: Dict[str, Any]) -> str:
        imei = data.get("imei")
        return f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <checkIMEI xmlns="http://eir-project.com/soap/">
                    <imei>{imei}</imei>
                </checkIMEI>
            </soap:Body>
        </soap:Envelope>
        """
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        # Parsing XML SOAP
        return {"status": "allowed", "imei": "123456789012345"}
    
    def validate_format(self, data: Dict[str, Any]) -> bool:
        return "imei" in data

class ProtocolGateway:
    """Passerelle de gestion des protocoles"""
    
    def __init__(self):
        self.adapters = {
            ProtocolType.MAP: MAPAdapter(),
            ProtocolType.SOAP: SOAPAdapter(),
            # Autres adaptateurs...
        }
    
    def process_request(self, protocol: ProtocolType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête selon le protocole spécifié"""
        adapter = self.adapters.get(protocol)
        if not adapter:
            raise ValueError(f"Protocole {protocol} non supporté")
        
        if not adapter.validate_format(data):
            raise ValueError("Format de données invalide")
        
        # Traitement de la requête
        formatted_request = adapter.format_request(data)
        
        # Simulation du traitement
        response = self.simulate_network_response(protocol, data)
        
        return adapter.parse_response(response)
    
    def simulate_network_response(self, protocol: ProtocolType, data: Dict[str, Any]) -> str:
        """Simulation de réponse réseau"""
        if protocol == ProtocolType.MAP:
            return "MAP-CHECK-IMEI-RSP { result: success, status: allowed }"
        elif protocol == ProtocolType.SOAP:
            return "<soap:Body><checkIMEIResponse><status>allowed</status></checkIMEIResponse></soap:Body>"
        return "{}"