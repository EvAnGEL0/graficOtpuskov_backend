# tests/test_api.py
from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

# Тест: корневой маршрут
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Привет от FastAPI!"}

# Тест: создание задачи
def test_create_todo():
    response = client.post(
        "/todos/",
        json={"title": "Тестовая задача", "description": "Описание", "completed": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Тестовая задача"
    assert data["completed"] is False
    assert "id" in data

    # Сохраним ID для следующих тестов
    global TODO_ID
    TODO_ID = data["id"]

# Тест: получение всех задач
def test_get_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Тест: обновление задачи
def test_update_todo():
    response = client.put(
        f"/todos/{TODO_ID}",
        json={"title": "Обновлённая задача", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Обновлённая задача"
    assert data["completed"] is True

# Тест: удаление задачи
def test_delete_todo():
    response = client.delete(f"/todos/{TODO_ID}")
    assert response.status_code == 200
    assert response.json() == {"message": "Задача удалена"}