FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /app

COPY ./app .
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# FROM python:3.9
# WORKDIR /app
# COPY requirements.txt /app
# COPY ./src /app/src
# COPY . /app
# RUN pip install -r requirements.txt
# RUN pip install uvicorn
# CMD uvicorn src.main:app --host=0.0.0.0 --port=${PORT:-5000} 