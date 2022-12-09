FROM python:3.11.0-buster
WORKDIR /app

COPY /app /app/ 

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

CMD ["python", "main.py"]

# FROM python:3.9
# WORKDIR /app
# COPY requirements.txt /app
# COPY ./src /app/src
# COPY . /app
# RUN pip install -r requirements.txt
# RUN pip install uvicorn
# CMD uvicorn src.main:app --host=0.0.0.0 --port=${PORT:-5000} 