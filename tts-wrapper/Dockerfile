FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y --no-install-recommends \
		libsndfile1-dev \
	&& rm -rf /var/lib/apt/lists/*
	
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app