FROM alpine:3.15.0

WORKDIR /usr/src/app
RUN apk update && apk add python3 py3-cffi py3-pip

RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY app.py /usr/src/app/
COPY static/ /usr/src/app/static/
COPY templates/ /usr/src/app/templates/
RUN adduser --disabled-password --gecos "" --no-create-home worker
USER worker:nobody

EXPOSE 8000

ENTRYPOINT ["python3"]

CMD ["-m", "gunicorn", "--chdir", "/usr/src/app", "-b", "0.0.0.0:8000", "-w", "2", "--threads", "100", "app:app"]
