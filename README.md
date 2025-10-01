#инсталяция


- source venv/bin/activate  # Linux/Mac
- venv\Scripts\activate   # Windows
- pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8801

#версии 
python --version
Python 3.11.2


обнови версию python на linux


тестирование
python3 -m pytest tests/ -v



создание структуры проекта
mkdir -p fastapi_project/{database/models,schemas,api/v1,services,dependencies,core}
cd fastapi_project
touch main.py
touch database/__init__.py database/models/*.py schemas/*.py api/v1/*.py services/*.py dependencies/deps.py core/*.py



users (только авторизованные: admin, kadry, work)
├── id
├── username
├── role
└── employee_id → ссылка на таблицу employees

employees (все сотрудники, включая начальников)
├── id
├── first_name
├── last_name
├── middle_name
├── department_id
├── position_id
└── supervisor_id → ссылка на начальника (если есть)

departments
├── id
├── name

positions
├── id
├── name

vacations (отпуска сотрудников)
├── id
├── employee_id
├── start_date
├── end_date
├── vacation_type_id
└── approval_status_id