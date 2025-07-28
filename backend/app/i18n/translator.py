from typing import Dict, Optional
import json
import os
from pathlib import Path

class Translator:
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = "en"
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        translations_dir = Path(__file__).parent / "translations"
        
        for lang_file in translations_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translations for {lang_code}: {e}")
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
        else:
            self.current_language = "en"  # fallback to English
    
    def translate(self, key: str, **kwargs) -> str:
        """Translate a key to the current language"""
        translation = self.translations.get(self.current_language, {}).get(key)
        
        # Fallback to English if translation not found
        if not translation:
            translation = self.translations.get("en", {}).get(key, key)
        
        # Replace placeholders
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except:
                pass
        
        return translation

# Global translator instance
translator = Translator()

def get_translator(language: str = "en") -> Translator:
    """Get translator instance with specified language"""
    translator.set_language(language)
    return translator

def _(key: str, **kwargs) -> str:
    """Shorthand for translation"""
    return translator.translate(key, **kwargs)