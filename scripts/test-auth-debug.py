#!/usr/bin/env python3
"""
Script de diagnostic pour l'API d'authentification
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/auth"

def test_login():
    """Test de connexion avec différents scénarios"""
    print(f"🔍 Test de diagnostic - {datetime.now()}")
    print(f"URL de base: {BASE_URL}")
    print("-" * 50)
    
    # Test 1: Vérification de l'API
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ API accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ API non accessible: {e}")
        return
    
    # Test 2: Tentative de connexion avec des données de test
    test_credentials = {
        "email": "admin@eir.com",
        "mot_de_passe": "admin123"
    }
    
    print(f"\n🧪 Test de connexion avec: {test_credentials['email']}")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/login",
            json=test_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Réponse: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion réussie!")
            print(f"Token reçu: {data.get('access_token', '')[:50]}...")
        else:
            print(f"❌ Échec de connexion")
            
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
    
    # Test 3: Test avec des identifiants incorrects
    print(f"\n🧪 Test avec identifiants incorrects")
    
    wrong_credentials = {
        "email": "wrong@email.com",
        "mot_de_passe": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{AUTH_URL}/login",
            json=wrong_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")

if __name__ == "__main__":
    test_login()
