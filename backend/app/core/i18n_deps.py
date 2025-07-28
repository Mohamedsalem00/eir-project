from fastapi import Header, Request
from typing import Optional
from ..i18n import get_translator, SUPPORTED_LANGUAGES

def get_language_from_request(
    request: Request,
    accept_language: Optional[str] = Header(None),
    x_language: Optional[str] = Header(None, alias="X-Language")
) -> str:
    """
    Determine language from request in this order:
    1. X-Language header
    2. Query parameter 'lang'
    3. Accept-Language header
    4. Default to English
    """
    
    # 1. Check X-Language header
    if x_language and x_language in SUPPORTED_LANGUAGES:
        return x_language
    
    # 2. Check query parameter
    lang_param = request.query_params.get("lang")
    if lang_param and lang_param in SUPPORTED_LANGUAGES:
        return lang_param
    
    # 3. Parse Accept-Language header
    if accept_language:
        accepted_languages = []
        for lang_range in accept_language.split(','):
            lang_code = lang_range.split(';')[0].strip().split('-')[0]
            if lang_code in SUPPORTED_LANGUAGES:
                accepted_languages.append(lang_code)
        
        if accepted_languages:
            return accepted_languages[0]
    
    # 4. Default to English
    return "en"

def get_current_translator(
    request: Request,
    accept_language: Optional[str] = Header(None),
    x_language: Optional[str] = Header(None, alias="X-Language")
):
    """Dependency to get translator for current request"""
    language = get_language_from_request(request, accept_language, x_language)
    return get_translator(language)