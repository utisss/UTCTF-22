FROM python:3.8-slim-buster

WORKDIR /usr/src/app
RUN apt update && apt install -y python3-dev build-essential zlib1g

RUN pip install --upgrade pip
COPY /requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 5000

ENTRYPOINT ["python3"]

ENV FLASK_APP=/usr/src/app/app.py

CMD ["-m", "flask", "run", "--host=0.0.0.0"]
