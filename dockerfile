FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

COPY ./app /app
WORKDIR /app
EXPOSE 8000

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install git -y
RUN apt-get -y install gcc mono-mcs build-essential
RUN pip3 install -r requirements.txt
RUN pip3 install "git+https://github.com/openai/whisper.git" 
RUN apt-get install -y espeak ffmpeg libespeak1