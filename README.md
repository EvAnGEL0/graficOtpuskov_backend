#инсталяция

-python -m venv venv
-source venv/bin/activate  # Linux/Mac
-venv\Scripts\activate   # Windows
-pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8801

#версии 
python --version
Python 3.11.2



тестирование
python3 -m pytest tests/ -v



создание структуры проекта
mkdir -p fastapi_project/{database/models,schemas,api/v1,services,dependencies,core}
cd fastapi_project
touch main.py
touch database/__init__.py database/models/*.py schemas/*.py api/v1/*.py services/*.py dependencies/deps.py core/*.py