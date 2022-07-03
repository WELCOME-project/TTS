FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

#RUN apt-get update

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY taln-tts-36120d1f2d87.json taln-tts-36120d1f2d87.json
COPY ./app /app
