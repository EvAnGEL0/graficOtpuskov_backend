#инсталяция

-python -m venv venv
-source venv/bin/activate  # Linux/Mac
-venv\Scripts\activate   # Windows
-pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8801

#версии 
python --version
Python 3.11.2


Авторизация для календаря отпусков 
graficOtpuskov_backend/
├── auth.py                 # Логика аутентификации
├── main.py                 # Точка входа
├── database.py             # Подключение к БД
├── models.py               # Модели (уже есть)
├── schemas.py              # Схемы Pydantic
├── crud.py                 # Логика работы с БД
└── api/
    └── rout

    pip install python-jose[cryptography] python-multipart

    

