from fastapi import FastAPI

# Создаём экземпляр приложения
app = FastAPI()

# Простой маршрут
@app.get("/")
def read_root():
    return {"message": "Привет от FastAPI!"}

# Маршрут с параметром
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}