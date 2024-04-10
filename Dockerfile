FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --break

COPY . .

RUN mkdir -p output
RUN mkdir -p uploads

EXPOSE 5000

CMD [ "uwsgi", "--http", "0.0.0.0:5000", "--module", "app:app", "--master", "--processes", "4", "--threads", "2" ]