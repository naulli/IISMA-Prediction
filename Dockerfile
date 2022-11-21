FROM python:3.9.0
WORKDIR /IISMA-Prediction
COPY requirements.txt /IISMA-Prediction/requirements.txt
RUN pip install -r requirements.txt
COPY . /IISMA-Prediction
RUN pip install uvicorn
CMD [ "uvicorn", "src.main:app" , "--host", "0.0.0.0", "--port", "8080", "--reload"]