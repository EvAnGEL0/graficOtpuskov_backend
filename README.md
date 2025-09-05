#инсталяция

-python -m venv venv
-source venv/bin/activate  # Linux/Mac
-venv\Scripts\activate   # Windows
-pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8801

#версии 
python --version
Python 3.11.2



