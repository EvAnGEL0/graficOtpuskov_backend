from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Настройка CORS
origins = [
    "http://localhost:5173",  # React по умолчанию
    "http://localhost:5173",  # Vue.js
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
    "*"  # Для разработки - разрешает все источники (НЕ для продакшена!)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https?://.*localhost.*",  # Разрешает localhost с любым портом
)

@app.get("/")
def read_root():
    return {"Hello": "World"}