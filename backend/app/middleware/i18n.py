from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from ..i18n import get_translator, SUPPORTED_LANGUAGES

class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Detect language from request
        language = self.detect_language(request)
        
        # Store language in request state
        request.state.language = language
        request.state.translator = get_translator(language)
        
        response = await call_next(request)
        
        # Add language info to response headers
        response.headers["Content-Language"] = language
        response.headers["X-Supported-Languages"] = ",".join(SUPPORTED_LANGUAGES.keys())
        
        return response
    
    def detect_language(self, request: Request) -> str:
        # Same logic as get_language_from_request
        x_language = request.headers.get("X-Language")
        if x_language and x_language in SUPPORTED_LANGUAGES:
            return x_language
        
        lang_param = request.query_params.get("lang")
        if lang_param and lang_param in SUPPORTED_LANGUAGES:
            return lang_param
        
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            for lang_range in accept_language.split(','):
                lang_code = lang_range.split(';')[0].strip().split('-')[0]
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code
        
        return "fr"