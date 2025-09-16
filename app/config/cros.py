from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    """Добавляет CORS middleware к FastAPI приложению"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex="https?://.*localhost.*",
    )